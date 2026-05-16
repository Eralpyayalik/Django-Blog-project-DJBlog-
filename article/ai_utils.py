import google.generativeai as genai
import os
import requests
import random
from django.conf import settings
from .models import Article, Category, Comment
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.files.base import ContentFile
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Gemini Yapılandırması
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def get_unsplash_image(query):
    """Unsplash API kullanarak konuya uygun görsel URL'si döner."""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Unsplash hatası: {e}")
    
    return f"https://source.unsplash.com/featured/1200x800?{query}"

def generate_ai_interaction(article=None):
    """Rastgele bir AI kullanıcısının bir makaleyi beğenmesini veya yorum yapmasını sağlar."""
    ai_usernames = ['Melis_Arkan', 'Caner_Yildiz', 'Selin_Yilmaz']
    if not article:
        article = Article.objects.order_by('?').first()
    if not article:
        return "Makale bulunamadı."

    interactor_name = random.choice([u for u in ai_usernames if u != article.author.username])
    interactor = User.objects.get(username=interactor_name)
    choice = random.choice(['LIKE', 'COMMENT', 'BOTH'])
    result_msg = f"{interactor.username} -> "
    
    if choice in ['LIKE', 'BOTH']:
        article.likes.add(interactor)
        result_msg += "Beğendi. "
        
    if choice in ['COMMENT', 'BOTH']:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Sen {interactor.username} isimli, teknoloji, YouTube ve oyun dünyasını yakından takip eden birisin. Arkadaşın {article.author.username}'ın '{article.title}' başlıklı yazısını okudun. Samimi, güncel ve biraz 'sosyal medya' lisanıyla yorum yap. Sadece yorumu döndür."
        try:
            response = model.generate_content(prompt)
            comment_text = response.text.strip().replace('"', '')
            Comment.objects.create(
                article=article,
                user=interactor,
                comment_author=f"{interactor.first_name} {interactor.last_name}",
                comment_content=comment_text
            )
            result_msg += f"Yorum yaptı."
        except:
            result_msg += "Hata."
    return result_msg

def generate_ai_article():
    ai_usernames = ['Melis_Arkan', 'Caner_Yildiz', 'Selin_Yilmaz']
    authors = User.objects.filter(username__in=ai_usernames)
    if not authors.exists(): return "Hata: AI yazarları bulunamadı."
    author = random.choice(authors)
    
    # 2. KONU HAVUZU (Donanım, Oyun, YouTube, Yayıncılık, İnceleme)
    topics = [
        "RTX 5090 Sızıntıları: Donanım Dünyası Sallanıyor", 
        "2026'da İzlenmesi Gereken En İyi YouTube Kanalları", 
        "Twitch'in Yeni Yayıncı Politikası: Kimler Kazanacak?",
        "GTA 6 Fragman Analizi: Kaçırdığınız Detaylar",
        "En İyi Fiyat/Performans Oyuncu Kulaklıkları (2026)",
        "MrBeast'in Yeni Projesi ve YouTube'un Geleceği",
        "PlayStation 6 Hakkında Bildiğimiz Her Şey",
        "Neden Herkes Bir Anda Yayıncı Olmak İstiyor?",
        "Yapay Zeka ile Video Montajı Yapmanın Kolay Yolları",
        "Valorant ve LoL Dünyasındaki Yeni Güncellemeler",
        "Akıllı Telefonlarda 2026 Trendleri: Katlanabilirler Devri",
        "Discord'un Yeni Özellikleri ve Topluluk Yönetimi"
    ]
    topic = random.choice(topics)
    
    model = genai.GenerativeModel('gemini-flash-latest')
    ALLOWED_CATEGORIES = ["Teknoloji", "Yazılım", "Oyun", "İnceleme", "Yayıncılık"]
    
    prompt = f"""
    Sen {author.username} isimli, YouTube, Twitch ve teknoloji dünyasını çok iyi bilen bir içerik üreticisisin.
    Konu: '{topic}'
    
    TALİMATLAR:
    - Dilin samimi, akıcı ve 'genç' olsun. 
    - YouTube trendlerinden, yayıncı dünyasından ve yeni ürünlerden bahset.
    - KATEGORİ sadece şunlardan biri olabilir: {', '.join(ALLOWED_CATEGORIES)}.
    - Yazı Formatı:
      BAŞLIK: [Başlık]
      İÇERİK: [HTML Formatında, en az 400 kelime, detaylı ve güncel bilgiler içeren içerik]
      KATEGORİ: [Seçilen Kategori]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "BAŞLIK:" not in text or "İÇERİK:" not in text or "KATEGORİ:" not in text:
            return f"Hata: AI formatı bozdu."

        title = text.split("BAŞLIK:")[1].split("İÇERİK:")[0].strip()
        content = text.split("İÇERİK:")[1].split("KATEGORİ:")[0].strip()
        raw_category = text.split("KATEGORİ:")[1].replace("*", "").strip()
        
        category_name = "Teknoloji"
        for cat in ALLOWED_CATEGORIES:
            if cat.lower() in raw_category.lower():
                category_name = cat
                break
        category, _ = Category.objects.get_or_create(name=category_name)
        
        image_url = get_unsplash_image(slugify(topic))
        article = Article(author=author, title=title, content=content, category=category)
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            article.article_image.save(f"{slugify(title)}.jpg", ContentFile(img_response.content), save=False)
        article.save()
        
        generate_ai_interaction(article)
        return f"Başarılı: '{title}' (Yayıncılık/Teknoloji odaklı) paylaşıldı."
        
    except Exception as e:
        return f"Hata: {str(e)}"
