from simple_history.models import HistoricalRecords

from .trouble import *
from .respond import *
from .media import *

from ..utils import is_model_registered

__all__ = list()


# 1
if not is_model_registered('celebot', 'Pain'):
    class Pain(AbstractPain):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractPain.Meta):
            pass

    __all__.append('Pain')


# 2
if not is_model_registered('celebot', 'Translate'):
    class Translate(AbstractTranslate):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractTranslate.Meta):
            pass

    __all__.append('Translate')


# 3
if not is_model_registered('celebot', 'Reaction'):
    class Reaction(AbstractReaction):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractReaction.Meta):
            pass

    __all__.append('Reaction')


# 4
if not is_model_registered('celebot', 'Comment'):
    class Comment(AbstractComment):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractComment.Meta):
            pass

    __all__.append('Comment')


# 5
if not is_model_registered('celebot', 'ParentChildComment'):
    class ParentChildComment(AbstractParentChildComment):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractParentChildComment.Meta):
            pass

    __all__.append('ParentChildComment')


# 6
if not is_model_registered('celebot', 'Attachment'):
    class Attachment(AbstractAttachment):
        history = HistoricalRecords(inherit=True)

        class Meta(AbstractAttachment.Meta):
            pass

    __all__.append('Attachment')
