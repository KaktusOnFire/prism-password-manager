from django import forms

from apps.crypto.forms import FernetField

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
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Encryption Key",
                "class": "form-control"
            }
        ))