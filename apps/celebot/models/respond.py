from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from .tag import TagItem
from .abstract import AbstractCommonField


class AbstractReaction(AbstractCommonField):
    class Identifiers(models.TextChoices):
        CELEBRATE = 'celebrate', _("Celebrate")
        SUPPORT = 'support', _("Support")
        FAVORITE = 'favorite', _("Favorite")
        INSIGHTFUL = 'insightful', _("Insightful")
        CURIOUS = 'curious', _("Curious")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reactions',
        on_delete=models.CASCADE
    )
    pain = models.ForeignKey(
        'celebot.Pain',
        related_name='reactions',
        on_delete=models.CASCADE
    )
    translate = models.ForeignKey(
        'celebot.Translate',
        related_name='reactions',
        on_delete=models.CASCADE
    )

    identifier = models.CharField(
        max_length=15,
        choices=Identifiers.choices,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z_]*$',
                message=_("Can only contain the letters a-z and underscores."),
                code='invalid_identifier'
            ),
        ]
    )

    class Meta:
        abstract = True
        app_label = 'celebot'
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")

    def __str__(self):
        return self.get_identifier_display()


class AbstractComment(AbstractCommonField):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )

    pain = models.ForeignKey(
        'celebot.Pain',
        related_name='comments',
        on_delete=models.CASCADE
    )

    translate = models.ForeignKey(
        'celebot.Translate',
        related_name='comments',
        on_delete=models.CASCADE
    )

    content = models.TextField()
    attachments = GenericRelation('celebot.Attachment')
    tags = TaggableManager(through=TagItem, blank=True)

    class Meta:
        abstract = True
        app_label = 'celebot'
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self) -> str:
        return self.content


class AbstractParentChildComment(AbstractCommonField):
    parent = models.ForeignKey(
        'celebot.Comment',
        related_name='parents',
        on_delete=models.CASCADE
    )

    child = models.ForeignKey(
        'celebot.Comment',
        related_name='childs',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        app_label = 'celebot'
        verbose_name = _("Parent Child Comment")
        verbose_name_plural = _("Parent Child Comments")

    def __str__(self) -> str:
        return '{} -> {}'.format(str(self.child.id), str(self.parent.id))
