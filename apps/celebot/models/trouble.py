from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from .abstract import AbstractCommonField
from .tag import TagItem
from ..locales import LocaleChoices
from ..conf import settings


class AbstractPain(AbstractCommonField):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='pains',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        app_label = 'celebot'
        verbose_name = _("Pain")
        verbose_name_plural = _("Pains")
        ordering = ('-create_at',)

    def __str__(self):
        return self.user.name

    @property
    def default_translate(self):
        try:
            return self.translates.get(locale=settings.CELEBOT_DEFAULT_LOCALE)
        except ObjectDoesNotExist:
            return None


class AbstractTranslate(AbstractCommonField):
    pain = models.ForeignKey(
        'celebot.Pain',
        related_name='translates',
        on_delete=models.CASCADE
    )

    locale = models.CharField(
        max_length=15,
        choices=LocaleChoices.choices,
        default=LocaleChoices.en_US,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z_]*$',
                message=_("Can only contain the letters a-z and underscores."),
                code='invalid_identifier'
            ),
        ]
    )
    label = models.CharField(max_length=255, blank=True, null=True)
    problem = models.TextField()
    solution = models.TextField()

    attachments = GenericRelation('celebot.Attachment')
    tags = TaggableManager(through=TagItem, blank=True)

    class Meta:
        abstract = True
        app_label = 'celebot'
        verbose_name = _("Translate")
        verbose_name_plural = _("Translates")

    def __str__(self):
        return self.label or self.problem
