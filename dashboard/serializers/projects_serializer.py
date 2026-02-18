from rest_framework import serializers
from django.utils.text import slugify

from main.models import (
    Projects, ProjectsTranslate,
    University, Country, Group,
    LANGUAGE_CHOICES
)


def get_fallback_detail(qs, lang, default_lang="uz"):
    detail = qs.filter(language=lang).first() if lang else None
    if detail:
        return detail
    if default_lang and lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail
    return qs.first()


def build_unique_slug(model, base_text, slug_field="slug"):
    base = slugify(base_text) if base_text else "item"
    count = model.objects.filter(**{f"{slug_field}__startswith": base}).count()
    return f"{base}-{count+1}" if count else base


class ProjectsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    topic = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    sponsor_university = serializers.PrimaryKeyRelatedField(queryset=University.objects.all(), required=True)
    sponsor_country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), required=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), required=False, allow_null=True)
    group_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    translation_statuses = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Projects
        fields = [
            "id",
            "start_date",
            "end_date",
            "image",
            "amount",
            "status",

            "group",
            "group_id",
            "sponsor_university",
            "sponsor_country",
            "title",
            "topic",
            "description",
            "translation_statuses",
        ]

    def get_language(self):
        lang = self.context.get("language")
        if not lang:
            request = self.context.get("request")
            lang = request.headers.get("Accept-Language", "uz") if request else "uz"
        return (lang or "uz").strip().lower()

    def get_translation_statuses(self, obj):
        active_langs = set(obj.translations.values_list("language", flat=True))
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def validate(self, attrs):
        if self.instance is None:
            for f in ("title", "topic", "description"):
                val = attrs.get(f)
                if val is None or str(val).strip() == "":
                    raise serializers.ValidationError({f: f"{f} majburiy"})
        return attrs

    def _apply_group_inputs(self, validated_data):
        grp = validated_data.get("group", None)
        gid = validated_data.pop("group_id", None)
        if grp is None and gid:
            validated_data["group_id"] = gid

        return validated_data

    def create(self, validated_data):
        lang = self.get_language()

        title = (validated_data.pop("title") or "").strip()
        topic = (validated_data.pop("topic") or "").strip()
        description = (validated_data.pop("description") or "").strip()

        validated_data = self._apply_group_inputs(validated_data)

        project = Projects.objects.create(**validated_data)

        unique_slug = build_unique_slug(ProjectsTranslate, title)
        ProjectsTranslate.objects.create(
            projects=project,
            language=lang,
            title=title,
            topic=topic,
            description=description,
            slug=unique_slug,
        )
        return project

    def update(self, instance, validated_data):
        lang = self.get_language()

        # translate fieldlar (PATCH’da kelishi mumkin)
        title = validated_data.pop("title", None)
        topic = validated_data.pop("topic", None)
        description = validated_data.pop("description", None)

        validated_data = self._apply_group_inputs(validated_data)

        # basic fields update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # translate update (faqat kelganlari)
        if title is not None or topic is not None or description is not None:
            tr, _ = ProjectsTranslate.objects.get_or_create(projects=instance, language=lang)

            if title is not None:
                title_clean = title.strip()
                tr.title = title_clean
                tr.slug = build_unique_slug(ProjectsTranslate, title_clean)

            if topic is not None:
                tr.topic = topic

            if description is not None:
                tr.description = description

            tr.save()

        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        lang = self.get_language()

        detail = get_fallback_detail(instance.translations, lang)
        uni_detail = get_fallback_detail(instance.sponsor_university.details,
                                         lang) if instance.sponsor_university_id else None
        country_detail = get_fallback_detail(instance.sponsor_country.details,
                                             lang) if instance.sponsor_country_id else None
        group_detail = get_fallback_detail(instance.group.details, lang) if instance.group_id else None  # ✅ yangi qator

        data = {
            "id": str(instance.id),
            "start_date": instance.start_date,
            "end_date": instance.end_date,
            "image": request.build_absolute_uri(instance.image.url) if request and instance.image else None,
            "amount": str(instance.amount) if instance.amount is not None else None,
            "status": instance.status,

            "group": {
                "id": str(instance.group_id) if instance.group_id else None,
                "name": group_detail.name if group_detail else None,
            },

            "translation_statuses": self.get_translation_statuses(instance),
            "sponsor_university": {
                "id": str(instance.sponsor_university_id) if instance.sponsor_university_id else None,
                "name": uni_detail.name if uni_detail else None,
            },
            "sponsor_country": {
                "id": str(instance.sponsor_country_id) if instance.sponsor_country_id else None,
                "name": country_detail.name if country_detail else None,
            },
        }
        if detail:
            data.update({
                "title": detail.title,
                "topic": detail.topic,
                "description": detail.description,
                "slug": detail.slug,
            })
        else:
            data.update({"title": None, "topic": None, "description": None, "slug": None})

        return data
