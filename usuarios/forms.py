from django import forms

class ImageUploadForm(forms.Form):
    username = forms.CharField(max_length=150)
    senha = forms.CharField(widget=forms.PasswordInput())
    confirmar_senha = forms.CharField(widget=forms.PasswordInput())
    image = forms.ImageField()