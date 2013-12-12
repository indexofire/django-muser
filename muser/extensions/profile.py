# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from muser.extensions import Extension


class Extension(Extension):
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
        (3, _('Unknown')),
    )

    def handle_model(self):
        self.model.add_to_class(
            'gender',
            models.PositiveSmallIntegerField(
                _('Gender'),
                blank=True,
                default=3,
                choices=self.GENDER_CHOICES,
            )
        )
        self.add_to_class(
            'birthday',
            models.DateField(
                _('Birthday'),
                blank=True,
                null=True,
            )
        )
        # field for user's telephone number
        self.add_to_class(
            'telephone',
            models.CharField(
                _("Telephone Number"),
                blank=True,
                max_length=25,
            )
        )

    def handle_modeladmin(self, modeladmin):
        modeladmin.add_extension_options(_('Profile'), {
            'fields': ('gender', 'birthday', 'telephone',),
            'classes': ('collapse', ), },
        )
