from rest_framework.exceptions import ValidationError
from main.models import *
from rest_framework import serializers

class LangMixin:
    def get_language(self):
        request = self.context.get("request")
        raw = request.headers.get("Accept-Language", "uz") if request else "uz"
        return (raw.split(",")[0].split("-")[0] or "uz").strip().lower()

    def build_defaults(self, **kwargs):

        return {k: v for k, v in kwargs.items() if v is not None}


def get_fallback_detail(qs, lang, default_lang="uz"):
    detail = qs.filter(language=lang).first() if lang else None
    if detail:
        return detail
    if default_lang and lang != default_lang:
        detail = qs.filter(language=default_lang).first()
        if detail:
            return detail
    return qs.first()


class MemberSerializer1(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ('id', 'full_name', 'email', 'phone', 'image')

    def get_language(self):
        request = self.context.get('request')
        return request.headers.get('Accept-Language', 'uz')

    def get_detail(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.details, lang)

    def get_full_name(self, obj):
        detail = self.get_detail(obj)
        return detail.full_name if detail else None


class GroupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]

class GroupShortSerializer(LangMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("id", "name")

    def get_name(self, obj):
        lang = self.get_language()

        tr = get_fallback_detail(obj.details, lang)
        return tr.name if tr else None

class PublicationSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    topic = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)


    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        write_only=True,
        source="group"
    )

    group = GroupShortSerializer(read_only=True)

    publisher_id = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(),
        write_only=True,
        required=False,
        source="publisher"
    )

    publisher = serializers.SerializerMethodField(read_only=True)
    slug = serializers.SerializerMethodField(read_only=True)

    member_ids = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        write_only=True,
        many=True,
        required=False
    )
    members = MemberSerializer1(read_only=True, many=True)

    class Meta:
        model = Publication
        fields = (
            "id", "url", "publication_date", "featured",
            "title", "topic",
            "publisher_id", "publisher", "slug",
            "member_ids", "members",
            "group_id", "group",
        )

    def get_translation(self, obj):
        return get_fallback_detail(obj.details, self.get_language())

    def get_publisher(self, obj):
        return {"id": obj.publisher.id, "name": obj.publisher.name} if obj.publisher else None

    def get_slug(self, obj):
        tr = self.get_translation(obj)
        return tr.slug if tr else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tr = self.get_translation(instance)
        data["title"] = tr.title if tr else None
        data["topic"] = tr.topic if tr else None
        data["slug"] = tr.slug if tr else None
        return data

    def create(self, validated_data):
        lang = self.get_language()

        title = validated_data.pop("title", None)
        topic = validated_data.pop("topic", None)
        member_ids = validated_data.pop("member_ids", [])

        publication = Publication.objects.create(**validated_data)

        if member_ids:
            publication.members.set(member_ids)

        PublicationDetail.objects.create(
            publication=publication,
            language=lang,
            title=title or "",
            topic=topic or ""
        )
        return publication

    def update(self, instance, validated_data):
        lang = self.get_language()

        member_ids = validated_data.pop("member_ids", None)
        if member_ids is not None:
            instance.members.set(member_ids)

        publisher_obj = validated_data.pop("publisher", None)
        if publisher_obj is not None:
            instance.publisher = publisher_obj

        title = validated_data.pop("title", None)
        topic = validated_data.pop("topic", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if title is not None or topic is not None:
            tr, _ = PublicationDetail.objects.get_or_create(publication=instance, language=lang)
            if title is not None:
                tr.title = title
            if topic is not None:
                tr.topic = topic
            tr.save()

        return instance


from main.models import *
from rest_framework import serializers


class MemberDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberDetail
        fields = ['id', 'full_name', 'affiliation', 'about', 'slug', 'language']


class MemberSerializer(serializers.ModelSerializer):
    university = serializers.PrimaryKeyRelatedField(
        queryset=University.objects.all(),
        required=False,
        allow_null=True
    )
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(),
        required=True
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=True
    )

    full_name = serializers.CharField(write_only=True, required=True)
    affiliation = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    about = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    translation_statuses = serializers.SerializerMethodField(read_only=True)

    status = serializers.ChoiceField(choices=STATUS_CHOISE, required=False)

    class Meta:
        model = Member
        fields = [
            'id', 'email', 'phone', 'image',
            'university', 'country', 'group',
            'orcid', 'google_scholar', 'scopus',
            'full_name', 'affiliation', 'about',
            'translation_statuses', 'status'
        ]

    def get_language(self):
        request = self.context.get("request")
        return request.headers.get("Accept-Language", "uz") if request else "uz"

    def get_translation_statuses(self, obj):
        active_langs = obj.details.values_list('language', flat=True)
        return [{"code": code, "is_active": code in active_langs} for code, _ in LANGUAGE_CHOICES]

    def create(self, validated_data):
        lang = self.get_language()

        full_name = validated_data.pop('full_name')
        affiliation = validated_data.pop('affiliation', None)
        about = validated_data.pop('about', None)

        member = Member.objects.create(**validated_data)

        MemberDetail.objects.create(
            member=member,
            language=lang,
            full_name=full_name,
            affiliation=affiliation,
            about=about
        )
        return member

    def update(self, instance, validated_data):
        lang = self.get_language()

        full_name = validated_data.pop('full_name', None)
        affiliation = validated_data.pop('affiliation', None)
        about = validated_data.pop('about', None)

        for field in ['email', 'phone', 'orcid', 'google_scholar', 'scopus']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        if 'image' in validated_data:
            instance.image = validated_data['image']

        request = self.context.get('request')
        if 'status' in validated_data:
            if request and request.user and request.user.is_staff:
                instance.status = validated_data['status']

        if 'university' in validated_data:
            instance.university = validated_data['university']
        if 'country' in validated_data:
            instance.country = validated_data['country']
        if 'group' in validated_data:
            instance.group = validated_data['group']

        instance.save()

        if full_name is not None or affiliation is not None or about is not None:
            MemberDetail.objects.update_or_create(
                member=instance,
                language=lang,
                defaults={
                    'full_name': full_name if full_name is not None else "",
                    'affiliation': affiliation,
                    'about': about
                }
            )

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()

        detail = get_fallback_detail(instance.details, lang)

        university_detail = None
        if instance.university:
            university_detail = get_fallback_detail(instance.university.details, lang)

        country_detail = None
        if instance.country:
            country_detail = get_fallback_detail(instance.country.details, lang)

        group_detail = None
        if instance.group:
            group_detail = get_fallback_detail(instance.group.details, lang)

        image_url = None
        if instance.image:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        return {
            "id": str(instance.id),
            "email": instance.email,
            "phone": instance.phone,
            "image": image_url,
            "orcid": instance.orcid,
            "google_scholar": instance.google_scholar,
            "scopus": instance.scopus,
            "status": instance.status,
            "translation_statuses": self.get_translation_statuses(instance),

            "university": None if not instance.university else {
                "id": str(instance.university_id),
                "name": university_detail.name if university_detail else None
            },

            "country": None if not instance.country else {
                "id": str(instance.country_id),
                "name": country_detail.name if country_detail else None
            },

            "group": None if not instance.group else {
                "id": str(instance.group_id),
                "name": group_detail.name if group_detail else None
            },

            "full_name": detail.full_name if detail else None,
            "affiliation": detail.affiliation if detail else None,
            "about": detail.about if detail else None,
            "slug": detail.slug if detail else None,
        }


