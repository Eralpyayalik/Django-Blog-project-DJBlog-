import time
import schedule
import random
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Arka planda belirli aralıklarla AI makalesi üretir'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('AI Zamanlayıcı başlatıldı...'))
        
        # Her 12 saatte bir yeni makale üret
        # Test amaçlı şimdilik daha kısa tutulabilir ama 12 saat idealdir
        while True:
            try:
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
            
            # 12 saat bekle (12 * 3600 saniye)
            time.sleep(43200)
