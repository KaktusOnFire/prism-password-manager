from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
from django.views.generic import CreateView
from django.conf import settings
from django.urls import reverse_lazy

from apps.crypto.base import CryptoManager
from apps.authentication.forms import RegisterForm
from .mixins import StaffRequiredMixin
from .models import PrismUser
from .forms import EncryptionKeyForm, \
    PasswordResetForm, UserEditForm, \
    ProfileEditForm, UserSearchForm, \
    PasswordEditForm

import datetime
from backports.zoneinfo import ZoneInfo

class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

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
    template_name = 'users/password.html'

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
            return redirect('users:profile')
        context = {
            "form": form,
            "user": request.user,
            "profile": request.user.profile
        }
        return render(request, self.template_name, context)

class UsersView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'users/users.html'
    PAGINATE_BY = 10

    def get(self, request, *args, **kwargs):
        form = UserSearchForm()
        users_qs = PrismUser.objects.all().order_by("username")
        users = list()
        for el in users_qs:
            if el.last_login:
                users.append((
                    el.username,
                    el.last_login.astimezone(ZoneInfo(request.user.profile.timezone)),
                    el.date_joined.astimezone(ZoneInfo(request.user.profile.timezone)),
                    el.is_active,
                    el.get_absolute_url(),
                ))
            else:
                users.append((
                    el.username,
                    "-",
                    el.date_joined.astimezone(ZoneInfo(request.user.profile.timezone)),
                    el.is_active,
                    el.get_absolute_url(),
                ))

        page = request.GET.get('page', 1)
        paginator = Paginator(users, self.PAGINATE_BY)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        context = {
            "form": form,
            "users": data,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = UserSearchForm(request.POST)
        users = list()
        if form.is_valid():
            query = form.cleaned_data["query"]

            if query != "":
                users_qs = PrismUser.objects.filter(username__icontains=query).order_by("username")
            else:
                users_qs = PrismUser.objects.all().order_by("username")
            for el in users_qs:
                users.append((
                    el.username,
                    el.last_login.astimezone(ZoneInfo(request.user.profile.timezone)),
                    el.date_joined.astimezone(ZoneInfo(request.user.profile.timezone)),
                    el.is_active,
                    el.get_absolute_url(),
                ))


        page = request.GET.get('page', 1)
        paginator = Paginator(users, self.PAGINATE_BY)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)
        context = {
            "form": form,
            "users": data,
        }
        return render(request, self.template_name, context)

class CreateUserView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    template_name = 'users/create.html'
    form_class = RegisterForm
    success_url = reverse_lazy("users:manager")

class ResetUserView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = 'users/password_reset.html'

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(PrismUser, id=pk)
        if pk == request.user.pk:
            return redirect("users:manager")

        action = request.GET.get("action")
        if action:
            if action == "disable":
                user.is_active = False
                user.save()
            if action == "enable":
                user.is_active = True
                user.save()
            return redirect("users:manager")
        else:
            form = PasswordResetForm(user=user)
            context = {
                "form": form,
                "user": user
            }
            return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        user = get_object_or_404(PrismUser, id=pk)
        if pk == request.user.pk:
            return redirect("users:manager")

        form = PasswordResetForm(user=user, data=request.POST)
        if form.is_valid():
            password = form.cleaned_data["new_password1"]
            user.set_password(password)
            user.save()
            return redirect("users:manager")
        
        context = {
            "form": form,
            "user": user
        }
        return render(request, self.template_name, context)
        

class EncryptionKeyView(LoginRequiredMixin, View):
    template_name = "users/encryption_key.html"

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