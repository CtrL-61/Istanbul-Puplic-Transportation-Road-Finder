# app.py

import networkx as nx
import os
from flask import Flask, render_template, request, jsonify
 # Flask kütüphanelerini içe aktar

# Flask'a şablon klasörünün yolunu manuel olarak belirtiyoruz.
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))


# (MEVCUT KODUNUZUN BÖLÜM 1 VE BÖLÜM 2'SİNİ BURAYA YAPIŞTIRIN)
# 1. YARDIMCI FONKSİYONLAR

def hat_ekle_ve_bagla(graf, hat_kodu, durak_listesi_metin, toplam_sure):
    """
    Belirtilen hat verilerini NetworkX grafına (G) ekler.
    Ardışık duraklar arasına iki yönlü kenar ekler (Ağırlık: Tahmini Süre).
    """
    durak_listesi = [d.strip() for d in durak_listesi_metin.split(',')]
    durak_arasi_sayisi = len(durak_listesi) - 1
    
    if durak_arasi_sayisi <= 0:
        print(f"UYARI: {hat_kodu} için yeterli durak yok.")
        return
        
    tahmini_durak_arasi_suresi = toplam_sure / durak_arasi_sayisi

    for durak in durak_listesi:
        # Not: Ortak duraklar (Yenikapı, Aksaray vb.) sadece bir kez eklenir.
        graf.add_node(durak, tip="Metro", hat=hat_kodu)
        
    for i in range(durak_arasi_sayisi):
        baslangic = durak_listesi[i]
        hedef = durak_listesi[i+1]
        graf.add_edge(baslangic, hedef, agirlik=tahmini_durak_arasi_suresi, tip='Yolculuk', hat=hat_kodu)
        graf.add_edge(hedef, baslangic, agirlik=tahmini_durak_arasi_suresi, tip='Yolculuk', hat=hat_kodu)
        
    print(f"-> {hat_kodu} hattı eklendi. Durak Arası Süre: {tahmini_durak_arasi_suresi:.2f} dakika.")


def aktarma_ekle(graf, durak1, durak2, aktarma_suresi, aciklama="Aktarma"):
    """İki düğüm arasına iki yönlü aktarma kenarı ekler."""
    # Sadece iki durak da grafikte varsa (yani hatlar eklendiyse) aktarma ekle.
    if durak1 in graf and durak2 in graf:
        graf.add_edge(durak1, durak2, agirlik=aktarma_suresi, tip=aciklama)
        graf.add_edge(durak2, durak1, agirlik=aktarma_suresi, tip=aciklama)
        return True
    return False

# 2. GRAF TANIMI VE SABİTLER

G = nx.DiGraph() 
AKTARMA_SURESI = 3 # Sabit Aktarma Süresi (Dakika)


# 1. YARDIMCI FONKSİYONLAR
# 2. GRAF TANIMI VE SABİTLER (G = nx.DiGraph() ve AKTARMA_SURESI)
# ------------------------------------------------------------------

# Grafiği sadece bir kere yükle
G = nx.DiGraph() 
AKTARMA_SURESI = 3 # Sabit Aktarma Süresi (Dakika)

# ------------------------------------------------------------------
# (MEVCUT KODUNUZUN BÖLÜM 3 VE BÖLÜM 4'ÜNÜ BURAYA YAPIŞTIRIN)

# 3. VERİ GİRİŞİ - M HATLARI

print("--- Hatlar Grafiğe Ekleniyor ---")

# M1A Hattı
m1a_duraklar = "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa-Maltepe, Sağmalcılar, Kocatepe, Otogar, Terazidere, Davutpaşa-YTÜ, Merter, Zeytinburnu, Bakırköy-İncirli, Bahçelievler, Ataköy-Şirinevler, Yenibosna, DTM-İstanbul Fuar Merkezi, Atatürk Havalimanı"
hat_ekle_ve_bagla(G, "M1A", m1a_duraklar, 35)

# M1B Hattı
m1b_duraklar = "Yenikapı, Aksaray, Emniyet-Fatih, Topkapı-Ulubatlı, Bayrampaşa-Maltepe, Sağmalcılar, Kocatepe, Otogar, Esenler, Menderes, Üçyüzlü, Bağcılar Meydan, Kirazlı-Bağcılar"
hat_ekle_ve_bagla(G, "M1B", m1b_duraklar, 25)

