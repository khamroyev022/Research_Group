from msilib.schema import Media
from pyexpat import model

from django.templatetags.i18n import language
from rest_framework import serializers
from rest_framework.response import Response
from urllib3 import request
from .models import *

def get_fallback_detail(qs, lang, default_lang="uz"):
    if not qs.exists():
        return None

    detail = qs.filter(language=lang).first()
    if detail:
        return detail

    if lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail

    return qs.first()

class SociallinkSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SosialLink
        fields = ["id", "name", "url", "image", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class OneLangDetailMixin:
    detail_related_name = "details"
    default_lang = "uz"

    def get_language(self):
        return self.context.get("language", "uz")

    def get_detail_qs(self, obj):
        return getattr(obj, self.detail_related_name).all()

    def get_detail(self, obj):
        qs = self.get_detail_qs(obj)
        return get_fallback_detail(qs, self.get_language(), self.default_lang)


class DirectionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()


    class Meta:
        model = Direction
        fields = ['id', 'image', 'name', 'description', 'slug','is_active','created']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_name(self, obj):
        lang = self.get_language()
        detail = obj.details.filter(language=lang).first()
        return detail.name if detail else None
    def get_detail(self, obj):
        qs = obj.details.all()
        return get_fallback_detail(qs, self.get_language(), "uz")

    def get_description(self, obj):
        lang = self.get_language()
        detail = obj.details.filter(language=lang).first()
        return detail.description if detail else None

    def get_slug(self, obj):
        lang = self.get_language()
        detail = obj.details.filter(language=lang).first()
        return detail.slug if detail else None

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class GroupSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    social = SociallinkSerializer(many=True, read_only=True, source="sosiallink_set")

    class Meta:
        model = Group
        fields = ("id", "image", "is_active", "created", "direction",
                  "name", "description", "social", "slug")

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_detail(self, obj):
        return get_fallback_detail(obj.details.all(), self.get_language(), "uz")

    def get_name(self, obj):
        d = self.get_detail(obj)
        return d.name if d else None

    def get_description(self, obj):
        d = self.get_detail(obj)
        return d.description if d else None

    def get_slug(self, obj):
        d = self.get_detail(obj)
        return d.slug if d else None

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"

class SlidergroupSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()
    class Meta:
        model = SliderGroup
        fields = "__all__"
    def get_image(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class AchivmentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Achivment
        fields = "id", "image",
    def get_image(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class PartnerShipSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Partnership
        fields = "id", "image","created_at",

    def get_image(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

class StudentSerachSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ReserchStudent
        fields = "id", "image",'created_at'

    def get_image(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url

        return None

class ResourcesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = Resources
        fields = "id", "image",

    def get_image(self, obj):
        request = self.context.get("request")
        if obj:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
class NewSerializerHome(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsActivities
        fields = "__all__"

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.newsactive, lang)

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if (request and obj.image) else None

class PublicationSerializerhome(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = "__all__"

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.details, lang)

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_topic(self, obj):
        tr = self.get_translation(obj)
        return tr.topic if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None
class ConferensiahomeSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = ConferencesSeminars
        fields = "__all__"

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.conferencesseminars, lang)

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

class MemberGetSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    affiliation = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    translation_statuses = serializers.SerializerMethodField()

    university = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id",
            "full_name", "affiliation", "about", "slug",
            "image",
            "email", "phone",
            "orcid", "google_scholar", "scopus",
            "created", "status",
            "translation_statuses",
            "university", "country", "group",
        ]

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.details, lang)

    def get_full_name(self, obj):
        tr = self.get_translation(obj)
        return tr.full_name if tr else None

    def get_affiliation(self, obj):
        tr = self.get_translation(obj)
        return tr.affiliation if tr else None

    def get_about(self, obj):
        tr = self.get_translation(obj)
        return tr.about if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_translation_statuses(self, obj):
        active_langs = set(obj.details.values_list("language", flat=True))
        # hammasini chiqaramiz: bor bo‘lsa True, bo‘lmasa False
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    # ====== FK ni ID emas, name bilan qaytarish ======

    def get_university(self, obj):
        if not obj.university:
            return None
        lang = self.get_language()
        tr = get_fallback_detail(obj.university.details, lang)
        return {
            "id": str(obj.university_id),
            "name": tr.name if tr else None
        }

    def get_country(self, obj):
        if not obj.country:
            return None
        lang = self.get_language()
        tr = get_fallback_detail(obj.country.details, lang)
        return {
            "id": str(obj.country_id),
            "name": tr.name if tr else None
        }

    def get_group(self, obj):
        if not obj.group:
            return None
        lang = self.get_language()
        tr = get_fallback_detail(obj.group.details, lang)
        return {
            "id": str(obj.group_id),
            "name": tr.name if tr else None
        }

class InterestsSerialzier(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Interests
        fields = ["id", "group", "created", "name", "description", "slug"]

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.interests.all(), lang)

    def get_name(self, obj):
        tr = self.get_translation(obj)
        return tr.name if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None


class PublicationHomeSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    translation_statuses = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            "id", "url", "publication_date", "featured", "created_at",
            "group",
            "publisher",
            "translation_statuses",
            "title", "topic", "slug",
            "members",
        ]

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def _tr(self, obj):
        return get_fallback_detail(obj.details.all(), self.get_language())

    def get_title(self, obj):
        tr = self._tr(obj)
        return tr.title if tr else None

    def get_topic(self, obj):
        tr = self._tr(obj)
        return tr.topic if tr else None

    def get_slug(self, obj):
        tr = self._tr(obj)
        return tr.slug if tr else None

    def get_translation_statuses(self, obj):
        active_langs = set(obj.details.values_list("language", flat=True))
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def get_publisher(self, obj):
        if not obj.publisher:
            return None
        return {"id": str(obj.publisher_id), "name": obj.publisher.name}



