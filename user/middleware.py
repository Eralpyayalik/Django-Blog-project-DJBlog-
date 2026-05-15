from django.utils import timezone
from user.models import Profile

class LastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Her istekte Profile güncellemek performansı etkileyebilir, 
            # ama kullanıcının isteği üzerine her istekte güncelliyoruz.
            Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
        
        response = self.get_response(request)
        return response
