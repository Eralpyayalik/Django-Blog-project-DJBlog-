import time
import random
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from article.models import Article

class Command(BaseCommand):
    help = 'Arka planda belirli aralıklarla AI makalesi üretir'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('AI Zamanlayıcı başlatıldı...'))
        
        ai_usernames = ['Melis_Arkan', 'Caner_Yildiz', 'Selin_Yilmaz']
        
        while True:
            try:
                # Son AI paylaşımını kontrol et
                last_ai_post = Article.objects.filter(author__username__in=ai_usernames).order_by('-created_date').first()
                
                if last_ai_post:
                    now = timezone.now()
                    time_since_last_post = now - last_ai_post.created_date
                    twelve_hours = timedelta(hours=12)
                    
                    if time_since_last_post < twelve_hours:
                        remaining_time = twelve_hours - time_since_last_post
                        sleep_seconds = remaining_time.total_seconds()
                        
                        # 0'dan küçük çıkma ihtimaline karşı güvenlik kilidi
                        if sleep_seconds > 0:
                            self.stdout.write(self.style.WARNING(
                                f"Son AI paylaşımı {last_ai_post.created_date.strftime('%d.%m.%Y %H:%M')} tarihinde yapılmış. "
                                f"Henüz 12 saat dolmamış (Geçen süre: {int(time_since_last_post.total_seconds() // 60)} dakika). "
                                f"{int(sleep_seconds // 60)} dakika boyunca uyku moduna geçiliyor..."
                            ))
                            time.sleep(sleep_seconds)
                            continue # Uyku bittikten sonra döngüyü baştan başlat ve paylaşımı yap
                
                self.stdout.write(self.style.HTTP_INFO('Otomatik AI paylaşımı tetikleniyor...'))
                call_command('generate_ai_post')
                
                # EKSTRA ETKİLEŞİM: Rastgele 2-3 makaleye daha yorum/beğeni yap (Gezgin Modu)
                self.stdout.write(self.style.HTTP_INFO('AI yazarları eski yazıları geziyor...'))
                from article.ai_utils import generate_ai_interaction
                for _ in range(random.randint(2, 3)):
                    inter_result = generate_ai_interaction() # Parametre vermezsek rastgele makale seçer
                    self.stdout.write(self.style.SUCCESS(f'Etkileşim: {inter_result}'))

                self.stdout.write(self.style.SUCCESS('İşlem tamam. 12 saat bekleniyor...'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Hata oluştu: {e}'))
            
            # Normal şartlarda 12 saat bekle (12 * 3600 saniye)
            time.sleep(43200)
