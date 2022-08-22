from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.core.files.images import get_image_dimensions

from backports.zoneinfo import available_timezones

from .models import PrismProfile, PrismUser

from apps.crypto.forms import FernetField

class UserEditForm(UserChangeForm):
    password = None
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    class Meta:
        model = PrismUser
        fields = ('username', 'email')

class UserSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search",
                "class": "form-control",
            }
        )
    )

class ProfileEditForm(forms.ModelForm):
    timezone = forms.ChoiceField(
        required=False,
        choices=sorted(
            (i, i) for i in available_timezones()
        ),
        widget=forms.Select(
            attrs={
                "placeholder": "Timezone",
                "class": "form-control"
            }
        ))
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "placeholder": "Avatar",
                "class": "form-control"
            }
        ))
    class Meta:
        model = PrismProfile
        fields = ('timezone', 'avatar',)

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        if avatar:
            try:
                w, h = get_image_dimensions(avatar)

                #validate dimensions
                max_width = max_height = 500
                if w > max_width or h > max_height:
                    raise forms.ValidationError(
                        f'Please use an image that is {max_width} x {max_height} pixels or smaller.'
                        )

                #validate content type
                main, sub = avatar.content_type.split('/')
                if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                    raise forms.ValidationError(
                        'Please use a JPEG, GIF or PNG image.'
                        )

                #validate file size
                if len(avatar) > (200 * 1024):
                    raise forms.ValidationError(
                        'Avatar file size may not exceed 200k.'
                        )

            except AttributeError:
                """
                Handles case when we are updating the user profile
                and do not supply a new avatar
                """
                pass

            return avatar

class PasswordEditForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        fields = ('old_password', 'new_password1', 'new_password2',)

class PasswordResetForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    class Meta:
        fields = ('new_password1', 'new_password2',)


class EncryptionKeyForm(forms.Form):
    key = FernetField(
        label="Encryption Key",
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        ))