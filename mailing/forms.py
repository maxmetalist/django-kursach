from django import forms
from mailing.models import Client, Message, Mailing

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите тему письма'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Введите текст письма...'
            }),
        }
        labels = {
            'subject': 'Тема письма',
            'body': 'Тело письма',
        }
        help_texts = {
            'subject': 'Краткое и понятное название темы',
            'body': 'Основное содержание письма',
        }

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject and len(subject) < 5:
            raise forms.ValidationError("Тема письма должна содержать не менее 5 символов")
        return subject

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if body and len(body) < 10:
            raise forms.ValidationError("Тело письма должно содержать не менее 10 символов")
        return body


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'status', 'message', 'clients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
