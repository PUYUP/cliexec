from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from ....helpers import build_result_pagination
from .serializers import CreateReactionSerializer, ListReactionSerializer, UpdateReactionSerializer

Reaction = apps.get_registered_model('celebot', 'Reaction')

# Define to avoid used ...().paginate__
_PAGINATOR = LimitOffsetPagination()


class BaseViewSet(viewsets.ViewSet):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.context = dict()

    def initialize_request(self, request, *args, **kwargs):
        self.context.update({'request': request})
        return super().initialize_request(request, *args, **kwargs)


class ReactionViewSet(BaseViewSet):
    """
    GET
    -----

        /reactions/?pain=<uuid64>&identifier=<string>


    POST
    -----

        {
            "pain": "uuid64",
            "translate": "uuid64",
            "identifier": "string"
        }


    PATCH
    -----

        {
            "identifier": "string"
        }
    """
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    throttle_classes = (UserRateThrottle,)

    def queryset(self):
        return Reaction.objects \
            .prefetch_related('user', 'user__profile', 'pain', 'translate') \
            .select_related('user', 'user__profile', 'pain', 'translate') \
            .all()

    def queryset_instance(self, uuid, for_update=False):
        try:
            if for_update:
                return self.queryset().select_for_update() \
                    .get(uuid=uuid, user_id=self.request.user.id)
            return self.queryset().get(uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound()

    @transaction.atomic
    def create(self, request, format=None):
        serializer = CreateReactionSerializer(
            data=request.data,
            context=self.context
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_201_CREATED)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    @transaction.atomic
    def partial_update(self, request, uuid=None, format=None):
        instance = self.queryset_instance(uuid, for_update=True)
        serializer = UpdateReactionSerializer(
            instance,
            data=request.data,
            context=self.context,
            partial=True
        )

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
            except DjangoValidationError as e:
                raise ValidationError(detail=str(e))
            return Response(serializer.data, status=response_status.HTTP_200_OK)
        return Response(serializer.errors, status=response_status.HTTP_406_NOT_ACCEPTABLE)

    def list(self, request, format=None):
        identifier = request.query_params.get('identifier', None)
        pain = request.query_params.get('pain', None)

        if not pain:
            raise ValidationError(
                detail={'pain': _("Pain parameter required")}
            )

        try:
            queryset = self.queryset().filter(pain__uuid=pain)
        except Exception as e:
            raise ValidationError(detail={'pain': str(e)})

        if identifier:
            queryset = queryset.filter(identifier=identifier)

        paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = ListReactionSerializer(
            paginator,
            context=self.context,
            many=True
        )

        results = build_result_pagination(self, _PAGINATOR, serializer)
        return Response(results, status=response_status.HTTP_200_OK)
