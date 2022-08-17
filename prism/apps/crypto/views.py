from django.views import View
from django.views.generic.edit import DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from cryptography.fernet import InvalidToken

from backports.zoneinfo import available_timezones, ZoneInfo

from .models import EncryptedPassword, EncryptedSocialAccount, EncryptedSSHKeypair
from .base import CryptoManager, BaseEncryptedObject
from .forms import PasswordForm, SSHKeypairForm, SocialAccountForm

from apps.accounts.mixins import KeyCookieRequiredMixin

def get_encryption_key(request):
    try:
        signer = TimestampSigner()
        encryption_cookie = request.get_signed_cookie('prism_key', max_age=settings.ENCRYPTION_COOKIE_AGE)
        encryption_key = signer.unsign_object(encryption_cookie, max_age=settings.ENCRYPTION_COOKIE_AGE)
        return encryption_key
    except (KeyError, BadSignature, SignatureExpired):
        return None

class SecretsView(LoginRequiredMixin, View):
    template_name = 'crypto/home.html'
    
    def get(self, request, *args, **kwargs):
        user = request.user
        secrets = list()
        obj_classes = BaseEncryptedObject.__subclasses__()
        querysets = (el.objects.filter(owner=request.user) for el in obj_classes)
        for qs in querysets:
            for el in qs:
                secrets.append((
                    el.title,
                    el._meta.verbose_name,
                    el.date_created.astimezone(ZoneInfo(user.timezone)),
                    el.get_absolute_url(),
                    el.get_delete_url(),
                ))
        context = {
            "secrets": secrets
        }
        return render(request, self.template_name, context)

class TemplateCreateView(LoginRequiredMixin, KeyCookieRequiredMixin, View):
    template_name = 'crypto/create.html'
    form = None
    field_to_encrypt: str = None
    object_type: str = None        

    def get(self, request, *args, **kwargs):
        form = self.form()

        context = {
            "form": form,
            "object": self.object_type
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        form = self.form(request.POST or None)
        if form.is_valid():
            encryption_key = get_encryption_key(request)
            if encryption_key:
                obj = form.save(commit=False)
                secret_data = CryptoManager.encrypt(encryption_key, form.cleaned_data[self.field_to_encrypt])
                setattr(obj, self.field_to_encrypt, secret_data)
                obj.owner = request.user
                obj.save()
            return redirect('home')

        context = {
            "form": form
        }
        return render(request, self.template_name, context)

class TemplateEditView(LoginRequiredMixin, KeyCookieRequiredMixin, View):
    template_name = 'crypto/edit.html'
    form = None
    model = None
    field_to_encrypt: str = None
    object_type: str = None        

    def get(self, request, pk, *args, **kwargs):
        to_decrypt = request.GET.get("decrypted")
        obj = get_object_or_404(self.model, pk=pk)
        is_err = False
        if to_decrypt:
            encryption_key = get_encryption_key(request)
            if encryption_key:
                try:
                    secret_data = CryptoManager.decrypt(encryption_key, getattr(obj, self.field_to_encrypt))
                    setattr(obj, self.field_to_encrypt, secret_data)
                except InvalidToken:
                    is_err = True

        form = self.form(instance=obj)
        context = {
            "form": form,
            "object": self.object_type,
            "is_err": is_err
        }
        return render(request, self.template_name, context)


    # def post(self, request, *args, **kwargs):
    #     form = self.form(request.POST or None)
    #     if form.is_valid():
    #         encryption_key = get_encryption_key(request)
    #         if encryption_key:
    #             obj = form.save(commit=False)
    #             secret_data = CryptoManager.encrypt(encryption_key, form.cleaned_data[self.field_to_encrypt])
    #             setattr(obj, self.field_to_encrypt, secret_data)
    #             obj.owner = request.user
    #             obj.save()
    #         return redirect('home')

    #     context = {
    #         "form": form
    #     }
    #     return render(request, self.template_name, context)

class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "crypto/delete.html"
    success_url ="/"

#Create Views
class CreatePasswordView(TemplateCreateView):
    form = PasswordForm
    field_to_encrypt = 'password'
    object_type = 'password'

class CreateSocialAccountView(TemplateCreateView):
    form = SocialAccountForm
    field_to_encrypt = 'password'
    object_type = 'social account'

class CreateSSHKeypairView(TemplateCreateView):
    form = SSHKeypairForm
    field_to_encrypt = 'private_key'
    object_type = 'SSH keypair'

#Edit Views
class EditPasswordView(TemplateEditView):
    form = PasswordForm
    model = EncryptedPassword
    field_to_encrypt = 'password'
    object_type = 'password'

class EditSocialAccountView(TemplateEditView):
    form = SocialAccountForm
    model = EncryptedSocialAccount
    field_to_encrypt = 'password'
    object_type = 'social account'

class EditSSHKeypairView(TemplateEditView):
    form = SSHKeypairForm
    model = EncryptedSSHKeypair
    field_to_encrypt = 'private_key'
    object_type = 'SSH keypair'

#Delete Views
class DeletePasswordView(TemplateDeleteView):
    model = EncryptedPassword

class DeleteSocialAccountView(TemplateDeleteView):
    model = EncryptedSocialAccount

class DeleteSSHKeypairView(TemplateDeleteView):
    model = EncryptedSSHKeypair