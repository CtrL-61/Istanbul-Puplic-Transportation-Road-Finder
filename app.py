# Metro Pulse - İstanbul Metro Rota Planlayıcı
# Bu proje eğitim amaçlıdır. Veriler simülasyon amaçlı rastgele üretilmektedir.
# Durak bilgileri Metro İstanbul kamuya açık kaynaklarından derlenmiştir.

import networkx as nx
import os
import random
from flask import Flask, render_template, request

#1. AYARLAR
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app = app # Vercel için

#2. DURAK EŞLEŞTİRME (STATION MAPPING)
# İBB API'sinden gelen isimleri senin grafındaki isimlere tercüme eder.
STATION_MAPPING = {
    "YENIKAPI STATION": "Yenikapı",
    "MECIDIYEKOY STATION": "Şişli-Mecidiyeköy",
    "HALIC STATION": "Haliç",
    "TAKISM STATION": "Taksim",
    "USKUDAR STATION": "Üsküdar",
    "KADIKOY STATION": "Kadıköy",
    "SABIHA GOKCEN AIRPORT": "Sabiha Gökçen Havalimanı",
    # Yeni duraklar eklendikçe burayı güncelleyebilirsin.
}

#3. YARDIMCI FONKSİYONLAR
def get_announcement(lang):
    if lang == 'tr':
        return "Sistem normal: Tüm hatlar seferlerine devam etmektedir."
    return "System normal: All lines are operating on schedule."

def get_live_info(durak_adi):
    """
    API verisini senin durak isimlerine göre filtreleyen fonksiyon.
    STATION_MAPPING kullanarak API karşılığını bulur.
    """
    # Senin durak isminin API karşılığını bul (Ters mapping)
    api_karsiligi = next((k for k, v in STATION_MAPPING.items() if v == durak_adi), durak_adi)
    
    # Canlı veri simülasyonu
    return {
        'dakika': random.randint(2, 12),
        'doluluk': random.choice(['Düşük', 'Orta', 'Yüksek']),
        'api_name': api_karsiligi # Hangi isimle sorgulandığını takip etmek için
    }

# DİL SÖZLÜĞÜ
LANGUAGES = {
    'tr': {
        'title': 'Metro Pulse',
        'subtitle': 'İstanbul Rota Planlama',
        'departure': 'KALKIŞ DURAĞI',
        'destination': 'VARIŞ DURAĞI',
        'button': 'ROTA BUL',
        'error_path': 'Üzgünüz, bu iki durak arasında bir metro bağlantısı bulunamadı.',
        'error_same': 'Aynı durağı seçtiniz!'
    },
    'en': {
        'title': 'Metro Pulse',
        'subtitle': 'Istanbul Route Planner',
        'departure': 'DEPARTURE STATION',
        'destination': 'DESTINATION STATION',
        'button': 'FIND ROUTE',
        'error_path': 'Sorry, no metro connection found between these stations.',
        'error_same': 'You selected the same station!'
    }
}

#4. GRAF VE VERİ İŞLEME
G = nx.Graph()
def hat_ekle(hat_kodu, durak_metni, toplam_sure):
    duraklar = [d.strip() for d in durak_metni.split(',')]
    sure = toplam_sure / (len(duraklar) - 1)
    for i in range(len(duraklar) - 1):
        G.add_edge(duraklar[i], duraklar[i+1], weight=sure, hat=hat_kodu)

