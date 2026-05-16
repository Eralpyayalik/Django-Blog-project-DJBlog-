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

    # Yazarı hariç tutarak bir etkileşimci seç
    interactor_name = random.choice([u for u in ai_usernames if u != article.author.username])
    interactor = User.objects.get(username=interactor_name)
    
    choice = random.choice(['LIKE', 'COMMENT', 'BOTH'])
    
    result_msg = f"{interactor.username} -> "
    
    # Beğeni Ekle
    if choice in ['LIKE', 'BOTH']:
        article.likes.add(interactor)
        result_msg += "Beğendi. "
        
    # Yorum Ekle
    if choice in ['COMMENT', 'BOTH']:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Sen {interactor.username} isimli blog yazarıyısın. Arkadaşın {article.author.username}'ın '{article.title}' başlıklı yazısını okudun. Bu yazıya Türkçe, samimi, kısa ve mantıklı bir yorum yap. Sadece yorum metnini döndür."
        
        try:
            response = model.generate_content(prompt)
            comment_text = response.text.strip().replace('"', '')
            Comment.objects.create(
                article=article,
                user=interactor,
                comment_author=f"{interactor.first_name} {interactor.last_name}",
                comment_content=comment_text
            )
            result_msg += f"Yorum yaptı: {comment_text[:30]}..."
        except:
            result_msg += "Yorum yaparken hata oluştu."
            
    return result_msg

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
        "Kendi Kendine Öğrenme (Self-Learning) Sanatı",
        "Yazılımcılar İçin Sağlıklı Yaşam İpuçları",
        "Geleceğin Akıllı Şehirleri"
    ]
    topic = random.choice(topics)
    
    # 3. Gemini ile İçerik Üretme
    model = genai.GenerativeModel('gemini-flash-latest')
    ALLOWED_CATEGORIES = ["Teknoloji", "Yazılım", "Yaşam", "Gezi", "Genel"]
    
    prompt = f"""
    Sen profesyonel bir blog yazarı olan {author.username} karakterisin. 
    Lütfen '{topic}' konusu üzerine Türkçe, ilgi çekici, bilgilendirici ve samimi bir blog yazısı yaz.
    KURALLAR:
    1. KATEGORİ sadece şu listeden biri olmalıdır: {', '.join(ALLOWED_CATEGORIES)}.
    2. Yazı formatı:
       BAŞLIK: [Başlık]
       İÇERİK: [HTML İçerik]
       KATEGORİ: [Kategori]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        if "BAŞLIK:" not in text or "İÇERİK:" not in text or "KATEGORİ:" not in text:
            return f"Hata: AI formatı bozdu."

        title = text.split("BAŞLIK:")[1].split("İÇERİK:")[0].strip()
        content = text.split("İÇERİK:")[1].split("KATEGORİ:")[0].strip()
        raw_category = text.split("KATEGORİ:")[1].replace("*", "").strip()
        
        category_name = "Genel"
        for cat in ALLOWED_CATEGORIES:
            if cat.lower() in raw_category.lower():
                category_name = cat
                break
        category, _ = Category.objects.get_or_create(name=category_name)
        
        # 5. Görsel Seçimi
        image_url = get_unsplash_image(slugify(topic))
        
        # 6. Makaleyi Oluştur
        article = Article(author=author, title=title, content=content, category=category)
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            article.article_image.save(f"{slugify(title)}.jpg", ContentFile(img_response.content), save=False)
        article.save()
        
        # 7. OTOMATİK ETKİLEŞİM: Diğer AI kullanıcıları beğensin/yorum yapsın
        generate_ai_interaction(article)
        
        return f"Başarılı: '{title}' paylaşıldı ve etkileşim aldı."
        
    except Exception as e:
        return f"Hata oluştu: {str(e)}"
