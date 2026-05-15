from django.shortcuts import redirect, render
from .forms import LoginForm, ProfileUpdateForm, RegisterForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate, logout
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token 
from django.shortcuts import  get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False 
        user.save()

        mail_subject = 'Hesabınızı Aktifleştirin - DjBlog'
        message = render_to_string('emails/activation_email.html', { 
            'user': user,
            'domain': '127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        
        email_to_send = EmailMessage(mail_subject, message, to=[email])

        email_to_send.content_subtype = "html" 

        
        email_to_send.send()

        messages.success(request, "Kayıt başarılı! Lütfen e-postanıza gelen linke tıklayarak hesabınızı onaylayın.")
        return redirect("user:login")
    
    return render(request, "register.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Hesabınız başarıyla onaylandı! Giriş yapabilirsiniz.")
        return redirect('user:login')
    else:
        messages.error(request, "Aktivasyon linki geçersiz veya süresi dolmuş!")
        return redirect('index')

def loginUser(request):
    form = LoginForm(request.POST or None)
    context = {"form": form}

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        try:
            user_exists = User.objects.get(username=username)
        except User.DoesNotExist:
            user_exists = None

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Başarıyla Giriş Yaptınız")
            return redirect("index")
        
        else:
            
            if user_exists and not user_exists.is_active:
                messages.warning(request, "Hesabınız henüz aktifleştirilmemiş. Lütfen e-postanızı onaylayın.")
            else:
                #
                messages.info(request, "Kullanıcı Adı veya Parola Hatalı")
            
            return render(request, "login.html", context)

    return render(request, "login.html", context)
    
def logoutUser(request):
    logout(request)
    messages.success(request,"Başarıyla Çıkış yaptınız.")
    return redirect("index")


@login_required(login_url="user:login")
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, "profile.html", {"profile": profile})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profilin başarıyla güncellendi!")
            return redirect("user:profile", username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

   
    return render(request, "profile_edit.html", {"u_form": u_form, "p_form": p_form})


def profile_view(request, username):

    user_profile = get_object_or_404(User, username=username)
    
    context = {
        'user_profile': user_profile 
    }
    return render(request, 'profile.html', context)

from .models import Message, Notification
from django.db.models import Q
from django.http import JsonResponse

@login_required(login_url="user:login")
def inbox(request):
    # Kullanıcının dahil olduğu tüm mesajlardan benzersiz diğer kullanıcıları bul
    received_messages = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    sent_messages = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    
    user_ids = set(list(received_messages) + list(sent_messages))
    users = User.objects.filter(id__in=user_ids).distinct()
    
    # Her kullanıcıyla olan son mesajı ve okunmamış mesaj sayısını bulabiliriz
    conversations = []
    for u in users:
        last_msg = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=u)) | 
            (Q(sender=u) & Q(receiver=request.user))
        ).order_by('-created_at').first()
        
        unread_count = Message.objects.filter(sender=u, receiver=request.user, is_read=False).count()
        
        conversations.append({
            'user': u,
            'last_message': last_msg,
            'unread_count': unread_count
        })
    
    # Son mesaja göre sırala
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else None, reverse=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        conv_data = []
        for c in conversations:
            conv_data.append({
                'user_id': c['user'].id,
                'username': c['user'].username,
                'avatar': c['user'].profile.image.url if hasattr(c['user'], 'profile') and c['user'].profile.image else '/media/default.jpg',
                'last_msg': c['last_message'].body[:30] if c['last_message'] else '',
                'unread': c['unread_count'],
                'time': c['last_message'].created_at.strftime("%H:%M") if c['last_message'] else '',
                'is_online': c['user'].profile.is_online
            })
        return JsonResponse({'conversations': conv_data})

    return render(request, 'user/inbox.html', {'conversations': conversations})

@login_required(login_url="user:login")
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            msg = Message.objects.create(sender=request.user, receiver=other_user, body=body)
            Notification.objects.create(
                user=other_user,
                sender=request.user,
                notification_type='message',
                text=f"{request.user.username} size bir mesaj gönderdi."
            )
            
            # WebSocket Broadcast
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{other_user.id}',
                {
                    'type': 'chat_message',
                    'sender_id': request.user.id
                }
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'body': msg.body, 'time': msg.created_at.strftime("%H:%M")})
            return redirect('user:chat_detail', user_id=user_id)

    messages_list = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) | 
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('created_at')
    
    unread_messages = messages_list.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)
    
    # Bildirimleri de okundu yap
    Notification.objects.filter(user=request.user, sender=other_user, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        msg_data = []
        for m in messages_list:
            msg_data.append({
                'sender': m.sender.username,
                'avatar': m.sender.profile.image.url if hasattr(m.sender, 'profile') and m.sender.profile.image else '/media/default.jpg',
                'body': m.body,
                'time': m.created_at.strftime("%H:%M"),
                'is_me': m.sender == request.user,
                'is_read': m.is_read
            })
        return JsonResponse({
            'messages': msg_data,
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'avatar': other_user.profile.image.url if hasattr(other_user, 'profile') and other_user.profile.image else '/media/default.jpg',
                'is_online': other_user.profile.is_online,
                'last_seen': other_user.profile.last_seen.strftime("%H:%M") if other_user.profile.last_seen else "Hiç görülmedi"
            }
        })

    return render(request, 'user/chat_detail.html', {
        'other_user': other_user,
        'messages_list': messages_list
    })


@login_required(login_url="user:login")
def notifications(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'unread_count': unread_count})
        
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/notifications.html', {
        'notifs': notifs,
        'unread_count': unread_count
    })

@login_required(login_url="user:login")
def notifications_api(request):
    from django.utils import timezone
    Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    last_notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    notif_data = []
    for n in last_notifs:
        notif_data.append({
            'text': n.text,
            'sender': n.sender.username if n.sender else "Sistem",
            'sender_id': n.sender.id if n.sender else None,
            'avatar': n.sender.profile.image.url if n.sender and hasattr(n.sender, 'profile') and n.sender.profile.image else '/media/default.jpg',
            'time': n.created_at.strftime("%H:%M"),
            'is_read': n.is_read
        })
        
    return JsonResponse({
        'unread_count': unread_count,
        'notifications': notif_data
    })

@login_required(login_url="user:login")
def messages_page(request):
    target_user_id = request.GET.get('user_id')
    target_user = None
    if target_user_id:
        try:
            from django.contrib.auth.models import User
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            pass
            
    return render(request, 'user/messages.html', {
        'target_user': target_user
    })