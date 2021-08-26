from django.utils.translation import gettext_lazy as _

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RootAPIView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AnonRateThrottle, UserRateThrottle,)

    def get(self, request, format=None):
        return Response({
            'person': {
                'securecode': reverse('person_api:securecode-list', request=request,
                                      format=format, current_app='person'),
                'user': reverse('person_api:user-list', request=request,
                                format=format, current_app='person'),
                'password-recovery': reverse('person_api:password-recovery', request=request,
                                             format=format, current_app='person'),
            },
            'celebot': {
                'pain': reverse('celebot_api:pain-list', request=request,
                                format=format, current_app='celebot'),
                'reaction': reverse('celebot_api:reaction-list', request=request,
                                    format=format, current_app='celebot'),
            },
        })
