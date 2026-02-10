from msilib.schema import Media
from os import name

from rest_framework import serializers
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

    class Meta:
        model = Group
        fields = ("id", "image", "is_active", "created", "direction", "name", "description", "slug")

    def get_language(self):
        request = self.context.get("request")
        if request:
            return request.headers.get("Accept-Language", "uz")
        return self.context.get("language", "uz")

    def get_detail(self, obj):
        qs = obj.details.all()
        return get_fallback_detail(qs, self.get_language(), "uz")

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
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
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





















