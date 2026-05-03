# Ders Notlarından NLP Tabanlı Otomatik Flashcard ve Soru-Cevap Üretim Sistemi

## Proje Açıklaması

Bu proje, ders notlarından doğal dil işleme (NLP) tekniklerini kullanarak otomatik olarak flashcard ve soru-cevap çiftleri üreten bir web uygulamasıdır. Öğrencilerin ders materyallerini daha etkili bir şekilde gözden geçirmelerini sağlamak amacıyla geliştirilmiştir.

## Özellikler

- **Metin Girişi ve Dosya Yükleme**: Kullanıcılar ders notlarını metin olarak girebilir veya PDF/DOCX dosyalarını yükleyebilir.
- **Otomatik Flashcard Üretimi**: NLP algoritmaları kullanarak metinden önemli kavramları ve cümleleri çıkarır ve flashcard'lar oluşturur.
- **Soru-Cevap Üretimi**: Metinden otomatik olarak soru-cevap çiftleri üretir.
- **Düzenleme ve Kaydetme**: Üretilen kartları düzenleyebilir ve SQLite veritabanında saklayabilirsiniz.
- **Web Arayüzü**: Flask tabanlı basit ve kullanıcı dostu web arayüzü.

## Teknolojiler

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, Jinja2
- **Veritabanı**: SQLite
- **NLP Kütüphaneleri**: spaCy, NLTK
- **Diğer**: pandas (opsiyonel), Hugging Face Transformers (hafif kullanım)

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

4. **NLP Modellerini İndirin** (spaCy için):
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Kullanım

1. **Uygulamayı Çalıştırın**:
   ```bash
   python run.py
   ```

2. **Tarayıcıda Açın**: `http://localhost:5000`

3. **Ders Notlarını Yükleyin veya Girin**: Ana sayfada metin girin veya dosya yükleyin.

4. **Flashcard'ları ve Soru-Cevap Çiftlerini Üretin**: Uygulama otomatik olarak kartları oluşturacaktır.

5. **Düzenleyin ve Kaydedin**: Kartları düzenleyip veritabanına kaydedin.

## Proje Yapısı

```
TYZM-623-01-Projem/
├── app/                 # Flask uygulaması
├── data/                # Veritabanı ve veri dosyaları
├── docs/                # Dokümantasyon
├── static/              # CSS, JS, resimler
├── templates/           # HTML şablonları
├── tests/               # Test dosyaları
├── requirements.txt     # Python bağımlılıkları
├── run.py               # Uygulama başlatma dosyası
└── README.md            # Bu dosya
```

## Testler

Testleri çalıştırmak için:
```bash
pytest
```

## İletişim

Sorularınız için [GitHub Issues](https://github.com/h-kod/TYZM-623-01-Projem/issues) kullanabilirsiniz.
## Testing

Automated tests can be run with:

```bash
python -m pytest
```

## License

This project is licensed under the MIT License.
