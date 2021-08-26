# https://pypi.org/project/django-appconf/
from django.conf import settings  # noqa
from appconf import AppConf


class CelebotAppConf(AppConf):
    DEFAULT_LOCALE = 'en_US'

    class Meta:
        perefix = 'celebot'
