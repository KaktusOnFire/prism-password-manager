from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterForm
from .models import PrismUser, PrismProfile

class PrismUserAdmin(UserAdmin):
    add_form = RegisterForm
    model = PrismUser
    list_display = ['username', 'email',]

admin.site.register(PrismUser, PrismUserAdmin)
admin.site.register(PrismProfile)