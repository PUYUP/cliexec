from django.apps import apps
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.expressions import Exists, Subquery

from rest_framework import serializers

from apps.person.api.v1.profile.serializers import RetrieveProfileSerializer

Pain = apps.get_registered_model('celebot', 'Pain')
Translate = apps.get_registered_model('celebot', 'Translate')
Reaction = apps.get_registered_model('celebot', 'Reaction')


class BaseReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'


class ListReactionSerializer(BaseReactionSerializer):
    user = serializers.CharField(source='user.uuid')
    pain = serializers.UUIDField(source='pain.uuid')
    profile = RetrieveProfileSerializer(source='user.profile')

    class Meta(BaseReactionSerializer.Meta):
        fields = ('uuid', 'user', 'profile', 'identifier',)


class RetrieveReactionSerializer(ListReactionSerializer):
    stat = serializers.SerializerMethodField()

    class Meta(ListReactionSerializer.Meta):
        fields = ('uuid', 'user', 'profile', 'translate',
                  'pain', 'identifier', 'create_at', 'stat',)

    def get_stat(self, instance):
        model = instance._meta.model
        counts = {
            x.value: Count(
                'id',
                filter=Q(identifier=x.value)
            ) for x in model.Identifiers
        }

        ret = model.objects \
            .filter(pain_id=instance.pain.id) \
            .aggregate(total=Count('identifier'), **counts)

        sorted_ret = sorted(ret.items(), key=lambda x: x[1], reverse=True)
        return {x[0]: x[1] for x in sorted_ret}


class CreateReactionSerializer(BaseReactionSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pain = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Pain.objects.all()
    )
    translate = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Translate.objects.all()
    )

    class Meta(BaseReactionSerializer.Meta):
        fields = ('user', 'pain', 'identifier', 'translate',)

    def to_representation(self, instance):
        serializer = RetrieveReactionSerializer(instance, context=self.context)
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        identifier = validated_data.pop('identifier', None)
        defaults = {'identifier': identifier}

        instance, _created = Reaction.objects.update_or_create(
            defaults=defaults,
            **validated_data
        )

        return instance


class UpdateReactionSerializer(BaseReactionSerializer):
    class Meta(BaseReactionSerializer.Meta):
        fields = ('identifier',)

    def to_representation(self, instance):
        serializer = RetrieveReactionSerializer(instance, context=self.context)
        return serializer.data

    @transaction.atomic
    def update(self, instance, validated_data):
        identifier = validated_data.pop('identifier', None)
        defaults = {'identifier': identifier}

        instance, _created = Reaction.objects.update_or_create(
            defaults=defaults,
            **validated_data
        )

        return instance
