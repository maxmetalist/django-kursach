from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from users.models import Profile


class UserRegisterForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

class ProfileUpdateForm(forms.ModelForm):
    """Форма для редактирования профиля (например, менеджером)"""
    class Meta:
        model = Profile
        fields = ['is_blocked']
        labels = {
            'is_blocked': 'Заблокировать пользователя'
        }