# M2 Hattı (Ana)
m2_ana_duraklar = "Yenikapı, Vezneciler-İstanbul Ü., Haliç, Şişhane, Taksim, Osmanbey, Şişli-Mecidiyeköy, Gayrettepe, Levent, 4.Levent, Sanayi Mahallesi, İTÜ-Ayazağa, Atatürk Oto Sanayi, Darüşşafaka, Hacıosman"
hat_ekle_ve_bagla(G, "M2", m2_ana_duraklar, 32)

# M2 Mekik Hattı (Seyrantepe)
m2_mekik_duraklar = "Sanayi Mahallesi, Seyrantepe"
hat_ekle_ve_bagla(G, "M2_Mekik", m2_mekik_duraklar, 10) # Varsayımsal 10dk süre

# M3 Hattı Durakları
m3_duraklar = "Bakırköy Sahil, Özgürlük Meydanı, İncirli, Haznedar, İlkyuva, Yıldıztepe, Molla Gürani, Kirazlı-Bağcılar, Yenimahalle, Mahmutbey, İSTOÇ, İkitelli Sanayi, Turgut Özal, Siteler, Başak Konutları, Başakşehir-Metrokent, Onurkent, Şehir Hastanesi, Toplu Konutlar, Kayaşehir Merkez"
m3_sure = 44
hat_ekle_ve_bagla(G, "M3", m3_duraklar, m3_sure)

# M4 Hattı Durakları
m4_duraklar = "Kadıköy, Ayrılık Çeşmesi, Acıbadem, Ünalan, Göztepe, Yenisahra, Pegasus-Kozyatağı, Bostancı, Küçükyalı, Maltepe, Huzurevi, Gülsuyu, Esenkent, Hastane-Adliye, Soğanlık, Kartal, Yakacık-Adnan Kahveci, Pendik, Tavşantepe, Fevzi Çakmak-Hastane, Yayalar-Şeyhli, Kurtköy, Sabiha Gökçen Havalimanı"
m4_sure = 52
hat_ekle_ve_bagla(G, "M4", m4_duraklar, m4_sure)

# M5 Hattı Durakları
m5_duraklar = "Üsküdar, Fıstıkağacı, Bağlarbaşı, Altunizade, Kısıklı, Bulgurlu, Ümraniye, Çarşı, Yamanevler, Çakmak, Ihlamurkuyu, Altınşehir, İmam Hatip Lisesi, Dudullu, Necip Fazıl, Çekmeköy, Meclis, Sarıgazi, Sancaktepe, Samandıra Merkez"
hat_ekle_ve_bagla(G, "M5", m5_duraklar, 43)

# M6 Hattı Durakları
m6_duraklar = "Levent, Nispetiye, Etiler, Boğaziçi Ü.-Hisarüstü"
hat_ekle_ve_bagla(G, "M6", m6_duraklar, 7)

# M7 Hattı Durakları
m7_duraklar = "Yıldız, Fulya, Mecidiyeköy, Çağlayan, Kağıthane, Nurtepe, Alibeyköy, Çırçır Mahallesi, Veysel Karani-Akşemsettin, Yeşilpınar, Kazım Karabekir, Yenimahalle, Karadeniz Mahallesi, Tekstilkent-Giyimkent, Oruç Reis, Göztepe Mahallesi, Mahmutbey"
hat_ekle_ve_bagla(G, "M7", m7_duraklar, 36)

# M8 Hattı Durakları
m8_duraklar = "Bostancı, Emin Ali Paşa, Ayşekadın, Kozyatağı, Küçükbakkalköy, İçerenköy, Kayışdağı, Mevlana, İMES, MODOKO-KEYAP, Dudullu, Huzur, Parseller"
hat_ekle_ve_bagla(G, "M8", m8_duraklar, 25)

# M9 Hattı Durakları
m9_duraklar = "Ataköy, Yenibosna, Çobançeşme, 29 Ekim Cumhuriyet, Doğu Sanayi, Mimar Sinan, 15 Temmuz, Halkalı Caddesi, Atatürk Mahallesi, Bahariye, MASKO, İkitelli Sanayi, Ziya Gökalp Mahallesi, Olimpiyat"
hat_ekle_ve_bagla(G, "M9", m9_duraklar, 26)

