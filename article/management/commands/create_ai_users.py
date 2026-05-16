from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import Profile
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'AI hayalet yazarları oluşturur'

    def handle(self, *args, **options):
        ai_users = [
            {
                'username': 'Melis_Arkan',
                'first_name': 'Melis',
                'last_name': 'Arkan',
                'bio': 'Gelecek teknolojileri ve yapay zeka üzerine araştırmalar yapan bir teknoloji tutkunu. Yazılımın dünyayı nasıl değiştirdiğini takip ediyorum.',
                'img': 'static/ai_avatars/melis.png'
            },
            {
                'username': 'Caner_Yildiz',
                'first_name': 'Caner',
                'last_name': 'Yıldız',
                'bio': 'Backend geliştirici ve açık kaynak hayranı. Kod yazarken içtiğim kahvenin kalitesi, kodun kalitesini belirler.',
                'img': 'static/ai_avatars/caner.png'
            },
            {
                'username': 'Selin_Yilmaz',
                'first_name': 'Selin',
                'last_name': 'Yılmaz',
                'bio': 'Minimalist yaşam, sürdürülebilir gezi rehberleri ve modern yaşam üzerine içerikler üretiyorum. Dünyayı gezerek öğreniyorum.',
                'img': 'static/ai_avatars/selin.png'
            }
        ]

        for u_data in ai_users:
            user, created = User.objects.get_or_create(
                username=u_data['username'],
                defaults={
                    'first_name': u_data['first_name'],
                    'last_name': u_data['last_name'],
                    'email': f"{u_data['username'].lower()}@ai-blog.com"
                }
            )
            
            if created:
                user.set_password('ai_power_2026')
                user.save()
                
                # Profil bilgilerini güncelle
                profile = user.profile
                profile.bio = u_data['bio']
                
                # Resmi Cloudinary'ye yüklemek için dosyayı aç
                if os.path.exists(u_data['img']):
                    with open(u_data['img'], 'rb') as f:
                        profile.image.save(f"{u_data['username']}.png", File(f), save=True)
                
                self.stdout.write(self.style.SUCCESS(f'Yazar oluşturuldu: {user.username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Yazar zaten var: {user.username}'))
