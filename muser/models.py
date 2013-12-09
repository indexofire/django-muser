# -*- coding: utf-8 -*-
import re
from django.db import models
from django.conf import settings
from django.core import validators
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    BaseUserManager
from muser.extensions import ExtensionsMixin
from muser.settings import SOCIAL_CHOICES


class MuserManager(BaseUserManager):
    """Mars User manager class """
    def _create_user(self, email, username, password, is_staff, is_superuser,
                     **extra_fields):
        """Creates and saves a User with the given email and password."""
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          username=username,
                          is_staff=is_staff,
                          is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class Muser(AbstractBaseUser, PermissionsMixin, ExtensionsMixin):
    """
    Extensible User models.

    Put `AUTH_USER_MODEL = 'mars.apps.user.User'` in project's
    settings.py file. Then using profile extensions to extend
    user's profile. i.e:

    AUTH_USER_MODEL = 'mars.apps.user.User'
    AUTH_EXTENSIONS = (
        'mars.apps.user.extensions.avatar',
        'mars.apps.user.extensions.profile',
        ...
    )

    After you add or delete extensions in AUTH_EXTENSIONS, just
    running `south migrate` to update database schema.
    """
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Name you used in site. Required. 30 \n'
                    'characters or fewer. Letters, \n'
                    'numbers and @/./+/-/_ characters'),
        db_index=True,
        validators=[
            validators.RegexValidator(
                re.compile('^[\w.@+-]+$'),
                _('Enter a valid username.'),
                'invalid',
            )
        ],
    )
    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        db_index=True,
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this \n'
                    'admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated \n'
                    'as active. Unselect this instead of deleting \n'
                    'accounts.'),
    )
    date_joined = models.DateTimeField(
        _('sign up date'),
        default=timezone.now,
    )

    objects = MuserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        app_label = "user"
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class SocialApp(models.Model):
    provider = models.CharField(
        max_length=30,
        choices=SOCIAL_CHOICES,
    )
    name = models.CharField(
        max_length=40,
    )
    client_id = models.CharField(
        max_length=100,
        help_text='App ID, or consumer key',
    )
    key = models.CharField(
        max_length=100,
        blank=True,
        help_text='API Key',
    )
    secret = models.CharField(
        max_length=100,
        help_text='API secret, client secret, or consumer secret',
    )

    def __str__(self):
        return self.name


class SocialAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )
    provider = models.CharField(
        max_length=30,
        choices=SOCIAL_CHOICES,
    )
    # Just in case you're wondering if an OpenID identity URL is going
    # to fit in a 'uid':
    #
    # Ideally, URLField(max_length=1024, unique=True) would be used
    # for identity.  However, MySQL has a max_length limitation of 255
    # for URLField. How about models.TextField(unique=True) then?
    # Well, that won't work either for MySQL due to another bug[1]. So
    # the only way out would be to drop the unique constraint, or
    # switch to shorter identity URLs. Opted for the latter, as [2]
    # suggests that identity URLs are supposed to be short anyway, at
    # least for the old spec.
    #
    # [1] http://code.djangoproject.com/ticket/2495.
    # [2] http://openid.net/specs/openid-authentication-1_1.html#limits

    uid = models.CharField(
        max_length=255,
    )
    last_login = models.DateTimeField(
        auto_now=True,
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
    )
    extra_data = JSONField(
        default='{}',
    )

    class Meta:
        unique_together = ('provider', 'uid')

    def authenticate(self):
        return authenticate(account=self)

    def __unicode__(self):
        return self.user.nickname

    def get_profile_url(self):
        return self.user.get_absolute_url()

    def get_avatar_url(self):
        return self.user.avatar
