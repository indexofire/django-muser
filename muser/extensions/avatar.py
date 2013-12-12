# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from muser.extensions import Extension
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


AVATAR_UPLOAD_TO = getattr(settings, 'AVATAR_UPLOAD_TO',
                           '%savatars/' % settings.MEDIA_URL)
AVATAR_RESIZE_WIDTH = getattr(settings, 'AVATAR_RESIZE_WIDTH', 80)
AVATAR_RESIZE_HEIGHT = getattr(settings, 'AVATAR_RESIZE_HEIGHT', 80)
AVATAR_RESIZE_QUALITY = getattr(settings, 'AVATAR_RESIZE_QUALITY', 70)


class Extension(Extension):
    """
    GauthAvatarExtension handle user's avatar into site.
    """
    def handle_model(self):
        self.model.add_to_class(
            'avatar',
            ProcessedImageField(
                upload_to=AVATAR_UPLOAD_TO,
                default='%sdefault.png' % AVATAR_UPLOAD_TO,
                processors=[ResizeToFill(AVATAR_RESIZE_WIDTH,
                                         AVATAR_RESIZE_HEIGHT)],
                format='JPEG',
                options={'quality': AVATAR_RESIZE_QUALITY},
            )
        )

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options(_('Avatar Pictures'), {
            'fields': ('avatar', ),
            'classes': ('collapse', ), },
        )
