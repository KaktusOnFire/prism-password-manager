from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

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
    is_active = models.BooleanField(_('account status'), default=True)
    is_confirmed = models.BooleanField(_('email confirmed'), default=False)
    timezone = models.CharField(_('timezone'), max_length=100, default="UTC")
    avatar = models.ImageField(upload_to=PathAndRename('avatars/'), null=True, blank=True)

    def __str__(self):
        return self.username

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