# HAT VERİLERİ
hat_ekle("M1A", "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa, Sağmalcılar, Kocatepe, Otogar, Terazidere, Davutpaşa, Merter, Zeytinburnu, Bakırköy-İncirli, Bahçelievler, Ataköy-Şirinevler, Yenibosna, DTM-İstanbul Fuar Merkezi, Atatürk Havalimanı", 35)
hat_ekle("M2", "Yenikapı, Vezneciler, Haliç, Şişhane, Taksim, Osmanbey, Şişli-Mecidiyeköy, Gayrettepe, Levent, 4. Levent, Sanayi Mahallesi, İTÜ-Ayazağa, Atatürk Oto Sanayi, Darüşşafaka, Hacıosman", 32)
hat_ekle("Marmaray", "Halkalı, Florya, Bakırköy, Kazlıçeşme, Yenikapı, Sirkeci, Üsküdar, Ayrılık Çeşmesi, Söğütlüçeşme, Bostancı, Kartal, Pendik, Gebze", 108)
hat_ekle("M4", "Kadıköy, Ayrılık Çeşmesi, Acıbadem, Ünalan, Göztepe, Yenisahra, Kozyatağı, Bostancı, Küçükyalı, Maltepe, Huzurevi, Gülsuyu, Esenkent, Hospital-Adliye, Soğanlık, Kartal, Yakacık-Adnan Kahveci, Pendik, Tavşantepe, Fevzi Çakmak-Hastane, Yayalar-Şeyhli, Kurtköy, Sabiha Gökçen Havalimanı", 50)

#5. ROUTE'LAR
@app.route('/')
def index():
    lang = request.args.get('lang', 'tr')
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    durak_listesi = sorted(list(G.nodes()))
    announcement = get_announcement(lang)
    
    return render_template('index.html', 
                           duraklar=durak_listesi, 
                           texts=texts, 
                           current_lang=lang,
                           announcement=announcement)

@app.route('/arama', methods=['POST'])
def arama():
    lang = request.form.get('lang', 'tr')
    texts = LANGUAGES.get(lang, LANGUAGES['tr'])
    
    try:
        # --- VERİ TEMİZLEME VE STANDARTLAŞTIRMA ---
        # Formdan gelen verileri alıyoruz ve başındaki/sonundaki boşlukları siliyoruz
        bas = request.form.get('baslangic', '').strip()
        hed = request.form.get('hedef', '').strip()
        # Terminale bilgi yazdır (Hata ayıklama için çok faydalı)
        print(f"Arama yapılıyor: {bas} -> {hed}")
        
        # 1. Boş veri kontrolü
        if not bas or not hed:
             return render_template('index.html', duraklar=sorted(list(G.nodes())), texts=texts, current_lang=lang)

        # 2. Durakların grafta olup olmadığını kontrol et
        if bas not in G or hed not in G:
            missing = []
            if bas not in G: missing.append(f"'{bas}'")
            if hed not in G: missing.append(f"'{hed}'")
            print(f"Hata: Durak bulunamadı -> {missing}")
            return render_template('hata.html', message=texts['error_path'], texts=texts, current_lang=lang)

        # 3. Aynı durak seçilme kontrolü
        if bas == hed:
            return render_template('hata.html', message=texts['error_same'], texts=texts, current_lang=lang)

# ROTA HESAPLAMA
        yol = nx.shortest_path(G, source=bas, target=hed, weight='weight')
        sure = nx.shortest_path_length(G, source=bas, target=hed, weight='weight')
        
        rota_detay = []
        onceki_hat = None
        
        for i in range(len(yol)):
            durak = yol[i]
            su_anki_hat = ""
            if i < len(yol) - 1:
                su_anki_hat = G[yol[i]][yol[i+1]]['hat']
                
            # Aktarma Kontrolü: Hat değişirse +5 dk ekle
            if onceki_hat and su_anki_hat and onceki_hat != su_anki_hat:
                sure += 5
                # Aktarma bilgisini ekle
                rota_detay.append({'durak': durak, 'hat': 'Aktarma'})
            
            rota_detay.append({'durak': durak, 'hat': su_anki_hat})
            onceki_hat = su_anki_hat

        res = {
            'toplam_sure': round(sure),
            'rota': rota_detay
        }
        
        # Canlı veri ve duyuru simülasyonu
        live_info = get_live_info(bas)
        announcement = get_announcement(lang)

        return render_template('sonuc.html', 
                               rota_sonucu=res, 
                               baslangic=bas, 
                               hedef=hed, 
                               texts=texts, 
                               current_lang=lang,
                               live_info=live_info,
                               announcement=announcement)
                                
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return render_template('hata.html', texts=texts, current_lang=lang)

if __name__ == "__main__":
    app.run(debug=True)