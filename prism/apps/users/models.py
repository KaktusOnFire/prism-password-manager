from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

import uuid
import os

@deconstructible
class PathAndRename():
    """
    Class for renaming users avatar images
    """
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        return os.path.join(self.path, filename)

class PrismUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:edit', kwargs={'pk' : self.pk})

    def get_delete_url(self):
        return reverse('users:delete', kwargs={'pk' : self.pk})

class PrismProfile(models.Model):
    user = models.OneToOneField(PrismUser, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    is_verified = models.BooleanField(_('email confirmed'), default=False)
    timezone = models.CharField(_('timezone'), max_length=100, default="UTC")
    avatar = models.ImageField(_('avatar'), upload_to=PathAndRename('avatars/'), null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

@receiver(post_save, sender=PrismUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        PrismProfile.objects.create(user=instance)
    instance.profile.save()


# @receiver(post_save, sender=PrismUser)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()


# class GroupUserPermission(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(PrismUser, on_delete=models.CASCADE)
#     read = models.BooleanField(default=True)
#     write = models.BooleanField(default=False)
#     admin = models.BooleanField(default=False)

#     def __str__(self):
#         return str(self.id)

# class PrismGroup(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     permissions = models.ManyToManyField(GroupUserPermission)

#     def __str__(self):
#         return str(self.id)