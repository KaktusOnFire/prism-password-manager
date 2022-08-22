from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
from django.views import View
from django.conf import settings
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm

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