from django.apps import apps
from django.db import transaction

from rest_framework import serializers

from ..tags.serializers import TaggitSerializer
from apps.person.api.v1.profile.serializers import RetrieveProfileSerializer

Pain = apps.get_model('celebot', 'Pain')
Reaction = apps.get_model('celebot', 'Reaction')
Translate = apps.get_model('celebot', 'Translate')


class BasePainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pain
        fields = '__all__'


class BaseTranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translate
        fields = '__all__'


class TagListSerializerField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'name': value.name,
            'slug': value.slug
        }


class RetrieveTranslateSerializer(BaseTranslateSerializer):
    tags = TagListSerializerField(many=True, read_only=True)

    class Meta(BaseTranslateSerializer.Meta):
        fields = ('uuid', 'pain', 'locale', 'label', 'problem',
                  'solution', 'tags',)


class RetrievePainSerializer(BasePainSerializer):
    translates = RetrieveTranslateSerializer(many=True)
    user = serializers.UUIDField(source='user.uuid')
    user_hexid = serializers.CharField(source='user.hexid')
    profile = RetrieveProfileSerializer(source='user.profile')

    reaction_stat = serializers.SerializerMethodField(read_only=True)
    reaction_given = serializers.CharField(read_only=True)
    is_creator = serializers.BooleanField(read_only=True)

    class Meta(BasePainSerializer.Meta):
        fields = ('uuid', 'user', 'user_hexid', 'profile', 'translates',
                  'reaction_stat', 'reaction_given', 'is_creator',
                  'create_at',)

    def get_reaction_stat(self, instance):
        ret = {'total': getattr(instance, 'reaction_total', 0)}

        for r in Reaction.Identifiers:
            ret.update({r.value: getattr(instance, '%s_count' % r.value, 0)})

        sorted_ret = sorted(ret.items(), key=lambda x: x[1], reverse=True)
        return {x[0]: x[1] for x in sorted_ret}


class ListPainSerializer(RetrievePainSerializer):
    permalink = serializers.HyperlinkedIdentityField(
        view_name='celebot_api:pain-detail',
        lookup_field='uuid'
    )

    class Meta(RetrievePainSerializer.Meta):
        fields = ('profile', 'permalink',) + \
            RetrievePainSerializer.Meta.fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        default_translate = [
            x for x in ret.get('translates') if x.get('locale') == 'en_US'
        ]

        if len(default_translate) > 0:
            ret.update({
                'default_translate': default_translate[0]
            })

        return ret


class CreateTranslateSerializer(BaseTranslateSerializer):
    tags = serializers.ListField(allow_empty=True)

    class Meta(BaseTranslateSerializer.Meta):
        fields = ('locale', 'label', 'problem', 'solution', 'tags',)


class CreatePainSerializer(BasePainSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    translate = CreateTranslateSerializer(write_only=True)

    class Meta(BasePainSerializer.Meta):
        fields = ('user', 'translate',)

    def to_representation(self, instance):
        request = self.context.get('request')

        ret = {
            'is_creator': request.user.id == instance.user.id
        }

        serializer = RetrievePainSerializer(instance, context=self.context)
        ret.update(serializer.data)
        return ret

    @transaction.atomic
    def create(self, validated_data):
        translate = validated_data.pop('translate', None)
        instance = self.Meta.model.objects.create(**validated_data)

        if instance:
            tags = translate.pop('tags', None)
            translate_instance = Translate.objects.create(
                pain=instance,
                **translate
            )

            # add tags
            if tags:
                translate_instance.tags.add(*tags)
        return instance


class UpdatePainSerializer(BasePainSerializer):
    translate = CreateTranslateSerializer(write_only=True)

    class Meta(BasePainSerializer.Meta):
        fields = ('translate',)

    def to_representation(self, instance):
        serializer = RetrievePainSerializer(instance, context=self.context)
        return serializer.data

    @transaction.atomic
    def update(self, instance, validated_data):
        translate = validated_data.pop('translate', None)

        if translate:
            locale = translate.pop('locale')
            tags = translate.pop('tags', None)

            translate_instance, _created = Translate.objects.update_or_create(
                defaults={**translate},
                pain=instance,
                locale=locale
            )

            # set or remove tags
            if tags:
                translate_instance.tags.set(*tags)

        instance.refresh_from_db()
        return instance
