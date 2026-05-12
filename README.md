# Ders Notlarından Yapay Zeka Destekli Flashcard Üretim Sistemi

## Proje Açıklaması

Bu proje, ders notlarından otomatik olarak flashcard ve soru-cevap çiftleri üreten bir web uygulamasıdır. Öğrencilerin ders materyallerini daha etkili bir şekilde gözden geçirmelerini sağlamak amacıyla geliştirilmiştir.

## Özellikler

- **Metin Girişi ve Dosya Yükleme**: Kullanıcılar ders notlarını metin olarak girebilir veya UTF-8 olarak okunabilen dosya içeriği kullanabilir.
- **Otomatik Flashcard Üretimi**: Metinden önemli kavramları ve cümleleri çıkarır ve flashcard'lar oluşturur.
- **Soru-Cevap Üretimi**: Metinden otomatik olarak soru-cevap çiftleri üretir.
- **Düzenleme ve Kaydetme**: Üretilen kartları düzenleyebilir ve SQLite veritabanında saklayabilirsiniz.
- **Web Arayüzü**: Flask tabanlı basit ve kullanıcı dostu web arayüzü.

## Teknolojiler

- **Backend**: Python, Flask, requests
- **Frontend**: HTML, CSS, Jinja2, JavaScript
- **Veritabanı**: SQLite
- **Test**: pytest

## Kurulum

1. **Depoyu Klonlayın**:
   ```bash
   git clone https://github.com/h-kod/TYZM-623-01-Projem.git
   cd TYZM-623-01-Projem
   ```

2. **Sanal Ortam Oluşturun ve Aktifleştirin**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows için
   ```

3. **Gerekli Paketleri Yükleyin**:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

1. **Uygulamayı Çalıştırın**:
   ```bash
   python run.py
   ```

2. **Tarayıcıda Açın**: `http://localhost:5000`

3. **Ders Notlarını Yükleyin veya Girin**: Ana sayfada metin girin veya uygulamanın kabul ettiği dosya girişini kullanın.

4. **Flashcard'ları ve Soru-Cevap Çiftlerini Üretin**: Uygulama otomatik olarak kartları oluşturacaktır.

5. **Düzenleyin ve Kaydedin**: Kartları düzenleyip veritabanına kaydedin.

## Proje Yapısı

```
TYZM-623-01-Projem/
├── app/                 # Flask uygulaması
├── data/                # Veritabanı ve veri dosyaları
├── static/              # CSS, JS, resimler
├── templates/           # HTML şablonları
├── tests/               # Test dosyaları
├── requirements.txt     # Python bağımlılıkları
├── run.py               # Uygulama başlatma dosyası
└── README.md            # Bu dosya
```

## Testing

Automated tests can be run with:

```bash
python -m pytest
```

## Render ile Yayınlama

Bu proje Render uzerinde Flask web service olarak yayimlanabilir.

1. Repoyu GitHub'a push edin.
2. Render'da `New > Blueprint` veya `New > Web Service` secin.
3. Repo baglandiginda su ayarlari kullanin:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
4. `GEMINI_API_KEY` ortam degiskenini Render panelinden ekleyin.

Repoda hazir bir [render.yaml](render.yaml) dosyasi vardir. `Blueprint` ile kurulum yaparsaniz bu ayarlar otomatik okunur.

Not: Render varsayilan olarak kalici olmayan bir dosya sistemi kullanir. Bu nedenle `data/*.db` altindaki SQLite verileri deploy sonrasinda korunmaz. Kalici veri gerekiyorsa Render Postgres veya bir persistent disk kullanin.

## License

This project is licensed under the MIT License.
