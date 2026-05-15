from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from PIL import Image
from django.contrib.auth.models import User

import user
# Create your models here.


class Category(models.Model):
    name=models.CharField(max_length=50)
    slug=models.SlugField(unique=True)
    def __str__(self):
        return self.name

class Article(models.Model):
    author=models.ForeignKey("auth.User",on_delete=models.CASCADE,verbose_name="Yazar")
    title=models.CharField(max_length=75,verbose_name="Başlık")
    content=RichTextField()
    created_date=models.DateTimeField(auto_now_add=True,verbose_name="Oluşturulma Tarihi")
    article_image=models.FileField(blank=True,null=True,verbose_name="Makaleye Resim Ekle")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    likes = models.ManyToManyField('auth.User', related_name='liked_articles', blank=True)
    read_count = models.IntegerField(default=0, verbose_name="Okunma Sayısı")
    slug = models.SlugField(unique=True, max_length=100, editable=False, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c'))
        super(Article, self).save(*args, **kwargs)

        if self.article_image:
                try:
                    # Resmin tam yolunu al (BASE_DIR + MEDIA_URL gibi)
                    img_path = self.article_image.path
                    img = Image.open(img_path)

                    # EĞER RESİM ZATEN 1200x600 İSE TEKRAR İŞLEM YAPMA (Sonsuz döngü engelleme)
                    if img.size == (1200, 600):
                        return
                    # Boyutlandırma ve Kırpma Mantığı (Aynı kod)
                    target_w, target_h = 1200, 600
                    w, h = img.size
                    target_ratio = target_w / target_h
                    current_ratio = w / h

                    if current_ratio > target_ratio:
                        new_width = int(target_ratio * h)
                        left = (w - new_width) / 2
                        img = img.crop((left, 0, w - left, h))
                    else:
                        new_height = int(w / target_ratio)
                        top = (h - new_height) / 2
                        img = img.crop((0, top, w, h - top))

                    img = img.resize((target_w, target_h), Image.LANCZOS)
                    img.save(img_path, quality=90, optimize=True) 
                    
                except Exception as e:
                    print(f"Resim işlenirken hata oluştu: {e}") 

    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title

    class Meta:
        ordering=['-created_date']

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name="Makale", related_name="comments")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kullanıcı")
    comment_author = models.CharField(max_length=50, verbose_name="İsim")
    comment_content = models.CharField(max_length=200, verbose_name="Yorum")
    comment_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)

    def __str__(self):
        return self.comment_content

    class Meta:
        ordering = ['-comment_date']