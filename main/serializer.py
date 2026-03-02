from rest_framework import serializers
from dashboard.models import GlobalLink
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

class TranslationMixin:

    translation_related_name = "details"
    default_lang = "uz"

    def get_language(self):
        request = self.context.get("request")
        if request:
            lang = request.headers.get("Accept-Language", "uz")
            return lang.split(",")[0].split("-")[0].strip().lower() or "uz"
        return self.context.get("language", "uz")

    def get_translation(self, obj):
        cache_attr = f"_cached_translation_{id(obj)}"
        if not hasattr(self, cache_attr):
            qs = getattr(obj, self.translation_related_name).all()
            result = get_fallback_detail(qs, self.get_language(), self.default_lang)
            setattr(self, cache_attr, result)
        return getattr(self, cache_attr)

    def to_representation(self, obj):
        if self.get_translation(obj) is None:
            return None
        return super().to_representation(obj)

    def get_absolute_image_url(self, obj):
        if self.get_translation(obj) is None:
            return None
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None




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


class SocialMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SosialLink
        fields = ["id", "name", "image", "url", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class DirectionSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ["id", "image", "name", "description", "slug", "is_active", "created"]

    def get_name(self, obj):
        tr = self.get_translation(obj)
        return tr.name if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_image(self, obj):
        return self.get_absolute_image_url(obj)




class GroupSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    social = SociallinkSerializer(many=True, read_only=True, source="sosiallink_set")

    class Meta:
        model = Group
        fields = ("id", "image", "is_active", "created", "direction",
                  "name", "description", "social", "slug")

    def get_name(self, obj):
        tr = self.get_translation(obj)
        return tr.name if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_image(self, obj):
        return self.get_absolute_image_url(obj)




class MediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = GroupMedia
        fields = ["id", "image", "video_url", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




class SlidergroupSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SliderGroup
        fields = "__all__"

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




class AchivmentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Achivment
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




class PartnerShipSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Partnership
        fields = ["id", "image", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




class StudentSerachSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ReserchStudent
        fields = ["id", "image", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None



class ResourcesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Resources
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None




class NewSerializerHome(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "newsactive"

    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NewsActivities
        fields = ("id", "title", "slug", "image", "created_at")

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_image(self, obj):
        return self.get_absolute_image_url(obj)




class NewsSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "newsactive"

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    group_id = serializers.IntegerField(source="group.id", read_only=True)

    class Meta:
        model = NewsActivities
        fields = ("id", "title", "description", "slug", "image", "created_at", "group_id")

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
        return self.get_absolute_image_url(obj)



class ConferensiaHomeSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "conferencesseminars"

    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = ConferencesSeminars
        fields = ("id", "start_date", "created_at", "group", "title", "slug")

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None



class ConferensiaDetailSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "conferencesseminars"

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = ConferencesSeminars
        fields = ("id", "start_date", "created_at", "group", "title", "description", "slug")

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None




class InterestsSerialzier(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "interests"

    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Interests
        fields = ["id", "group", "created", "name", "description", "slug"]

    def get_name(self, obj):
        tr = self.get_translation(obj)
        return tr.name if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None



class PublicationHomeSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    title = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    translation_statuses = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            "id", "url", "publication_date", "featured", "created_at",
            "group", "publisher", "translation_statuses",
            "title", "slug", "members",
        ]

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_translation_statuses(self, obj):
        active_langs = set(obj.details.values_list("language", flat=True))
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def get_publisher(self, obj):
        if not obj.publisher:
            return None
        return {"id": str(obj.publisher_id), "name": obj.publisher.name}

    def get_group(self, obj):
        if not obj.group_id:
            return None
        lang = self.get_language()
        gd = get_fallback_detail(obj.group.details.all(), lang)
        return {"id": str(obj.group_id), "name": gd.name if gd else None}

    def get_members(self, obj):
        lang = self.get_language()
        out = []
        for m in obj.members.all():
            md = get_fallback_detail(m.details.all(), lang)
            out.append({"id": str(m.id), "full_name": md.full_name if md else None})
        return out


class PublicationDetailSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    title = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    translation_statuses = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            "id", "url", "publication_date", "featured", "created_at",
            "group", "publisher", "translation_statuses",
            "title", "topic", "slug", "members",
        ]

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_topic(self, obj):
        tr = self.get_translation(obj)
        return tr.topic if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_translation_statuses(self, obj):
        active_langs = set(obj.details.values_list("language", flat=True))
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def get_publisher(self, obj):
        if not obj.publisher:
            return None
        return {"id": str(obj.publisher_id), "name": obj.publisher.name}

    def get_group(self, obj):
        if not obj.group_id:
            return None
        lang = self.get_language()
        gd = get_fallback_detail(obj.group.details.all(), lang)
        return {"id": str(obj.group_id), "name": gd.name if gd else None}

    def get_members(self, obj):
        lang = self.get_language()
        out = []
        for m in obj.members.all():
            md = get_fallback_detail(m.details.all(), lang)
            out.append({"id": str(m.id), "full_name": md.full_name if md else None})
        return out


class ProjectsSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "translations"

    image = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    sponsor_university = serializers.SerializerMethodField()
    sponsor_country = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = (
            "id", "start_date", "end_date", "image", "amount", "status",
            "group", "sponsor_university", "sponsor_country",
            "title", "topic", "description", "slug",
        )

    def get_image(self, obj):
        return self.get_absolute_image_url(obj)

    def get_title(self, obj):
        tr = self.get_translation(obj)
        return tr.title if tr else None

    def get_topic(self, obj):
        tr = self.get_translation(obj)
        return tr.topic if tr else None

    def get_description(self, obj):
        tr = self.get_translation(obj)
        return tr.description if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_group(self, obj):
        if not obj.group:
            return None
        lang = self.get_language()
        gd = get_fallback_detail(obj.group.details.all(), lang)
        return {"id": str(obj.group.id), "name": gd.name if gd else None}

    def get_sponsor_university(self, obj):
        if not obj.sponsor_university:
            return None
        lang = self.get_language()
        ud = get_fallback_detail(obj.sponsor_university.details.all(), lang)
        return {"id": str(obj.sponsor_university.id), "name": ud.name if ud else None}

    def get_sponsor_country(self, obj):
        if not obj.sponsor_country:
            return None
        lang = self.get_language()
        cd = get_fallback_detail(obj.sponsor_country.details.all(), lang)
        return {"id": str(obj.sponsor_country.id), "name": cd.name if cd else None}



class MemberGetSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    full_name = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    affiliation = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "email", "phone", "image", "orcid",
            "google_scholar", "scopus", "status", "created",
            "university", "country", "group",
            "full_name", "about", "affiliation",
            "university_name", "country_name", "group_name", "slug",
        ]

    def get_full_name(self, obj):
        tr = self.get_translation(obj)
        return tr.full_name if tr else None

    def get_about(self, obj):
        tr = self.get_translation(obj)
        return tr.about if tr else None

    def get_affiliation(self, obj):
        tr = self.get_translation(obj)
        return tr.affiliation if tr else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def get_university_name(self, obj):
        if not obj.university:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.university.details.all(), lang)
        return d.name if d else None

    def get_country_name(self, obj):
        if not obj.country:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.country.details.all(), lang)
        return d.name if d else None

    def get_group_name(self, obj):
        if not obj.group:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.group.details.all(), lang)
        return d.name if d else None



