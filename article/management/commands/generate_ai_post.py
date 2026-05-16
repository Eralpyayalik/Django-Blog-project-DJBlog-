from django.core.management.base import BaseCommand
from article.ai_utils import generate_ai_article

class Command(BaseCommand):
    help = 'Yapay zeka ile otomatik makale üretir ve yayınlar'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('AI Makale üretimi başlatılıyor...'))
        result = generate_ai_article()
        
        if "Başarılı" in result:
            self.stdout.write(self.style.SUCCESS(result))
        else:
            self.stdout.write(self.style.ERROR(result))
