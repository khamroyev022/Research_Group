from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from main.models import (
    Group, GroupDetail,
    Member, MemberDetail,
    Publication, PublicationDetail,
    Projects, ProjectsTranslate,
    Achivment, AchivmentTranslation,
    Partnership, PartnershipDetail,
    Resources, ResourcesDatail,
    ReserchStudent, ReserchStudentDatail,
    NewsActivities, NewsActivitiesDetail,
    ConferencesSeminars, ConferencesSeminarsDetail,
)

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

def _paginate_list(items, page, page_size):
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return total, items[start:end]

@api_view(["GET"])
@permission_classes([AllowAny])
def global_search(request):
    q = (request.GET.get("q") or "").strip()
    lang = request.headers.get("Accept-Language", "uz")
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 20))

    if not q:
        return Response(
            {"detail": "q param yuborilishi kerak. Masalan: /api/search/?q=ai"},
            status=status.HTTP_400_BAD_REQUEST
        )

    results = []

    group_qs = (
        Group.objects
        .select_related("direction")
        .prefetch_related("details")
        .filter(
            Q(details__name__icontains=q) |
            Q(details__description__icontains=q) |
            Q(details__slug__icontains=q)
        )
        .distinct()
    )
    for obj in group_qs[:50]:
        d = get_active_fallback_detail(obj.details.all(), lang)
        results.append({
            "type": "group",
            "id": str(obj.id),
            "title": d.name if d else None,
            "description": (d.description if d else None),
            "slug": (d.slug if d else None),
        })

    # 2) Member
    member_qs = (
        Member.objects
        .select_related("group", "university", "country")
        .prefetch_related("details")
        .filter(
            Q(details__full_name__icontains=q) |
            Q(details__about__icontains=q) |
            Q(details__affiliation__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(details__slug__icontains=q)
        )
        .distinct()
    )
    for obj in member_qs[:50]:
        d = get_active_fallback_detail(obj.details.all(), lang)
        results.append({
            "type": "member",
            "id": str(obj.id),
            "title": d.full_name if d else obj.email,
            "description": d.about if d else None,
            "slug": d.slug if d else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 3) Publication
    pub_qs = (
        Publication.objects
        .select_related("group", "publisher")
        .prefetch_related("details")
        .filter(
            Q(details__title__icontains=q) |
            Q(details__topic__icontains=q) |
            Q(details__slug__icontains=q) |
            Q(url__icontains=q) |
            Q(publisher__name__icontains=q)
        )
        .distinct()
    )
    for obj in pub_qs[:50]:
        d = get_active_fallback_detail(obj.details.all(), lang)
        results.append({
            "type": "publication",
            "id": str(obj.id),
            "title": d.title if d else None,
            "description": d.topic if d else None,
            "slug": d.slug if d else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
            "url": obj.url,
        })

    # 4) Projects
    proj_qs = (
        Projects.objects
        .select_related("group", "sponsor_university", "sponsor_country")
        .prefetch_related("translations")
        .filter(
            Q(translations__title__icontains=q) |
            Q(translations__topic__icontains=q) |
            Q(translations__description__icontains=q) |
            Q(translations__slug__icontains=q)
        )
        .distinct()
    )
    for obj in proj_qs[:50]:
        tr = get_active_fallback_detail(obj.translations.all(), lang)
        results.append({
            "type": "project",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 5) Achivment (related_name='achivment')
    ach_qs = (
        Achivment.objects
        .select_related("group")
        .prefetch_related("achivment")
        .filter(
            Q(achivment__title__icontains=q) |
            Q(achivment__description__icontains=q) |
            Q(achivment__slug__icontains=q)
        )
        .distinct()
    )
    for obj in ach_qs[:50]:
        tr = get_active_fallback_detail(obj.achivment.all(), lang)
        results.append({
            "type": "achivment",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 6) Partnership (related_name='partnereship')
    part_qs = (
        Partnership.objects
        .select_related("group")
        .prefetch_related("partnereship")
        .filter(
            Q(partnereship__title__icontains=q) |
            Q(partnereship__description__icontains=q) |
            Q(partnereship__slug__icontains=q)
        )
        .distinct()
    )
    for obj in part_qs[:50]:
        tr = get_active_fallback_detail(obj.partnereship.all(), lang)
        results.append({
            "type": "partnership",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 7) Resources (related_name='resources')
    res_qs = (
        Resources.objects
        .select_related("group")
        .prefetch_related("resources")
        .filter(
            Q(resources__title__icontains=q) |
            Q(resources__description__icontains=q) |
            Q(resources__slug__icontains=q)
        )
        .distinct()
    )
    for obj in res_qs[:50]:
        tr = get_active_fallback_detail(obj.resources.all(), lang)
        results.append({
            "type": "resources",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 8) ResearchStudent (related_name='reserchStudent')
    rs_qs = (
        ReserchStudent.objects
        .select_related("group")
        .prefetch_related("reserchStudent")
        .filter(
            Q(reserchStudent__title__icontains=q) |
            Q(reserchStudent__description__icontains=q) |
            Q(reserchStudent__slug__icontains=q)
        )
        .distinct()
    )
    for obj in rs_qs[:50]:
        tr = get_active_fallback_detail(obj.reserchStudent.all(), lang)
        results.append({
            "type": "research_student",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 9) NewsActivities (related_name='newsactive')
    news_qs = (
        NewsActivities.objects
        .select_related("group")
        .prefetch_related("newsactive")
        .filter(
            Q(newsactive__title__icontains=q) |
            Q(newsactive__description__icontains=q) |
            Q(newsactive__slug__icontains=q)
        )
        .distinct()
    )
    for obj in news_qs[:50]:
        tr = get_active_fallback_detail(obj.newsactive.all(), lang)
        results.append({
            "type": "news",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
        })

    # 10) ConferencesSeminars (related_name='conferencesseminars')
    conf_qs = (
        ConferencesSeminars.objects
        .select_related("group")
        .prefetch_related("conferencesseminars")
        .filter(
            Q(conferencesseminars__title__icontains=q) |
            Q(conferencesseminars__description__icontains=q) |
            Q(conferencesseminars__slug__icontains=q)
        )
        .distinct()
    )
    for obj in conf_qs[:50]:
        tr = get_active_fallback_detail(obj.conferencesseminars.all(), lang)
        results.append({
            "type": "conference",
            "id": str(obj.id),
            "title": tr.title if tr else None,
            "description": tr.description if tr else None,
            "slug": tr.slug if tr else None,
            "group_id": str(obj.group_id) if obj.group_id else None,
            "start_date": str(obj.start_date),
        })

    # (ixtiyoriy) natijalarni "title" bo'yicha tartiblash
    results.sort(key=lambda x: (x.get("title") or "").lower())

    total, page_items = _paginate_list(results, page, page_size)

    return Response({
        "q": q,
        "lang": lang,
        "page": page,
        "page_size": page_size,
        "total": total,
        "results": page_items
    })
