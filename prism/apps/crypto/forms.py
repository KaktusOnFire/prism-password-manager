from django import forms
from django.forms import ModelForm, ValidationError
from .models import EncryptedPassword, EncryptedSocialAccount, EncryptedSSHKeypair
from cryptography.fernet import Fernet

class FernetField(forms.CharField):
    def __init__(self, *args, **kwargs):
        help_text = "Your encryption key will be pulled from temporary storage, but you can override it using this field."
        super().__init__(help_text=help_text, **kwargs)

    def validate(self, value):
        try:
            Fernet(value)
        except ValueError:
            raise ValidationError("Encryption key must be a base64-encoded 32-byte key.")
        super().validate(value)

class PasswordForm(ModelForm):
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    password = forms.CharField(
        label='Password',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = EncryptedPassword
        fields = ['title', 'password']

class SocialAccountForm(PasswordForm):
    login = forms.CharField(
        label='Login',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = EncryptedSocialAccount
        fields = ['title', 'login', 'password']

class SSHKeypairForm(ModelForm):
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        )
    )
    public_key = forms.CharField(
        label='Public Key',
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                
            }
        )
    )
    private_key = forms.CharField(
        label='Private Key',
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        model = EncryptedSSHKeypair
        fields = ['title', 'public_key', 'private_key']