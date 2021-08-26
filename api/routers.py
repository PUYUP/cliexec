from django.urls import path, include

from api.views import RootAPIView
from apps.person.api import routers as person_routers
from apps.celebot.api import routers as celebot_routers

urlpatterns = [
    path('', RootAPIView.as_view(), name='api'),
    path('', include(person_routers)),
    path('', include(celebot_routers)),
]
