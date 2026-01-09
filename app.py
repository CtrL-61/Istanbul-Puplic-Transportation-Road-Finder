import networkx as nx
import os
from flask import Flask, render_template, request

# --- 1. AYARLAR VE KLASÖR TANIMLAMA ---
# Pydroid ve Render klasör farkını çözer
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# --- 2. GRAF OLUŞTURMA (EN ÖNEMLİ KISIM) ---
# Bu tanımlar fonksiyonların DIŞINDA olmalı ki Render başlarken yüklesin
G = nx.DiGraph()
AKTARMA_SURESI = 3

# --- 3. YARDIMCI FONKSİYONLAR ---
def hat_ekle_ve_bagla(graf, hat_kodu, durak_listesi_metin, toplam_sure):
    durak_listesi = [d.strip() for d in durak_listesi_metin.split(',')]
    durak_arasi_sayisi = len(durak_listesi) - 1
    if durak_arasi_sayisi <= 0: return
    tahmini_durak_arasi_suresi = toplam_sure / durak_arasi_sayisi

    for durak in durak_listesi:
        graf.add_node(durak, tip="Metro", hat=hat_kodu)
        
    for i in range(durak_arasi_sayisi):
        baslangic = durak_listesi[i]
        hedef = durak_listesi[i+1]
        graf.add_edge(baslangic, hedef, agirlik=tahmini_durak_arasi_suresi, tip='Yolculuk', hat=hat_kodu)
        graf.add_edge(hedef, baslangic, agirlik=tahmini_durak_arasi_suresi, tip='Yolculuk', hat=hat_kodu)

def aktarma_ekle(graf, durak1, durak2, aktarma_suresi, aciklama="Aktarma"):
    if durak1 in graf and durak2 in graf:
        graf.add_edge(durak1, durak2, agirlik=aktarma_suresi, tip=aciklama, hat='Aktarma')
        graf.add_edge(durak2, durak1, agirlik=aktarma_suresi, tip=aciklama, hat='Aktarma')

def rota_hesapla(baslangic, hedef):
    try:
        yol = nx.dijkstra_path(G, baslangic, hedef, weight='agirlik')
        sure = nx.dijkstra_path_length(G, baslangic, hedef, weight='agirlik')
        rota_detaylari = []
        for i, durak in enumerate(yol):
            onceki = yol[i-1] if i > 0 else None
            hat = ""
            if onceki:
                d = G[onceki][durak]
                hat = d.get('hat', 'Aktarma') if d.get('tip') != 'Aktarma' else "Aktarma"
            rota_detaylari.append({"durak": durak, "hat": hat})
        return {"basarili": True, "toplam_sure": int(sure), "rota": rota_detaylari}
    except:
        return {"basarili": False, "hata": "Rota bulunamadı."}

