from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import AccessMixin
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse

from cryptography.fernet import Fernet

class KeyCookieRequiredMixin(AccessMixin):
    """Verify that the current user has a valid prism_key cookie"""

    def dispatch(self, request, *args, **kwargs):
        signer = TimestampSigner()
        try:
            encryption_cookie = request.get_signed_cookie('prism_key', max_age=settings.ENCRYPTION_COOKIE_AGE)
            encryption_key = signer.unsign_object(encryption_cookie, max_age=settings.ENCRYPTION_COOKIE_AGE)
            Fernet(encryption_key)
        except (KeyError, ValueError, BadSignature, SignatureExpired):
            path = self.request.get_full_path()
            key_update_url = reverse('users:key')
            return redirect_to_login(
                path,
                key_update_url,
                self.redirect_field_name
            )
        return super().dispatch(request, *args, **kwargs)

class StaffRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)