class MemberSerializer1(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ('id', 'full_name', 'email', 'phone', 'image')

    def get_language(self):
        request = self.context.get('request')
        return request.headers.get('Accept-Language', 'uz')

    def get_detail(self, obj):
        lang = self.get_language()
        return get_fallback_detail(obj.details, lang)

    def get_full_name(self, obj):
        detail = self.get_detail(obj)
        return detail.full_name if detail else None


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'

class AchivmentSerializer(LangMixin, serializers.ModelSerializer):
    title = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Achivment
        fields = ['id', 'group', 'image', 'created_at', 'title', 'description']

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)

        group_obj = validated_data.get('group')
        if Achivment.objects.filter(group=group_obj).exists():
            raise ValidationError({'group': 'Bunday Achivment mavjud'})

        ach = Achivment.objects.create(**validated_data)

        AchivmentTranslation.objects.create(
            achivment=ach,
            language=lang,
            title=title or "",
            description=description or ""
        )
        return ach

    def update(self, instance, validated_data):
        lang = self.get_language()

        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)

        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)

        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        instance.save()

        if title is not None or description is not None:
            tr, _ = AchivmentTranslation.objects.get_or_create(
                achivment=instance,
                language=lang
            )
            if title is not None:
                tr.title = title
            if description is not None:
                tr.description = description
            tr.save()

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()

        tr = get_fallback_detail(instance.achivment, lang)  # related_name shu bo'lsa
        image_url = request.build_absolute_uri(instance.image.url) if request and instance.image else (instance.image.url if instance.image else None)

        return {
            "id": instance.id,
            "image": image_url,
            "created_at": instance.created_at,
            "group": {"id": instance.group.id, "name": get_fallback_detail(instance.group.details, lang).name} if instance.group_id else None,
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None
        }


class PartnershipSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Partnership
        fields = ['id', 'group', 'image', 'created_at', 'title', 'description', 'translation_statuses']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.partnereship.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()

        group = validated_data.get("group")

        if Partnership.objects.filter(group=group).exists():
            raise serializers.ValidationError({
                "group": "Bu group uchun Partnership allaqachon mavjud. Yangi yaratib bo'lmaydi."
            })

        title = validated_data.pop('title')
        description = validated_data.pop('description')

        partnership = Partnership.objects.create(**validated_data)
        PartnershipDetail.objects.create(
            partnership=partnership,
            language=lang,
            title=title,
            description=description
        )
        return partnership

    def update(self, instance, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)
        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)

        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        instance.save()

        if title or description:
            PartnershipDetail.objects.update_or_create(
                partnership=instance,
                language=lang,
                defaults={
                    'title': title,
                    'description': description
                }
            )
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()
        detail = get_fallback_detail(instance.partnereship, lang)

        image_url = None
        if instance.image:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": instance.id,
            "image": image_url,
            "created_at": instance.created_at,
            "translation_statuses": self.get_translation_statuses(instance),
            "group": {
                "id": instance.group.id,
                "name": group_detail.name if group_detail else None
            }
        }

        data.update({
            "title": detail.title if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None
        })
        return data


class ReserchStudentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = ReserchStudent
        fields = ['id', 'group', 'image', 'created_at', 'title', 'description', 'translation_statuses']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.reserchStudent.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title')
        description = validated_data.pop('description')
        if ReserchStudentDatail.objects.filter(title=title, description=description).exists():
            raise serializers.ValidationError({'Error': 'Reserch Student already exists!'})
        student = ReserchStudent.objects.create(**validated_data)
        ReserchStudentDatail.objects.create(
            reserchStudent=student,
            language=lang,
            title=title,
            description=description
        )
        return student

    def update(self, instance, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)
        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)
        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        instance.save()

        if title or description:
            ReserchStudentDatail.objects.update_or_create(
                reserchStudent=instance,
                language=lang,
                defaults={
                    'title': title,
                    'description': description
                }
            )
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()
        detail = get_fallback_detail(instance.reserchStudent, lang)

        image_url = None
        if instance.image:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": instance.id,
            "image": image_url,
            "created_at": instance.created_at,
            "translation_statuses": self.get_translation_statuses(instance),
            "group": {
                "id": instance.group.id,
                "name": group_detail.name if group_detail else None
            }
        }

        data.update({
            "title": detail.title if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None
        })
        return data

class ResourcesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = Resources
        fields = ['id', 'group', 'image', 'created_at', 'title', 'description', 'translation_statuses']

    def get_language(self):
        request = self.context.get("request")
        raw = request.headers.get("Accept-Language", "uz") if request else "uz"
        return (raw.split(",")[0].split("-")[0] or "uz").strip().lower()

    def get_translation_statuses(self, obj):
        active_langs = obj.resources.values_list('language', flat=True)
        return [
            {"code": code, "is_active": code in active_langs}
            for code, _ in LANGUAGE_CHOICES
        ]

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title')
        description = validated_data.pop('description')

        group_obj = validated_data.get("group")
        if Resources.objects.filter(group=group_obj).exists():
            raise ValidationError({"group": "Bu group uchun Resources allaqachon mavjud."})

        resource = Resources.objects.create(**validated_data)

        ResourcesDatail.objects.create(
            resources=resource,
            language=lang,
            title=title,
            description=description
        )
        return resource

    def update(self, instance, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)

        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)

        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        instance.save()

        if title is not None or description is not None:
            ResourcesDatail.objects.update_or_create(
                resources=instance,
                language=lang,
                defaults={
                    'title': title,
                    'description': description
                }
            )
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()

        detail = get_fallback_detail(instance.resources, lang)

        image_url = None
        if instance.image:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": instance.id,
            "image": image_url,
            "created_at": instance.created_at,
            "translation_statuses": self.get_translation_statuses(instance),
            "group": {
                "id": instance.group.id,
                "name": group_detail.name if group_detail else None
            }
        }

        data.update({
            "title": detail.title if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None
        })
        return data

class NewsActivitiesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = NewsActivities
        fields = [
            'id', 'group', 'image', 'created_at',
            'title', 'description', 'translation_statuses'
        ]

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.newsactive.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title')
        description = validated_data.pop('description')

        news = NewsActivities.objects.create(**validated_data)
        NewsActivitiesDetail.objects.create(
            newsdetail=news,
            language=lang,
            title=title,
            description=description
        )
        return news

    def update(self, instance, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)
        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)

        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if title or description:
            NewsActivitiesDetail.objects.update_or_create(
                newsdetail=instance,
                language=lang,
                defaults={
                    'title': title,
                    'description': description
                }
            )
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()
        detail = get_fallback_detail(instance.newsactive, lang)

        image_url = None
        if instance.image:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": instance.id,
            "image": image_url,
            "created_at": instance.created_at,
            "translation_statuses": self.get_translation_statuses(instance),
            "group": {
                "id": instance.group.id,
                "name": group_detail.name if group_detail else None
            }
        }

        data.update({
            "title": detail.title if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None
        })
        return data


