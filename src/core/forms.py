from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, User


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "body", "publisher"]


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
