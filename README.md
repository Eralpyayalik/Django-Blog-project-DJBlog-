#  DjBlog - Django Blog Project

DjBlog, Python'ın güçlü ve güvenli web framework'ü **Django** kullanılarak geliştirilmiş; özelleştirilmiş kullanıcı yönetiminden zengin metin editörlerine, dinamik içerik mimarisinden gelişmiş etkileşim sistemlerine kadar modern bir web platformunun tüm ihtiyaçlarını barındıran profesyonel bir blog projesidir.

website:https://django-blog-project-djblog-production.up.railway.app/

## ✨ Özellikler

* **Özelleştirilmiş Kullanıcı & Profil Yönetimi:** Django'nun yerleşik yapısı yerine `AbstractUser` kullanılarak kurgulanmış esnek üyelik sistemi. Her kullanıcıya özel biyografi, sosyal medya linkleri ve profil fotoğrafı barındıran dinamik `Profile` yapısı.
* **Zengin Metin Editörü (Rich Text) Entegrasyonu:** `CKEditor` entegrasyonu sayesinde admin paneli ve içerik üreticileri için görsel, kod bloğu ve biçimlendirilmiş metinleri kolayca yönetme imkanı.
* **Gelişmiş İçerik Mimarisi:** Gönderiler için SEO dostu `slug` yönetimi, kategorilendirme, taslak (`Draft`) veya yayında (`Published`) durum kontrolleri ve yayınlanma tarihine göre dinamik sıralama.
* **Etkileşim Sistemleri:** Okuyucuların gönderilere yorum yapabilmesi, içerikleri beğenmesi/favorilere eklemesi ve dinamik etkileşim sayıları.
* **Modüler Arayüz (Jinja2/Django Templates):** Tekrarlayan UI elementlerinin (`navbar`, `sidebar`, `footer`) `base.html` şablonu üzerinden `extends` ve `include` pratikleri ile temiz bir şekilde yönetilmesi.

---

## 🛠️ Kullanılan Teknolojiler & Kütüphaneler

Projenin arkasındaki güçlü teknoloji yığını:

* **Framework:** [Django](https://www.djangoproject.com/) (Python tabanlı yüksek seviyeli web framework)
* **Veritabanı / ORM:** Django ORM & SQLite (Production ortamları için PostgreSQL/MySQL uyumlu mimari)
* **Zengin Metin Editörü:** `django-ckeditor`
* **Form & UI Yönetimi:** Django Forms & Widgets özelleştirmeleri

---

## 📂 Klasör Yapısı

Proje, ölçeklenebilir ve sürdürülebilir olması adına monolitik ama modüler bir yapıda tasarlanmıştır:

```text
├── djblog/              # Projenin ana ayar klasörü (settings.py, urls.py, wsgi.py)
├── accounts/            # Kullanıcı kayıt, giriş, custom user ve profil logic'leri
├── blog/                # Kategoriler, gönderiler, yorumlar, slug ve ana içerik mimarisi
├── media/               # Kullanıcıların yüklediği profil fotoğrafları ve blog görselleri
├── static/              # CSS, JavaScript ve tema dosyaları
├── templates/           # Proje genelinde kullanılan HTML şablonları (layout, auth, blog sayfaları)
└── manage.py            # Django yönetim betiği
