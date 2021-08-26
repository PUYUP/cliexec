from django.urls import path, include
from apps.celebot.api.v1 import routers

urlpatterns = [
    path('celebot/v1/', include((routers, 'celebot_api'), namespace='celebot_api')),
]