# --- 4. METRO VERİLERİ (HATLAR BURAYA EKLENİYOR) ---
hat_ekle_ve_bagla(G, "M1A", "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa-Maltepe, Sağmalcılar, Kocatepe, Otogar, Terazidere, Davutpaşa-YTÜ, Merter, Zeytinburnu, Bakırköy-İncirli, Bahçelievler, Ataköy-Şirinevler, Yenibosna, DTM-İstanbul Fuar Merkezi, Atatürk Havalimanı", 35)
hat_ekle_ve_bagla(G, "M1B", "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa-Maltepe, Sağmalcılar, Kocatepe, Otogar, Esenler, Menderes, Üçyüzlü, Bağcılar Meydan, Kirazlı-Bagcılar", 25)
hat_ekle_ve_bagla(G, "M2", "Yenikapı, Vezneciler-İstanbul Ü., Haliç, Şişhane, Taksim, Osmanbey, Şişli-Mecidiyeköy, Gayrettepe, Levent, 4.Levent, Sanayi Mahallesi, İTÜ-Ayazağa, Atatürk Oto Sanayi, Darüşşafaka, Hacıosman", 32)
hat_ekle_ve_bagla(G, "M2_Mekik", "Sanayi Mahallesi, Seyrantepe", 10)
hat_ekle_ve_bagla(G, "M3", "Bakırköy Sahil, Özgürlük Meydanı, İncirli, Haznedar, İlkyuva, Yıldıztepe, Molla Gürani, Kirazlı-Bagcılar, Yenimahalle, Mahmutbey, İSTOÇ, İkitelli Sanayi, Turgut Özal, Siteler, Başak Konutları, Başakşehir-Metrokent, Onurkent, Şehir Hastanesi, Toplu Konutlar, Kayaşehir Merkez", 44)
hat_ekle_ve_bagla(G, "M4", "Kadıköy, Ayrılık Çeşmesi, Acıbadem, Ünalan, Göztepe, Yenisahra, Pegasus-Kozyatağı, Bostancı, Küçükyalı, Maltepe, Huzurevi, Gülsuyu, Esenkent, Hastane-Adliye, Soğanlık, Kartal, Yakacık-Adnan Kahveci, Pendik, Tavşantepe, Fevzi Çakmak-Hastane, Yayalar-Şeyhli, Kurtköy, Sabiha Gökçen Havalimanı", 52)
hat_ekle_ve_bagla(G, "M5", "Üsküdar, Fıstıkağacı, Bağlarbaşı, Altunizade, Kısıklı, Bulgurlu, Ümraniye, Çarşı, Yamanevler, Çakmak, Ihlamurkuyu, Altınşehir, İmam Hatip Lisesi, Dudullu, Necip Fazıl, Çekmeköy, Meclis, Sarıgazi, Sancaktepe, Samandıra Merkez", 43)
hat_ekle_ve_bagla(G, "M6", "Levent, Nispetiye, Etiler, Boğaziçi Ü.-Hisarüstü", 7)
hat_ekle_ve_bagla(G, "M7", "Yıldız, Fulya, Mecidiyeköy, Çağlayan, Kağıthane, Nurtepe, Alibeyköy, Çırçır Mahallesi, Veysel Karani-Akşemsettin, Yeşilpınar, Kazım Karabekir, Yenimahalle, Karadeniz Mahallesi, Tekstilkent-Giyimkent, Oruç Reis, Göztepe Mahallesi, Mahmutbey", 36)
hat_ekle_ve_bagla(G, "M8", "Bostancı, Emin Ali Paşa, Ayşekadın, Kozyatağı, Küçükbakkalköy, İçerenköy, Kayışdağı, Mevlana, İMES, MODOKO-KEYAP, Dudullu, Huzur, Parseller", 25)
hat_ekle_ve_bagla(G, "M9", "Ataköy, Yenibosna, Çobançeşme, 29 Ekim Cumhuriyet, Doğu Sanayi, Mimar Sinan, 15 Temmuz, Halkalı Caddesi, Atatürk Mahallesi, Bahariye, MASKO, İkitelli Sanayi, Ziya Gökalp Mahallesi, Olimpiyat", 26)
hat_ekle_ve_bagla(G, "T1", "Kabataş, Fındıklı-Mimar Sinan Ü., Tophane, Karaköy, Eminönü, Sirkeci, Gülhane, Sultanahmet, Çemberlitaş, Beyazıt-Kapalıçarşı, Laleli-İstanbul Ü., Aksaray, Yusufpaşa, Haseki, Fındıkzade, Çapa-Şehremini, Pazartekke, Topkapı, Cevizlibağ-AÖY, Merkezefendi, Seyitnizam-Akşemsettin, Mithatpaşa, Zeytinburnu, Mehmet Akif, Merter Tekstil Merkezi, Güngören, Akıncılar, Soğanlı, Yavuzselim, Güneştepe, Bağcılar", 65)
hat_ekle_ve_bagla(G, "T4", "Topkapı, Fetihkapı, Vatan, Edirnekapı, Şehitlik, Demirkapı, Topçular, Rami, Uluyol Bereç, Sağmalcılar, Bosna Çukurçeşme, Ali Fuat Başgil, Taşköprü, Karadeniz, Kiptaş-Venezia, Cumhuriyet Mahallesi, 50.Yıl-Baştabya, Hacı Şükrü, Yenimahalle, Sultançiftliği, Cebeci, Mescid-i Selam", 45)
hat_ekle_ve_bagla(G, "T5", "Eminönü, Küçükpazar, Cibali, Fener, Balat, Ayvansaray, Feshane, Eyüpsultan Teleferik, Eyüpsultan Devlet Hastanesi, Silahtarağa Mahallesi, Üniversite, Alibeyköy Merkez, Alibeyköy Metro, Alibeyköy Cep Otogarı", 32)
hat_ekle_ve_bagla(G, "F1", "Taksim, Kabataş", 2.5)
hat_ekle_ve_bagla(G, "Marmaray", "Halkalı, Mustafa Kemal, Küçükçekmece, Florya, Florya Akvaryum, Yeşilköy, Yeşilyurt, Ataköy, Bakırköy, Yenimahalle, Zeytinburnu, Kazlıçeşme, Yenikapı, Sirkeci, Üsküdar, Ayrılık Çeşmesi, Söğütlüçeşme, Feneryolu, Göztepe, Erenköy, Suadiye, Bostancı, Küçükyalı, İdealtepe, Süreyya Plajı, Maltepe, Cevizli, Atalar, Başak, Kartal, Yunus, Pendik, Kaynarca, Tersane, Güzelyalı, Aydıntepe, İçmeler, Gebze", 115)
hat_ekle_ve_bagla(G, "Metrobüs", "Söğütlüçeşme, Fikirtepe, Uzunçayır, Acıbadem, Altunizade, Burhaniye, 15 Temmuz Şehitler Köprüsü, Mecidiyeköy, Çağlayan, Okmeydanı Hastane, Darülaceze-Perpa, Okmeydanı, Halıcıoğlu, Ayvansaray-Eyüp Sultan, Edirnekapı, Bayrampaşa-Maltepe, Topkapı-Şehit Mustafa Cambaz, Cevizlibağ, Merter, Zeytinburnu, İncirli, Bahçelievler, Şirinevler, Yenibosna, Sefaköy, Beşyol, Florya, Cennet Mahallesi, Küçükçekmece, İBB Sosyal Tesisleri, Mustafa Kemal Paşa, Cihangir-Üniversite Mahallesi, Avcılar Merkez, Şükrübey, Gümüşpala, Zafer, Haramidere, Haramidere Sanayi, Saadetdere Mahallesi, Mustafa Kemal Paşa, Beylikdüzü Belediye, Cumhuriyet Mahallesi, Beylikdüzü Son Durak", 90)

