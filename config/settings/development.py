from .project import *

# GMAIL SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'cli.exec.com@gmail.com'
EMAIL_HOST_PASSWORD = 'ind0nesi@'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# Django Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}


# Django Debug Toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/stable/installation.html

if DEBUG:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ('127.0.0.1', '10.0.2.2', 'localhost' '192.168.1.115',)
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS += (
        'debug_toolbar',
    )

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }
