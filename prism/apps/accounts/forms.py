from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import PrismUser

from apps.crypto.forms import FernetField

class PrismUserCreationForm(UserCreationForm):
    class Meta:
        model = PrismUser
        fields = ('username', 'email')

class PrismUserChangeForm(UserChangeForm):
    class Meta:
        model = PrismUser
        fields = ('username', 'email')

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "Remember Me",
                "class": "form-check-input"
            }
        )
    )

class EncryptionKeyForm(forms.Form):
    key = FernetField(
        label="Encryption Key",
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        ))