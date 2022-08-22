from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views import View
from django.conf import settings
from django.urls import reverse_lazy

from apps.crypto.base import CryptoManager
from .forms import EncryptionKeyForm, LoginForm, PasswordEditForm, UserEditForm, ProfileEditForm, RegisterForm

import datetime

class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        context = {
            'form': form,
            'registration': settings.REGISTRATION_ENABLED
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        msg = None
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data.get("remember_me")
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:   
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)
                    return redirect(self.request.GET.get('next', "/"))
                else:
                    msg = 'Account is disabled'
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'
        context = {
            'form': form,
            'msg': msg,
            'registration': settings.REGISTRATION_ENABLED
        }
        return render(request, self.template_name, context)

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        response = redirect('accounts:login')
        response.delete_cookie(
            'prism_key'
        )
        return response

class SignUpView(CreateView):
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    form_class = RegisterForm

class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "user": request.user,
            "profile": request.user.profile
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "user": request.user,
            "profile": request.user.profile
        }
        return render(request, self.template_name, context)

class PasswordView(LoginRequiredMixin, View):
    template_name = 'accounts/password.html'

    def get(self, request, *args, **kwargs):
        form = PasswordEditForm(request.user)
        context = {
            "form": form,
            "user": request.user,
            "profile": request.user.profile
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = PasswordEditForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('accounts:profile')
        context = {
            "form": form,
            "user": request.user,
            "profile": request.user.profile
        }
        return render(request, self.template_name, context)

class EncryptionKeyView(LoginRequiredMixin, View):
    template_name = "accounts/encryption_key.html"

    def get(self, request, *args, **kwargs):
        signer = TimestampSigner()
        try:
            encryption_cookie = request.get_signed_cookie('prism_key', max_age=settings.ENCRYPTION_COOKIE_AGE)
            encryption_key = signer.unsign_object(encryption_cookie, max_age=settings.ENCRYPTION_COOKIE_AGE)
            err = False
            form = EncryptionKeyForm(initial={"key": encryption_key})
        except (KeyError, BadSignature, SignatureExpired):
            form = EncryptionKeyForm()
            encryption_key = None
            err = True

        context = {
            'form': form,
            'key': encryption_key,
            'is_err': err
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'generate' in request.POST:
            key = CryptoManager.create_pkey().decode("utf-8")
            form = EncryptionKeyForm(initial={"key": key})
            context = {
                'form': form,
                'key': key,
                'is_err': False
            }
            response = render(request, self.template_name, context)

                
            signer = TimestampSigner()
            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.ENCRYPTION_COOKIE_AGE),
                "%a, %d-%b-%Y %H:%M:%S GMT",
            )
            response.set_signed_cookie(
                "prism_key",
                signer.sign_object(key, compress=True),
                max_age=settings.ENCRYPTION_COOKIE_AGE,
                expires=expires,
                httponly=True,
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE or None,
            )

            return response

        elif 'update' in request.POST:
            form = EncryptionKeyForm(request.POST)
            if form.is_valid():
                blurred_key = form.cleaned_data['key']
                context = {
                    'form': form,
                    'key': blurred_key
                }

                if self.request.GET.get('next'):
                    response = redirect(self.request.GET.get('next'))
                else:
                    response = render(request, self.template_name, context)

                
                signer = TimestampSigner()
                expires = datetime.datetime.strftime(
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.ENCRYPTION_COOKIE_AGE),
                    "%a, %d-%b-%Y %H:%M:%S GMT",
                )
                response.set_signed_cookie(
                    "prism_key",
                    signer.sign_object(form.cleaned_data['key'], compress=True),
                    max_age=settings.ENCRYPTION_COOKIE_AGE,
                    expires=expires,
                    httponly=True,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    secure=settings.SESSION_COOKIE_SECURE or None,
                )

                return response
            else:
                context ={
                    'form': form,
                }

            return render(request, self.template_name, context)