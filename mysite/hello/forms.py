from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MediaFile

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ('title', 'file')