class MemberDetailGetSerializer(TranslationMixin, serializers.ModelSerializer):
    translation_related_name = "details"

    full_name = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    affiliation = serializers.SerializerMethodField()
    university_name = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "email", "phone", "image", "orcid",
            "google_scholar", "scopus", "status", "created",
            "university", "country", "group",
            "full_name", "about", "affiliation",
            "university_name", "country_name", "group_name",
        ]

    def get_full_name(self, obj):
        tr = self.get_translation(obj)
        return tr.full_name if tr else None

    def get_about(self, obj):
        tr = self.get_translation(obj)
        return tr.about if tr else None

    def get_affiliation(self, obj):
        tr = self.get_translation(obj)
        return tr.affiliation if tr else None

    def get_university_name(self, obj):
        if not obj.university:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.university.details.all(), lang)
        return d.name if d else None

    def get_country_name(self, obj):
        if not obj.country:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.country.details.all(), lang)
        return d.name if d else None

    def get_group_name(self, obj):
        if not obj.group:
            return None
        lang = self.get_language()
        d = get_fallback_detail(obj.group.details.all(), lang)
        return d.name if d else None



class MembersPost(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"



class GlobalLinkGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalLink
        fields = ["id", "name", "url", "image"]



class SaytDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaytDetail
        fields = ['id', 'phone', 'email', 'facebook', 'twitter',
                  'instagram', 'linkedin', 'telegram']


class SliderGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderSayt
        fields = '__all__'







