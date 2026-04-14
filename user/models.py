
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', verbose_name="Profil Resmi")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Hakkımda")
    github = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.user.username} Profili'

    # XP ve Rütbe 
    @property
    def total_xp(self):
        # Makale: 50 XP | Yorum: 10 XP
        try:
            article_xp = self.user.article_set.count() * 50
            comment_xp = self.user.comment_set.count() * 10
            return article_xp + comment_xp
        except:
            return 0

    @property
    def rank_info(self):
        xp = self.total_xp
        if xp < 100:
            return {"title": "Çaylak Yazar", "color": "#6c757d", "icon": "fa-pen-nib"}
        elif xp < 300:
            return {"title": "Yetkin Kalem", "color": "#17a2b8", "icon": "fa-book-open"}
        elif xp < 700:
            return {"title": "Usta Yazar", "color": "#007bff", "icon": "fa-keyboard"}
        else:
            return {"title": "Baş Editör", "color": "#ffc107", "icon": "fa-award"}

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        if hasattr(instance, 'profile'):
            instance.profile.save()
        

