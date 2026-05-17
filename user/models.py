
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
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Son Görülme")

    @property
    def is_online(self):
        if self.last_seen:
            from django.utils import timezone
            now = timezone.now()
            return now < self.last_seen + timezone.timedelta(minutes=5)
        return False

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
        if xp < 50:
            return {"title": "Yeni Üye", "color": "#94a3b8", "icon": "fa-user", "class": "yeni"}
        elif xp < 150:
            return {"title": "Çaylak Yazar", "color": "#6c757d", "icon": "fa-pen-nib", "class": "caylak"}
        elif xp < 300:
            return {"title": "Aktif Yazar", "color": "#0ea5e9", "icon": "fa-pen", "class": "aktif"}
        elif xp < 500:
            return {"title": "Yetkin Kalem", "color": "#10b981", "icon": "fa-book-open", "class": "yetkin"}
        elif xp < 800:
            return {"title": "Usta Yazar", "color": "#3b82f6", "icon": "fa-keyboard", "class": "usta"}
        elif xp < 1200:
            return {"title": "Üstat", "color": "#8b5cf6", "icon": "fa-feather", "class": "ustat"}
        else:
            return {"title": "Baş Editör", "color": "#f59e0b", "icon": "fa-award", "class": "editor"}

    @receiver(post_save, sender=User)
    def create_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_profile(sender, instance, **kwargs):
        if hasattr(instance, 'profile'):
            instance.profile.save()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

    class Meta:
        ordering = ['-created_at']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') # Bildirimi alacak kişi
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_notifications', null=True, blank=True) # Bildirimi tetikleyen kişi
    notification_type = models.CharField(max_length=20) # 'message', 'like', 'reply' vb.
    text = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.notification_type}"

    class Meta:
        ordering = ['-created_at']

        

