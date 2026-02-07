from rest_framework import serializers
from main.models import Direction, DirectionDetail,Country,University,CountryDetail,UniversityDetail
from main.models import LANGUAGE_CHOICES

def get_language(self):
    return self.context.get('language', 'uz')

def get_fallback_detail(qs, lang, default_lang="uz"):
    detail = qs.filter(language=lang).first() if lang else None
    if detail:
        return detail
    if default_lang and lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail
    return qs.first()


class DirectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectionDetail
        fields = ['id', 'name', 'description', 'slug']

class DirectionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ['id', 'image', 'name', 'description', 'translation_statuses']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.details.filter(direction__is_active=True).values_list('language', flat=True)
        
        return [
            {
                "code": code,
                "is_active": True
            }
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name')
        description = validated_data.pop('description')
        image = validated_data.get('image', None)

        direction = Direction.objects.create(**validated_data)

        DirectionDetail.objects.create(
            direction=direction,
            language=lang,
            name=name,
            description=description
        )

        return direction

    def update(self, instance, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name', None)
        description = validated_data.pop('description', None)
        image = validated_data.get('image', None)

        if image is not None:
            instance.image = image
            instance.save(update_fields=['image'])

        if name or description:
            DirectionDetail.objects.update_or_create(
                direction=instance,
                language=lang,
                defaults={
                    'name': name,
                    'description': description
                }
            )

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        lang = self.get_language()

        # Tanlangan til bo‘yicha detail
        detail = get_fallback_detail(instance.details, lang)

        if detail:
            data['name'] = detail.name
            data['description'] = detail.description
            data['slug'] = detail.slug
        else:
            data['name'] = None
            data['description'] = None
            data['slug'] = None

        return data


class CountrySerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'translation_statuses']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        # faqat is_active=True bo‘lgan tillar
        active_langs = obj.details.filter(is_active=True).values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name')
        country = Country.objects.create(**validated_data)

        CountryDetail.objects.create(
            country=country,
            language=lang,
            name=name,
            is_active=True
        )
        return country

    def update(self, instance, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name', None)

        if name:
            CountryDetail.objects.update_or_create(
                country=instance,
                language=lang,
                defaults={'name': name, 'is_active': True}
            )
        return instance

    def to_representation(self, instance):
        lang = self.get_language()
        detail = get_fallback_detail(instance.details.filter(is_active=True), lang)
        data = {
            "id": instance.id,
            "translation_statuses": self.get_translation_statuses(instance)
        }
        if detail:
            data.update({"name": detail.name, "slug": detail.slug})
        else:
            data.update({"name": None, "slug": None})
        return data

class UniversitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = University
        fields = ['id', 'name', 'translation_statuses']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.details.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name')
        univer = University.objects.create(**validated_data)

        UniversityDetail.objects.create(
            university=univer,
            language=lang,
            name=name
        )
        return univer

    def update(self, instance, validated_data):
        lang = self.get_language()
        name = validated_data.pop('name', None)

        if name:
            UniversityDetail.objects.update_or_create(
                university=instance,
                language=lang,
                defaults={'name': name}
            )
        return instance

    def to_representation(self, instance):
        lang = self.get_language()
        detail = get_fallback_detail(instance.details, lang)
        data = {
            "id": instance.id,
            "translation_statuses": self.get_translation_statuses(instance)
        }
        if detail:
            data.update({"name": detail.name, "slug": detail.slug})
        else:
            data.update({"name": None, "slug": None})
        return data





