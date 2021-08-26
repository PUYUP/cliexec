from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .trouble.views import PainViewSet
from .reaction.views import ReactionViewSet

router = DefaultRouter(trailing_slash=True)
router.register('pains', PainViewSet, basename='pain')
router.register('reactions', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('', include(router.urls)),
]