# --- 5. AKTARMALAR ---
aktarmalar = {
    'Yenibosna': ['Metrobüs_Yenibosna'], 'Ataköy': ['Marmaray_Ataköy'], 
    'Şişli-Mecidiyeköy': ['Metrobüs_Mecidiyeköy'], 'Gayrettepe': ['Metrobüs_Gayrettepe'],
    'İncirli': ['Metrobüs_İncirli'], 'Özgürlük Meydanı': ['Marmaray_Bakırköy'], 
    'Ayrılık Çeşmesi': ['Marmaray_Ayrılık Çeşmesi'], 'Ünalan': ['Metrobüs_Uzunçayır'],
    'Üsküdar': ['Marmaray_Üsküdar'], 'Altunizade': ['Metrobüs_Altunizade'],
    'Bostancı': ['Marmaray_Bostancı'], 'Sirkeci': ['Marmaray_Sirkeci'],
    'Yenikapı': ['Marmaray_Yenikapı'], 'Zeytinburnu': ['Marmaray_Zeytinburnu', 'Metrobüs_Zeytinburnu']
}

for bas, hedefler in aktarmalar.items():
    for hed in hedefler:
        target_name = hed.split('_')[1] if '_' in hed else hed
        if hed not in G and target_name in G:
             aktarma_ekle(G, bas, target_name, AKTARMA_SURESI)
        elif bas in G and hed in G:
             aktarma_ekle(G, bas, hed, AKTARMA_SURESI)

# --- 6. RENDER VE HTML İÇİN ROUTE (İŞTE BURASI EKSİKTİ!) ---
@app.route('/')
def index():
    # Render'ın "Select Station" kısmını doldurması için bu liste ŞART
    durak_listesi = sorted(list(G.nodes()))
    
    # Loglara yazdırıyoruz (Render Loglarında görebilirsin)
    print(f"DEBUG: Render toplam {len(durak_listesi)} durak yükledi.")
    
    # HTML'deki 'duraklar' değişkenine bu listeyi gönderiyoruz
    return render_template('index.html', duraklar=durak_listesi)

@app.route('/arama', methods=['POST'])
def arama():
    bas = request.form.get('baslangic')
    hed = request.form.get('hedef')
    res = rota_hesapla(bas, hed)
    if res["basarili"]:
        return render_template('sonuc.html', baslangic=bas, hedef=hed, rota_sonucu=res)
    return render_template('hata.html', mesaj=res["hata"])

# --- 7. ÇALIŞTIRMA ---
if __name__ == '__main__':
    # Pydroid
    app.run(debug=True, host='0.0.0.0', port=5001)
else:
    # Render
    port = int(os.environ.get("PORT", 5000))
