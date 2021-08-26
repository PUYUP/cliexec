import pycountry

from django.apps import apps
from django.utils.translation import gettext_lazy as _


def is_model_registered(app_label, model_name):
    """
    Checks whether a given model is registered. This is used to only
    register Oscar models if they aren't overridden by a forked app.
    """
    try:
        apps.get_registered_model(app_label, model_name)
    except LookupError:
        return False
    else:
        return True


def locales():
    """List languange by countries"""
    langs = list()
    countries = [country.alpha_2 for country in pycountry.countries]

    for code in countries:
        lang = pycountry.languages.get(alpha_2=code)
        name = getattr(lang, 'name', None)

        if name is not None:
            langs.append((code, _(name)))

    return langs