# T1 Hattı Durakları
t1_duraklar = "Kabataş, Fındıklı-Mimar Sinan Ü., Tophane, Karaköy, Eminönü, Sirkeci, Gülhane, Sultanahmet, Çemberlitaş, Beyazıt-Kapalıçarşı, Laleli-İstanbul Ü., Aksaray, Yusufpaşa, Haseki, Fındıkzade, Çapa-Şehremini, Pazartekke, Topkapı, Cevizlibağ-AÖY, Merkezefendi, Seyitnizam-Akşemsettin, Mithatpaşa, Zeytinburnu, Mehmet Akif, Merter Tekstil Merkezi, Güngören, Akıncılar, Soğanlı, Yavuzselim, Güneştepe, Bağcılar"
hat_ekle_ve_bagla(G, "T1", t1_duraklar, 65)

# T3 Hattı Durakları (Ring olduğu için çift yönlü eklenmesi yeterlidir.)
t3_duraklar = "Kadıköy İDO, İskele Camii, Çarşı, Altıyol, Bahariye, Kilise, Moda İlkokulu, Moda, Rızapaşa, Mühürdar, Damga Sokak"
hat_ekle_ve_bagla(G, "T3", t3_duraklar, 20)

# T4 Hattı Durakları
t4_duraklar = "Topkapı, Fetihkapı, Vatan, Edirnekapı, Şehitlik, Demirkapı, Topçular, Rami, Uluyol Bereç, Sağmalcılar, Bosna Çukurçeşme, Ali Fuat Başgil, Taşköprü, Karadeniz, Kiptaş-Venezia, Cumhuriyet Mahallesi, 50.Yıl-Baştabya, Hacı Şükrü, Yenimahalle, Sultançiftliği, Cebeci, Mescid-i Selam"
hat_ekle_ve_bagla(G, "T4", t4_duraklar, 45)

# T5 Hattı Durakları
t5_duraklar = "Eminönü, Küçükpazar, Cibali, Fener, Balat, Ayvansaray, Feshane, Eyüpsultan Teleferik, Eyüpsultan Devlet Hastanesi, Silahtarağa Mahallesi, Üniversite, Alibeyköy Merkez, Alibeyköy Metro, Alibeyköy Cep Otogarı"
hat_ekle_ve_bagla(G, "T5", t5_duraklar, 32)

# F1 Hattı Durakları
f1_duraklar = "Taksim, Kabataş"
hat_ekle_ve_bagla(G, "F1", f1_duraklar, 2.5)

# F4 Hattı Durakları
f4_duraklar = "Boğaziçi Ü./Hisarüstü, Aşiyan"
hat_ekle_ve_bagla(G, "F4", f4_duraklar, 2.5)

# TF1 Hattı Durakları
tf1_duraklar = "Maçka, Taşkışla"
hat_ekle_ve_bagla(G, "TF1", tf1_duraklar, 3.5)

# TF2 Hattı Durakları
tf2_duraklar = "Eyüp, Piyer Loti"
hat_ekle_ve_bagla(G, "TF2", tf2_duraklar, 2.75)

# 4. VERİ GİRİŞİ - TÜM AKTARMALAR (M, T, F, TF + Dış Sistemler)

print("\n--- Aktarma Bağlantıları Kuruluyor (M, T, F, TF + Dış Sistemler) ---")

# DİKKAT: Aynı isimdeki duraklar (Yenikapı, Aksaray, Taksim, Levent vb.) 
# NetworkX tarafından otomatik olarak birleştirilmiştir (merge). 
# Bu yüzden M-M, M-F, T-T, T-F gibi ortak isme sahip olan aktarmalar için 
# "aktarma_ekle" kullanmaya gerek yoktur.


tum_aktarmalar = {}
AKTARMA_SURESI = 3 # Sabit Aktarma Süresi (Dakika)

# ****************** M HATLARI DİĞER SİSTEMLERLE ******************
m_entegrasyonlar = {
    # M1A / M9
    'Yenibosna': ['Metrobüs_Yenibosna'], 
    'Ataköy': ['Marmaray_Ataköy'], 
    # M2
    'Şişli-Mecidiyeköy': ['Metrobüs_Mecidiyeköy'], 
    'Gayrettepe': ['M11_Gayrettepe', 'Metrobüs_Gayrettepe'],
    # M3
    'İncirli': ['Metrobüs_İncirli'],                
    'Özgürlük Meydanı': ['Marmaray_Bakırköy', 'HızlıTren_Bakırköy'], 
    # M4
    'Ayrılık Çeşmesi': ['Marmaray_Ayrılık Çeşmesi'],         
    'Ünalan': ['Metrobüs_Ünalan'],                          
    'Pendik': ['YHT_Pendik'], 
    # M5
    'Üsküdar': ['Marmaray_Üsküdar', 'DenizHatları_Üsküdar'], 
    'Altunizade': ['Metrobüs_Altunizade'],                   
    # M8
    'Bostancı': ['Marmaray_Bostancı', 'YHT_Bostancı', 'DenizHatları_Bostancı'], 
}
tum_aktarmalar.update(m_entegrasyonlar)

