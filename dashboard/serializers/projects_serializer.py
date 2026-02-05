from rest_framework import serializers
from main.models import Projects, ProjectsTranslate, University, Country, LANGUAGE_CHOICES
from django.utils.text import slugify

def get_fallback_detail(qs, lang, default_lang="uz"):
    detail = qs.filter(language=lang).first() if lang else None
    if detail:
        return detail
    if default_lang and lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail
    return qs.first()

class ProjectsSerializer(serializers.ModelSerializer):
    # WRITE ONLY (majburiy translation fieldlar)
    title = serializers.CharField(write_only=True, required=True)
    topic = serializers.CharField(write_only=True, required=True)
    description = serializers.CharField(write_only=True, required=True)

    sponsor_university = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(),
        write_only=True,
        required=True
    )
    sponsor_country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        write_only=True,
        required=True
    )

    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = [
            'id',
            'start_date',
            'end_date',
            'image',
            'amount',
            'status',
            'sponsor_university',
            'sponsor_country',
            'title',
            'topic',
            'description',
            'translation_statuses'
        ]

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.translations.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()

        title = validated_data.pop('title')
        topic = validated_data.pop('topic')
        description = validated_data.pop('description')

        project = Projects.objects.create(**validated_data)

        ProjectsTranslate.objects.create(
            projects=project,
            language=lang,
            title=title,
            topic=topic,
            description=description,
            slug=slugify(title)
        )

        return project

    def update(self, instance, validated_data):
        lang = self.get_language()

        title = validated_data.pop('title', None)
        topic = validated_data.pop('topic', None)
        description = validated_data.pop('description', None)

        # Basic Projects fields update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if title or topic or description:
            existing = get_fallback_detail(instance.translations, lang)
            ProjectsTranslate.objects.update_or_create(
                projects=instance,
                language=lang,
                defaults={
                    'title': title or "",
                    'topic': topic or "",
                    'description': description or "",
                    'slug': slugify(title) if title else (existing.slug if existing else None)
                }
            )

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()

        # Translation
        detail = get_fallback_detail(instance.translations, lang)

        # University translation
        uni_detail = get_fallback_detail(instance.sponsor_university.details, lang) if hasattr(instance.sponsor_university, 'details') else None

        # Country translation
        country_detail = get_fallback_detail(instance.sponsor_country.details, lang) if hasattr(instance.sponsor_country, 'details') else None

        data = {
            "id": instance.id,
            "start_date": instance.start_date,
            "end_date": instance.end_date,
            "image": request.build_absolute_uri(instance.image.url) if request and instance.image else None,
            "amount": instance.amount,
            "status": instance.status,
            "translation_statuses": self.get_translation_statuses(instance),

            "sponsor_university": {
                "id": instance.sponsor_university.id,
                "name": uni_detail.name if uni_detail else None
            },

            "sponsor_country": {
                "id": instance.sponsor_country.id,
                "name": country_detail.name if country_detail else None
            }
        }

        if detail:
            data.update({
                "title": detail.title,
                "topic": detail.topic,
                "description": detail.description,
                "slug": detail.slug
            })
        else:
            data.update({
                "title": None,
                "topic": None,
                "description": None,
                "slug": None
            })

        return data

