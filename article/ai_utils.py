import google.generativeai as genai
import os
import requests
import random
from django.conf import settings
from .models import Article, Category
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
    
    # Yedek (Fallback)
    return f"https://source.unsplash.com/featured/1200x800?{query}"

def generate_ai_article():
    # 1. Yazarı Rastgele Seç
    ai_usernames = ['Melis_Arkan', 'Caner_Yildiz', 'Selin_Yilmaz']
    authors = User.objects.filter(username__in=ai_usernames)
    
    if not authors.exists():
        return "Hata: AI yazarları bulunamadı."
    
    author = random.choice(authors)
    
    # 2. Konu Seçimi
    topics = [
        "Yapay Zekanın Günlük Hayattaki Etkileri", 
        "Modern Web Tasarımında Renk Psikolojisi", 
        "Minimalist Çalışma Alanı Nasıl Kurulur?",
        "Sürdürülebilir Bir Gelecek İçin 5 Adım",
        "2026'da Yazılım Dünyasını Neler Bekliyor?",
        "Dijital Detoks: Neden İhtiyacımız Var?",
        "E-ticaretin Geleceği ve Web3 Teknolojileri",
        "Kendi Kendine Öğrenme (Self-Learning) Sanatı"
    ]
    topic = random.choice(topics)
    
    # 3. Gemini ile İçerik Üretme
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Sen profesyonel bir blog yazarı olan {author.username} karakterisin. 
    Lütfen '{topic}' konusu üzerine Türkçe, ilgi çekici, bilgilendirici ve samimi bir blog yazısı yaz.
    Yazı şu formatta olsun:
    BAŞLIK: [Buraya etkileyici bir başlık]
    İÇERİK: [Buraya en az 400 kelimelik, HTML formatında (p, h2, ul, li etiketleri kullanarak) zengin bir içerik]
    KATEGORİ: [Teknoloji, Yaşam, Yazılım, Gezi kategorilerinden birini seç]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse Title, Content and Category
        # Bazı durumlarda AI formatı bozabilir, basit bir kontrol ekleyelim
        if "BAŞLIK:" not in text or "İÇERİK:" not in text or "KATEGORİ:" not in text:
            return f"Hata: AI beklenmedik bir format döndürdü. \nİçerik: {text[:100]}..."

        title = text.split("BAŞLIK:")[1].split("İÇERİK:")[0].strip()
        content = text.split("İÇERİK:")[1].split("KATEGORİ:")[0].strip()
        category_name = text.split("KATEGORİ:")[1].strip()
        
        # 4. Kategori Kontrolü ve Temizliği
        category_name = category_name.replace("*", "").strip()
        category = Category.objects.filter(name=category_name).first()
        if not category:
            category = Category.objects.create(name=category_name)
        
        # 5. Görsel Seçimi (Unsplash API)
        image_url = get_unsplash_image(slugify(topic))
        
        # 6. Makaleyi Oluştur
        article = Article(
            author=author,
            title=title,
            content=content,
            category=category,
        )
        
        # Görseli indir ve kaydet
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            article.article_image.save(f"{slugify(title)}.jpg", ContentFile(img_response.content), save=False)
        
        article.save()
        
        return f"Başarılı: '{title}' isimli makale {author.username} tarafından paylaşıldı."
        
    except Exception as e:
        return f"Hata oluştu: {str(e)}"
