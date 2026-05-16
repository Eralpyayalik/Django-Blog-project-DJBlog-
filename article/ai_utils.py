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
        prompt = f"Sen {interactor.username} isimli, teknoloji ve yayıncı dünyasını takip eden birisin. Arkadaşın {article.author.username}'ın '{article.title}' başlıklı yazısına samimi, kısa bir yorum yap. Sadece yorumu döndür."
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
    
    topics = [
        "RTX 5090 Sızıntıları ve Performans Beklentileri", 
        "2026'da İzlenmesi Gereken YouTuber'lar", 
        "Twitch vs YouTube: Yayıncılar Nereye Gidiyor?",
        "GTA 6'dan Yeni Detaylar: Harita ve Karakterler",
        "En İyi Oyuncu Mouse'ları: Ürün İncelemesi",
        "PlayStation 6 Hakkındaki Son Söylentiler",
        "Yazılımcılar İçin En İyi Laptoplar (2026)",
        "Yeni Nesil Akıllı Gözlükler ve VR Dünyası",
        "Mobil Oyun Dünyasındaki Devrim: Yeni AAA Oyunlar",
        "E-Spor Arenasında Bu Hafta Neler Oldu?"
    ]
    topic = random.choice(topics)
    
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # KESİN VE NET KATEGORİ LİSTESİ
    ALLOWED_CATEGORIES = ["Teknoloji", "Yazılım", "Oyun", "Ürün İnceleme", "Yayıncılık"]
    
    prompt = f"""
    Sen {author.username} isimli bir teknoloji içerik üreticisisin.
    Konu: '{topic}'
    
    KURALLAR:
    1. KATEGORİ mutlaka şu listeden biri olmalıdır: {', '.join(ALLOWED_CATEGORIES)}.
    2. Sakın 'İnceleme' veya başka bir isim kullanma, eğer ürün inceliyorsan tam olarak 'Ürün İnceleme' yaz.
    3. Yazı Formatı:
       BAŞLIK: [Başlık]
       İÇERİK: [HTML İçerik]
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
        
        # AKILLI EŞLEŞTİRME (Mapping)
        category_name = "Teknoloji" # Varsayılan
        
        # Eğer AI 'İnceleme' falan derse onu 'Ürün İnceleme'ye çek
        if "inceleme" in raw_category.lower():
            category_name = "Ürün İnceleme"
        elif "oyun" in raw_category.lower():
            category_name = "Oyun"
        elif "yazılım" in raw_category.lower() or "kod" in raw_category.lower():
            category_name = "Yazılım"
        elif "yayın" in raw_category.lower() or "youtube" in raw_category.lower() or "twitch" in raw_category.lower():
            category_name = "Yayıncılık"
        elif "tekno" in raw_category.lower():
            category_name = "Teknoloji"
            
        # Son bir kontrol: Eğer hala listede yoksa zorla listeden birini seç
        if category_name not in ALLOWED_CATEGORIES:
            category_name = random.choice(ALLOWED_CATEGORIES)

        category, _ = Category.objects.get_or_create(name=category_name)
        
        image_url = get_unsplash_image(slugify(topic))
        article = Article(author=author, title=title, content=content, category=category)
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            article.article_image.save(f"{slugify(title)}.jpg", ContentFile(img_response.content), save=False)
        article.save()
        
        generate_ai_interaction(article)
        return f"Başarılı: '{title}' ({category_name} kategorisinde) paylaşıldı."
        
    except Exception as e:
        return f"Hata: {str(e)}"