# ****************** T HATLARI DİĞER SİSTEMLERLE ******************
t_entegrasyonlar = {
    # T1 (M, F, Marmaray ile ortak duraklar üzerinden otomatik bağlanır)
    'Sirkeci': ['Marmaray_Sirkeci', 'T6_Sirkeci'],
    'Eminönü': ['DenizHatları_Eminönü'], 
    'Karaköy': ['F2_Karaköy', 'DenizHatları_Karaköy'], 
    'Kabataş': ['DenizHatları_Kabataş'], 
    'Topkapı': ['Metrobüs_Topkapı'], 
    'Cevizlibağ-AÖY': ['Metrobüs_Cevizlibağ'],
    'Zeytinburnu': ['Metrobüs_Zeytinburnu'],
    
    # T3 (M4 ile ortak durak ismi olmadığı için elle aktarma yapılmalı)
    'İskele Camii': ['Kadıköy_M4'], # T3 İskele Camii -> M4 Kadıköy
    'Kadıköy İDO': ['Kadıköy_M4', 'DenizHatları_Kadıköy'], # T3 Kadıköy İDO -> M4 Kadıköy
    
    # T4
    'Şehitlik': ['Metrobüs_Şehitlik'], 
    
    # T5
    'Feshane': ['DenizHatları_Feshane'],
    'Ayvansaray': ['DenizHatları_Ayvansaray'],
    'Balat': ['DenizHatları_Balat'],
    'Fener': ['DenizHatları_Fener'],
}
tum_aktarmalar.update(t_entegrasyonlar)

# ****************** F ve TF HATLARI DİĞER SİSTEMLERLE ******************
f_tf_entegrasyonlar = {
    # F4
    'Aşiyan': ['DenizHatları_Aşiyan'],                  
    
    # TF2 (T5 ve Deniz Hattına bağlantı)
    'Eyüp': ['Eyüpsultan Teleferik_T5', 'DenizHatları_Eyüp'], # TF2 Eyüp -> T5 Eyüpsultan Teleferik
}
tum_aktarmalar.update(f_tf_entegrasyonlar)

print("-----------------------------------")
print(f"[Graf Hazır] Toplam Düğüm: {G.number_of_nodes()}, Toplam Kenar: {G.number_of_edges()}")
# ... T hatlarına ait tum_aktarmalar.update(t_entegrasyonlar) çağrısından sonra ...

# Aktarmaları Grafiğe Uygulama
basarili_baglanti_sayisi = 0

for baslangic_durak, hedef_duraklar in tum_aktarmalar.items():
    for hedef in hedef_duraklar:
        
        # <<< 1. HEDEF DÜĞÜM EKLEME MANTIĞI BURAYA GELİR >>>
        # Hedef aktarma durağı grafikte yoksa (Metrobüs, Marmaray vb.), önce onu ekle
        if hedef not in G:
            hedef_hat_kodu = hedef.split("_")[0] 
            G.add_node(hedef, tip="Aktarma Noktası", hat=hedef_hat_kodu)
        # <<< HEDEF DÜĞÜM EKLEME BİTTİ >>>

        # Aktarma işlemini yap (T3 ve TF2 gibi özel durumlar)
        
        # T3 İskele Camii -> M4 Kadıköy özel bağlantısı
        if baslangic_durak == 'İskele Camii' and hedef == 'Kadıköy_M4':
            if aktarma_ekle(G, baslangic_durak, 'Kadıköy', AKTARMA_SURESI, f"Aktarma T3-M4"):
                basarili_baglanti_sayisi += 1

        # T3 Kadıköy İDO -> M4 Kadıköy özel bağlantısı
        elif baslangic_durak == 'Kadıköy İDO' and hedef == 'Kadıköy_M4':
            if aktarma_ekle(G, baslangic_durak, 'Kadıköy', AKTARMA_SURESI, f"Aktarma T3-M4"):
                basarili_baglanti_sayisi += 1

        # TF2 Eyüp -> T5 Eyüpsultan Teleferik özel bağlantısı
        elif baslangic_durak == 'Eyüp' and hedef == 'Eyüpsultan Teleferik_T5':
            if aktarma_ekle(G, baslangic_durak, 'Eyüpsultan Teleferik', AKTARMA_SURESI, f"Aktarma TF2-T5"):
                basarili_baglanti_sayisi += 1

        # Diğer tüm normal ve dış sistem aktarmaları
        else:
            if aktarma_ekle(G, baslangic_durak, hedef, AKTARMA_SURESI, f"Aktarma"):
                 basarili_baglanti_sayisi += 1

