from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from .tokens import account_activation_token
from .forms import LoginForm, RegisterForm
from apps.users.models import PrismUser

class LoginView(View):
    template_name = "authentication/login.html"

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
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect(self.request.GET.get('next', "/"))
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
        response = redirect('authentication:login')
        response.delete_cookie(
            'prism_key'
        )
        return response

class SignUpView(CreateView):
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')
    form_class = RegisterForm

class SignUpView(View):
    template_name = 'authentication/register.html'

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            current_site = get_current_site(request)
            subject = 'Prism Account Verification'
            message = render_to_string('authentication/email/activation_code.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            try:
                user.email_user(subject, message)
                user.save()
                msg = "Please confirm your email address to complete the registration."
            except Exception as err:
                msg = "An email subsystem error has occurred. Please contact your administrator."
                print(f"Email error: {err}")

            context = {
                'form': form,
                'msg': msg
            }
        else:
            context = {
                'form': form
            }
        return render(request, self.template_name,  context)

class AccountActivateView(View):
    template_name= 'authentication/activation/invalid_code.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = PrismUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, PrismUser.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.profile.is_verified = True
            user.save()
            return redirect('accounts:login')
        else:
            return render(request, self.template_name)