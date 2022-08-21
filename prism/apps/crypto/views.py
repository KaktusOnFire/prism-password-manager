from django.views import View
from django.views.generic.edit import DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from cryptography.fernet import InvalidToken

from backports.zoneinfo import ZoneInfo

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
                    el.date_created.astimezone(ZoneInfo(user.profile.timezone)),
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
        obj = get_object_or_404(self.model, pk=pk)
        is_err = False

        form = self.form(instance=obj)
        context = {
            "form": form,
            "object": self.object_type,
            "is_err": is_err
        }
        return render(request, self.template_name, context)


    def post(self, request, pk, *args, **kwargs):
        current_data = get_object_or_404(self.model, id=pk)
        encryption_key = get_encryption_key(request)
        if 'edit' in request.POST:
            form = self.form(data=request.POST, instance=current_data)
            if form.is_valid():
                obj = form.save(commit=False)
                if self.field_to_encrypt in form.changed_data:
                    if encryption_key:
                        secret_data = CryptoManager.encrypt(encryption_key, form.cleaned_data[self.field_to_encrypt])
                        setattr(obj, self.field_to_encrypt, secret_data)
                    else:
                        context = {
                            'form': form,
                            "object": self.object_type,
                            "is_err": True
                        }
                        return render(request, self.template_name, context)
                obj.save()
                return redirect('home')
            else:
                context = {
                    'form': form,
                    "object": self.object_type,
                    "is_err": False
                }
            return render(request, self.template_name, context)

        elif 'decrypt' in request.POST:
            if encryption_key:
                try:
                    secret_data = CryptoManager.decrypt(encryption_key, getattr(current_data, self.field_to_encrypt))
                    form = self.form(instance=current_data, initial={self.field_to_encrypt: secret_data})
                    is_err = False
                except InvalidToken:
                    form = self.form(instance=current_data)
                    is_err = True
            context = {
                'form': form,
                "object": self.object_type,
                "is_err": is_err
            }
            return render(request, self.template_name, context)

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
    object_type = 'SSH key pair'

#Edit Views
class EditPasswordView(TemplateEditView):
    form = PasswordForm
    model = EncryptedPassword
    field_to_encrypt = 'password'
    object_type = 'Password'

class EditSocialAccountView(TemplateEditView):
    form = SocialAccountForm
    model = EncryptedSocialAccount
    field_to_encrypt = 'password'
    object_type = 'Social Account'

class EditSSHKeypairView(TemplateEditView):
    form = SSHKeypairForm
    model = EncryptedSSHKeypair
    field_to_encrypt = 'private_key'
    object_type = 'SSH Key pair'

#Delete Views
class DeletePasswordView(TemplateDeleteView):
    model = EncryptedPassword

class DeleteSocialAccountView(TemplateDeleteView):
    model = EncryptedSocialAccount

class DeleteSSHKeypairView(TemplateDeleteView):
    model = EncryptedSSHKeypair