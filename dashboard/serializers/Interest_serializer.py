from rest_framework import serializers
from main.models import Interests, InterestDetail, Group, LANGUAGE_CHOICES

def get_fallback_detail(qs, lang, default_lang="uz"):
    detail = qs.filter(language=lang).first() if lang else None
    if detail:
        return detail
    if default_lang and lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail
    return qs.first()


class InterestsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=True)
    description = serializers.CharField(write_only=True, required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Interests
        fields = ['id', 'group', 'created', 'name', 'description', 'translation_statuses']

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation_statuses(self, obj):
        active_langs = set(obj.interests.values_list('language', flat=True))
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def create(self, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name')
        description = validated_data.pop('description')
        group = validated_data['group']

        if Interests.objects.filter(group=group).exists():
            raise serializers.ValidationError({'group': 'Bu gruppada interest mavjud'})

        interests = Interests.objects.create(**validated_data)

        InterestDetail.objects.create(
            interests=interests,
            language=lang,
            name=name,
            description=description
        )
        return interests

    def update(self, instance, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name', None)
        description = validated_data.pop('description', None)

        if 'group' in validated_data:
            instance.group = validated_data['group']
            instance.save(update_fields=['group'])

        if name is not None or description is not None:
            InterestDetail.objects.update_or_create(
                interests=instance,
                language=lang,
                defaults={
                    'name': name if name is not None else "",
                    'description': description if description is not None else ""
                }
            )
        return instance

    def to_representation(self, instance):
        lang = self.get_language()
        detail = get_fallback_detail(instance.interests.all(), lang)

        data = {
            "id": str(instance.id),
            "group": str(instance.group_id),
            "created": instance.created,
            "translation_statuses": self.get_translation_statuses(instance),
        }

        if detail:
            data.update({
                "name": detail.name,
                "description": detail.description,
                "slug": detail.slug
            })
        else:
            data.update({
                "name": None,
                "description": None,
                "slug": None
            })

        return data
