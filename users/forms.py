from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Ім'я користувача", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': "Ім'я користувача",
            'email': 'Email',

        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Отключить подсказки для всех полей формы
    #     for fieldname in ['username', 'password1', 'password2']:
    #         self.fields[fieldname].help_text = None

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Підтвердження паролю'
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': "Ім'я користувача",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Отключить подсказки для всех полей формы
        for fieldname in ['username']:
            self.fields[fieldname].help_text = None


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
        labels = {
            'image': "Фото",
        }
