from django.db import models
from django.utils.translation import gettext_lazy as _

from taggit.models import GenericTaggedItemBase, TagBase
from simple_history.models import HistoricalRecords
from ..utils import locales


class Tag(TagBase):
    description = models.TextField(null=True, blank=True)
    locale = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        choices=locales()
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        app_label = 'celebot'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TagItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s"
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        app_label = 'celebot'
        verbose_name = _("Tag Item")
        verbose_name_plural = _("Tag Items")
