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