# <<< BU SATIR DÖNGÜNÜN DIŞINA ÇIKARILMALIDIR >>>
print(f"Toplam {basarili_baglanti_sayisi} adet aktarma bağlantısı kuruldu.")

# Bu fonksiyon, rotayı hesaplayan ana iş mantığınızdır (Eski Bölüm 5'in Rota hesaplama kısmı)
def rota_hesapla(baslangic, hedef):
    try:
        yol = nx.dijkstra_path(G, baslangic, hedef, weight='agirlik')
        sure = nx.dijkstra_path_length(G, baslangic, hedef, weight='agirlik')
        
        rota_detaylari = []
        for i, durak in enumerate(yol):
            onceki_durak = yol[i-1] if i > 0 else None
            hat_bilgisi = ""
            
            if onceki_durak:
                 kenar_datasi = G[onceki_durak][durak]
                 kenar_tipi = kenar_datasi.get('tip', '')
                 
                 if 'Aktarma' in kenar_tipi:
                     hat_bilgisi = "Aktarma"
                 elif kenar_tipi == 'Yolculuk':
                     hat_bilgisi = kenar_datasi.get('hat', 'Bilinmeyen Hat')

            rota_detaylari.append({
                "durak": durak,
                "hat": hat_bilgisi
            })
            
        return {
            "basarili": True,
            "toplam_sure": f"{sure:.2f}",
            "rota": rota_detaylari,
        }

    except nx.NetworkXNoPath:
        return {"basarili": False, "hata": f"[{baslangic} - {hedef}] arasında yol bulunamadı."}
    except nx.NodeNotFound as e:
        return {"basarili": False, "hata": f"Durak bulunamadı: {e}. Lütfen durak isimlerini kontrol edin."}
    except Exception as e:
        return {"basarili": False, "hata": f"Beklenmedik Hata: {e}"}


# ------------------------------------------------------------------
# API Endpoint'leri
<<<<<<< HEAD
=======
# 
# ------------------------------------------------------------------
# API Endpoint'leri
>>>>>>> 5bb0b9c (Optimizasyon için düzeltilmiş kodlar)
# ------------------------------------------------------------------

# 1. Anasayfa (HTML formunun yükleneceği yer)
@app.route('/')
def index():
<<<<<<< HEAD
    # Tüm durak isimlerini otomatik tamamlama için toplayalım
=======
>>>>>>> 5bb0b9c (Optimizasyon için düzeltilmiş kodlar)
    tum_duraklar = sorted(list(G.nodes()))
    return render_template('index.html', duraklar=tum_duraklar)

# 2. Rota Hesaplama API'si (Formun veriyi göndereceği yer)
<<<<<<< HEAD
@app.route('/hesapla', methods=['POST'])
def hesapla():
=======
@app.route('/arama', methods=['POST']) # <-- Burası /hesapla yerine /arama olmalı
def arama(): # <-- Fonksiyon adı da arama olmalı
>>>>>>> 5bb0b9c (Optimizasyon için düzeltilmiş kodlar)
    baslangic = request.form.get('baslangic')
    hedef = request.form.get('hedef')
    
    if not baslangic or not hedef:
<<<<<<< HEAD
=======
        # Hata durumunda HTML döndürmek yerine JSON döndürelim
>>>>>>> 5bb0b9c (Optimizasyon için düzeltilmiş kodlar)
        return jsonify({"basarili": False, "hata": "Başlangıç ve hedef durakları zorunludur."})
        
    sonuc = rota_hesapla(baslangic.strip(), hedef.strip())
    return jsonify(sonuc) # JSON formatında sonucu döndür

if __name__ == '__main__':
    # Flask uygulamasını çalıştır
<<<<<<< HEAD
    print("Web uygulaması başlatılıyor... http://127.0.0.1:5000/")
    app.run(debug=True)
=======
    print("Web uygulaması başlatılıyor... http://127.0.0.1:5000")
    app.run(debug=True)
>>>>>>> 5bb0b9c (Optimizasyon için düzeltilmiş kodlar)
