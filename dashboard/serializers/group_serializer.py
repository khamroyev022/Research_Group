from rest_framework import serializers
from main.models import Group, GroupDetail, Direction, LANGUAGE_CHOICES
from .direction_serializer import DirectionDetailSerializer


def get_active_fallback_detail(qs, lang, default_lang="uz"):
    model = qs.model

    has_is_active = any(f.name == "is_active" for f in model._meta.fields)
    qs_active = qs.filter(is_active=True) if has_is_active else qs

    if lang:
        d = qs_active.filter(language=lang).first()
        if d:
            return d

    if default_lang and lang != default_lang:
        d = qs_active.filter(language=default_lang).first()
        if d:
            return d

    return qs_active.first() or qs.first()


class GroupDetailSerialzier(serializers.ModelSerializer):
    class Meta:
        model = GroupDetail
        fields = ["id", "name", "description", "slug", "language", "is_active"]


class GroupSerializer(serializers.ModelSerializer):
    # WRITE
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)

    direction = serializers.PrimaryKeyRelatedField(
        queryset=Direction.objects.all(),
        write_only=True,
        required=False
    )

    translation_statuses = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Group
        fields = [
            "id",
            "image",
            "is_active",
            "direction",
            "translation_statuses",
            "name",
            "description",
        ]

    def get_language(self):
        # ViewSet'da context['language'] berilsa ishlaydi,
        # aks holda request headerdan ham olamiz (xavfsizroq)
        request = self.context.get("request")
        if request:
            return request.headers.get("Accept-Language", self.context.get("language", "uz"))
        return self.context.get("language", "uz")

    def get_translation_statuses(self, obj):
        # ✅ obj.details (related_name='details')
        active_langs = obj.details.filter(is_active=True).values_list("language", flat=True)
        return [
            {"code": code, "is_active": code in active_langs}
            for code, _ in LANGUAGE_CHOICES
        ]

    def create(self, validated_data):
        lang = self.get_language()

        name = validated_data.pop("name", None)
        description = validated_data.pop("description", "")
        direction = validated_data.pop("direction", None)
        image = validated_data.pop("image", None)

        if direction is None:
            raise serializers.ValidationError({"direction": "direction majburiy"})

        if not name:
            raise serializers.ValidationError({"name": "name majburiy"})

        group = Group.objects.create(
            image=image,
            direction=direction,
        )

        GroupDetail.objects.create(
            group=group,
            language=lang,
            name=name,
            description=description,
            is_active=True
        )

        return group

    def update(self, instance, validated_data):
        lang = self.get_language()

        name = validated_data.pop("name", None)
        description = validated_data.pop("description", None)
        image = validated_data.pop("image", None)
        direction = validated_data.pop("direction", None)

        changed_group = False

        if image is not None:
            instance.image = image
            changed_group = True

        if direction is not None:
            instance.direction = direction
            changed_group = True

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]
            changed_group = True

        if changed_group:
            instance.save()

        # Detailga tegilmasa, shu yerda chiqib ketadi
        if name is None and description is None:
            return instance

        detail = GroupDetail.objects.filter(group=instance, language=lang).first()

        if not detail:
            GroupDetail.objects.create(
                group=instance,
                language=lang,
                name=name or "",
                description=description or "",
                is_active=True
            )
            return instance

        if name is not None:
            detail.name = name
        if description is not None:
            detail.description = description

        if not detail.is_active:
            detail.is_active = True

        detail.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")

        image_url = None
        if instance.image and instance.image.name:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        lang = self.get_language()

        # ✅ instance.details (related_name='details')
        detail = get_active_fallback_detail(instance.details.all(), lang)

        data = {
            "id": str(instance.id),
            "image": image_url,
            "is_active": instance.is_active,
            "translation_statuses": self.get_translation_statuses(instance),

            "name": detail.name if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None,

            "direction": None
        }

        if instance.direction:
            # DirectionDetail related_name='details' ekan
            direction_detail = get_active_fallback_detail(instance.direction.details.all(), lang)
            data["direction"] = (
                DirectionDetailSerializer(direction_detail, context={"request": request}).data
                if direction_detail else {"id": str(instance.direction.id)}
            )

        return data
