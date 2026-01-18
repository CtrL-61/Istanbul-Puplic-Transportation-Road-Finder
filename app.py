import networkx as nx
import os
from flask import Flask, render_template, request

# --- 1. KRİTİK AYAR: KLASÖR YOLLARINI SABİTLEME ---
# Bu blok, Vercel/Render'ın dosyaları bulamama hatasını %100 çözer.
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Vercel'in uygulamayı tanıması için gerekli sihirli dokunuş
app = app 

# DİL SÖZLÜĞÜ (Bu app.py'nin en üstünde, route'lardan önce olmalı)
LANGUAGES = {
    'tr': {
        'title': 'Metro Pulse',
        'subtitle': 'İstanbul Rota Planlama',
        'departure': 'KALKIŞ DURAĞI',
        'destination': 'VARIŞ DURAĞI',
        'placeholder': 'Durak adı...',
        'button': 'ROTA BUL',
        'theme_btn': 'Mod'
    },
    'en': {
        'title': 'Metro Pulse',
        'subtitle': 'Istanbul Route Planner',
        'departure': 'DEPARTURE STATION',
        'destination': 'DESTINATION STATION',
        'placeholder': 'Station name...',
        'button': 'FIND ROUTE',
        'theme_btn': 'Mode'
    }
}
# --- 3. GRAF VERİLERİ
G = nx.DiGraph()
AKTARMA_SURESI = 3

def hat_ekle_ve_bagla(graf, hat_kodu, durak_listesi_metin, toplam_sure):
    durak_listesi = [d.strip() for d in durak_listesi_metin.split(',')]
    durak_arasi_sayisi = len(durak_listesi) - 1
    if durak_arasi_sayisi <= 0: return
    tahmini_durak_arasi_suresi = toplam_sure / durak_arasi_sayisi

    for durak in durak_listesi:
        # Hata önlemi: Eğer durak zaten varsa özelliğini güncelle
        if durak not in graf:
            graf.add_node(durak, tip="Metro")
        
    for i in range(durak_arasi_sayisi):
        baslangic = durak_listesi[i]
        hedef = durak_listesi[i+1]
        graf.add_edge(baslangic, hedef, weight=tahmini_durak_arasi_suresi, hat=hat_kodu)
        graf.add_edge(hedef, baslangic, weight=tahmini_durak_arasi_suresi, hat=hat_kodu)

def aktarma_ekle(graf, durak1, durak2, sure):
    if durak1 in graf and durak2 in graf:
        graf.add_edge(durak1, durak2, weight=sure, hat="Aktarma")
        graf.add_edge(durak2, durak1, weight=sure, hat="Aktarma")

# --- HAT VERİLERİ (Aynen Kalıyor)
hat_ekle_ve_bagla(G, "M1A", "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa, Sağmalcılar, Kocatepe, Otogar, Terazidere, Davutpaşa, Merter, Zeytinburnu, Bakırköy-İncirli, Bahçelievler, Ataköy-Şirinevler, Yenibosna, DTM-İstanbul Fuar Merkezi, Atatürk Havalimanı", 35)
hat_ekle_ve_bagla(G, "M2", "Yenikapı, Vezneciler, Haliç, Şişhane, Taksim, Osmanbey, Şişli-Mecidiyeköy, Gayrettepe, Levent, 4. Levent, Sanayi Mahallesi, İTÜ-Ayazağa, Atatürk Oto Sanayi, Darüşşafaka, Hacıosman", 32)
hat_ekle_ve_bagla(G, "Marmaray", "Gebze, Darıca, Osmangazi, Fatih, Çayırova, Tuzla, İçmeler, Aydıntepe, Güzelyalı, Tersane, Kaynarca, Pendik, Yunus, Kartal, Başak, Atalar, Cevizli, İdealtepe, Küçükyalı, Bostancı, Suadiye, Erenköy, Göztepe, Feneryolu, Söğütlüçeşme, Ayrılık Çeşmesi, Üsküdar, Sirkeci, Yenikapı, Kazlıçeşme, Zeytinburnu, Yenimahalle, Bakırköy, Ataköy, Yeşilyurt, Yeşilköy, Florya Akvaryum, Florya, Küçükçekmece, Mustafa Kemal, Halkalı", 108)

# Aktarmalar
aktarma_ekle(G, "Yenikapı", "Yenikapı", 0) 

# --- 4. ROTALAR (Endpointler)
@app.route('/')
def index():
    # URL'den dili al (?lang=tr gibi), yoksa 'tr' varsay
    lang = request.args.get('lang', 'tr')
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    
    durak_listesi = sorted(list(G.nodes()))
    
    return render_template('index.html', 
                           duraklar=durak_listesi, 
                           texts=texts, 
                           current_lang=lang)


@app.route('/arama', methods=['POST'])
def arama():
    # Fonksiyonun başında dili yakalıyoruz ki hata olursa hata sayfası da bu dilde gelsin
    lang = request.form.get('lang', request.args.get('lang', 'tr'))
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    
    try:
        bas = request.form.get('baslangic')
        hed = request.form.get('hedef')
        
        # Boş input kontrolü
        if not bas or not hed:
             return render_template('index.html', duraklar=sorted(list(G.nodes())), texts=texts, current_lang=lang)

        # Rota Hesaplama (Aynı kalıyor)
        yol = nx.shortest_path(G, source=bas, target=hed, weight='weight')
        sure = nx.shortest_path_length(G, source=bas, target=hed, weight='weight')
        
        rota_detay = []
        for i in range(len(yol)):
            durak_adi = yol[i]
            hat_bilgisi = ""
            if i < len(yol) - 1:
                hat_bilgisi = G[yol[i]][yol[i+1]].get('hat', '')
            rota_detay.append({'durak': durak_adi, 'hat': hat_bilgisi})

        res = {
            'toplam_sure': round(sure),
            'rota': rota_detay
        }
        
        # Sonuç sayfasını render et (Dil ve metinleri gönderiyoruz)
        return render_template('sonuc.html', 
                               rota_sonucu=res, 
                               baslangic=bas, 
                               hedef=hed, 
                               texts=texts, 
                               current_lang=lang)
    
    except Exception as e:
        print(f"Hata oluştu: {e}")
        # Hata sayfasını da seçili dilde gösteriyoruz
        return render_template('hata.html', texts=texts, current_lang=lang)


if __name__ == "__main__":
    app.run(debug=False)
