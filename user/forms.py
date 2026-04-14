from django import forms
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
     username=forms.CharField(label="Kullanıcı Adı")
     password=forms.CharField(label="Şifre",widget=forms.PasswordInput)

     

class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Adınız")
    last_name = forms.CharField(max_length=50, label="Soyadınız")
    email = forms.EmailField(label="E-posta Adresi") 
    
    username = forms.CharField(max_length=50, label="Kullanıcı Adı")
    password = forms.CharField(max_length=20, label="Parola", widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=20, label="Parolayı Doğrula", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanımda!")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış!")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm")

        if password and confirm and password != confirm:
            raise forms.ValidationError("Parolalar Eşleşmiyor")
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio', 'github', 'linkedin']