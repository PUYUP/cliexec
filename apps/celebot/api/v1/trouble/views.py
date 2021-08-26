from copy import copy

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist, ValidationError as DjangoValidationError
from django.db.models.expressions import Exists, OuterRef, Subquery, Value
from django.db.models.fields import CharField

from rest_framework import viewsets, status as response_status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from ....helpers import build_result_pagination
from .serializers import CreatePainSerializer, ListPainSerializer, RetrievePainSerializer, UpdatePainSerializer

Pain = apps.get_registered_model('celebot', 'Pain')
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


class PainViewSet(BaseViewSet):
    """
    GET
    -----
        ../troubles/?user_hexid=<string>&tags=my,hero,tags


    POST
    -----
        {
            "translate": {
                "locale": "en_US",
                "label": "Joke word",
                "problem": "My problem X",
                "solution": "My solution X",
                "tags": ["abc", "def", "ghi"]
            }
        }
    """
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    throttle_classes = (UserRateThrottle,)

    def queryset(self):
        pain_subquery = Pain.objects \
            .filter(id=OuterRef('id'), user__id=self.request.user.id)

        reaction_subquery = Reaction.objects \
            .filter(pain__id=OuterRef('id'), user__id=self.request.user.id)

        reaction_stat = {'%s_count' % x.value: Count(
            'reactions',
            filter=Q(reactions__identifier=x.value),
            distinct=True
        ) for x in Reaction.Identifiers}

        return Pain.objects \
            .prefetch_related(
                'user',
                'user__profile',
                'translates',
                'translates__tags',
                'reactions'
            ) \
            .select_related('user', 'user__profile') \
            .annotate(
                is_creator=Exists(pain_subquery),
                reaction_total=Count('reactions', distinct=True),
                reaction_given=Subquery(
                    reaction_subquery.values('identifier')[:1]
                ),
                **reaction_stat,
            ) \
            .order_by('-create_at')

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
        serializer = CreatePainSerializer(
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
        serializer = UpdatePainSerializer(
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
        queryset = self.queryset()

        user_hexid = request.query_params.get('user_hexid', None)
        tags = request.query_params.get('tags', None)

        if user_hexid:
            queryset = queryset.filter(user__hexid=user_hexid)

        if tags:
            tags_list = tags.split(',')
            queryset = queryset.filter(translates__tags__name__in=tags_list)

        paginator = _PAGINATOR.paginate_queryset(queryset, request)
        serializer = ListPainSerializer(
            paginator,
            context=self.context,
            many=True
        )

        results = build_result_pagination(self, _PAGINATOR, serializer)
        return Response(results, status=response_status.HTTP_200_OK)

    @transaction.atomic()
    def delete(self, request, uuid=None):
        try:
            instance = self.queryset() \
                .get(uuid=uuid, user_id=request.user.id)
        except ObjectDoesNotExist:
            raise NotFound()

        # copy for response
        instance_copy = copy(instance)

        # run delete
        instance.delete()

        # return object
        serializer = RetrievePainSerializer(
            instance_copy,
            context=self.context
        )
        return Response(serializer.data, status=response_status.HTTP_200_OK)

    def retrieve(self, request, uuid=None, format=None):
        instance = self.queryset_instance(uuid)
        serializer = RetrievePainSerializer(instance, context=self.context)
        return Response(serializer.data, status=response_status.HTTP_200_OK)