class ConferencesSeminarsSerializer(serializers.ModelSerializer):
    title = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = ConferencesSeminars
        fields = [
            'id', 'group', 'created_at', 'start_date',
            'title', 'description', 'translation_statuses'
        ]

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        active_langs = obj.conferencesseminars.values_list('language', flat=True)
        return [
            {"code": code, "is_active": True}
            for code, _ in LANGUAGE_CHOICES
            if code in active_langs
        ]

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title')
        description = validated_data.pop('description')

        conf = ConferencesSeminars.objects.create(**validated_data)
        ConferencesSeminarsDetail.objects.create(
            conferencesseminars=conf,
            language=lang,
            title=title,
            description=description
        )
        return conf

    def update(self, instance, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title', None)
        description = validated_data.pop('description', None)
        group = validated_data.pop('group', None)

        if group is not None:
            instance.group = group
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if title or description:
            ConferencesSeminarsDetail.objects.update_or_create(
                conferencesseminars=instance,
                language=lang,
                defaults={
                    'title': title,
                    'description': description
                }
            )
        return instance

    def to_representation(self, instance):
        lang = self.get_language()
        detail = get_fallback_detail(instance.conferencesseminars, lang)

        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": instance.id,
            "created_at": instance.created_at,
            "start_date": instance.start_date,
            "translation_statuses": self.get_translation_statuses(instance),
            "group": {
                "id": instance.group.id,
                "name": group_detail.name if group_detail else None
            }
        }

        data.update({
            "title": detail.title if detail else None,
            "description": detail.description if detail else None,
            "slug": detail.slug if detail else None
        })
        return data

class SliderGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    title = serializers.CharField(write_only=True)
    translation_statuses = serializers.SerializerMethodField()

    class Meta:
        model = SliderGroup
        fields = ['id', 'group', 'title', 'translation_statuses', 'image', 'created_at']

    def get_language(self):
        return self.context.get('language', 'uz')

    def get_translation_statuses(self, obj):
        # ✅ SliderGroupDetail da language bor
        active_langs = obj.details.values_list('language', flat=True)

        return [
            {
                "code": code,
                "is_active": code in active_langs
            }
            for code, _ in LANGUAGE_CHOICES
        ]

    def create(self, validated_data):
        lang = self.get_language()
        title = validated_data.pop('title')

        slider = SliderGroup.objects.create(**validated_data)

        # ⚠️ sizda is_avtive field bor
        SliderGroupDetail.objects.create(
            slider_group=slider,
            language=lang,
            title=title,
            is_avtive=True
        )
        return slider

    def update(self, instance, validated_data):
        lang = self.get_language()

        title = validated_data.pop('title', None)
        image = validated_data.pop('image', None)
        group = validated_data.pop('group', None)

        if image is not None:
            instance.image = image
        if group is not None:
            instance.group = group
        instance.save()

        detail = instance.details.filter(language=lang).first()

        if detail:
            if title is not None:
                detail.title = title
            detail.is_avtive = True
            detail.save()
        elif title is not None:
            SliderGroupDetail.objects.create(
                slider_group=instance,
                language=lang,
                title=title,
                is_avtive=True
            )

        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        lang = self.get_language()

        image_url = None
        if instance.image and instance.image.name:
            image_url = request.build_absolute_uri(instance.image.url) if request else instance.image.url

        slider_detail = get_fallback_detail(instance.details, lang)
        group_detail = get_fallback_detail(instance.group.details, lang)

        data = {
            "id": str(instance.id),
            "image": image_url,
            "created_at": instance.created_at,
            "translation_statuses": self.get_translation_statuses(instance),
            "title": slider_detail.title if slider_detail else None,
            "group": {
                "id": str(instance.group.id),
                "name": group_detail.name if group_detail else None
            }
        }

        return data
class GroupMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name']

    def get_name(self, obj):
        lang = self.context.get('language', 'uz')
        detail = obj.details.filter(language=lang, is_active=True).first()
        if not detail:
            detail = obj.group.filter(language=lang).first()
        if not detail:
            detail = obj.group.first()
        return detail.name if detail else None

class MediaSerializer(serializers.ModelSerializer):
    group = GroupMiniSerializer(read_only=True)
    class Meta:
        model = GroupMedia
        fields = ['id','image','video_url','group','created_at' ]


class SocialLinkSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    class Meta:
        model = SosialLink
        fields = ['id','name','url','group','image','created_at']


class MemberPatchStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["status"]

