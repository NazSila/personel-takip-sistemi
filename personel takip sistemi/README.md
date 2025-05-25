# Personel Giriş-Çıkış Takip Sistemi

Bu proje, bir işletmenin personel bilgilerinin yönetilmesi ve giriş-çıkış saatlerinin kayıt altına alınması için geliştirilmiş web tabanlı bir sistemdir. Flask framework'ü ile geliştirilmiştir ve SQLite veri tabanı kullanır.

## 🚀 Özellikler

- Personel kayıt ekleme, düzenleme ve silme
- Giriş ve çıkış saatlerini kayıt altına alma
- Giriş/çıkış raporlama ekranı
- Yönetici paneli (dashboard)
- Kullanıcı girişi ekranı
- Basit ve anlaşılır arayüz

## 🛠️ Kullanılan Teknolojiler

- Python
- Flask
- SQLite
- HTML + Jinja2 Template
- (Varsa) Bootstrap

## 📁 Proje Dosya Yapısı

```
personel takip sistemi/
├── app.py                  # Ana Flask uygulaması
├── personel.db             # SQLite veritabanı
├── requirements.txt        # Gereken Python paketleri
└── templates/              # HTML şablon dosyaları
    ├── base.html
    ├── login.html
    ├── kayit.html
    ├── dashboard.html
    ├── personel.html
    ├── personel_ekle.html
    ├── personel_duzenle.html
    ├── personel_giris_cikis.html
    ├── giris_ekle.html
    ├── cikis_ekle.html
    └── raporlar.html
```

## ⚙️ Kurulum ve Çalıştırma

1. Python 3 yüklü olmalıdır.
2. Proje dizinine terminal veya komut satırı ile gidin.
3. Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

4. Uygulamayı başlatın:

```bash
python app.py
```

5. Tarayıcıdan şu adresi ziyaret edin:

```
http://127.0.0.1:5000
```



## 🧠 Öğrenilenler

- Flask ile routing, veri işlemleri ve template kullanımı
- SQLite ile temel veritabanı yönetimi
- CRUD (Create, Read, Update, Delete) işlemleri
- Web uygulaması geliştirme sürecinin yönetimi

## 🔧 Geliştirilebilir Özellikler

- Admin / kullanıcı yetkilendirme sistemi
- Giriş/çıkışlara konum veya cihaz bilgisi ekleme
- Mobil uyumluluk geliştirmeleri
- API desteği ile farklı sistemlere entegrasyon


