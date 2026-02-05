
from django.db import models
from django.utils.text import slugify
import uuid
from django.db.models.signals import pre_save



LANGUAGE_CHOICES = (
    ('uz', 'Uzbek'),
    ('ru', 'Russian'),
    ('en', 'English'),
)

class Publisher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    slug = models.SlugField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            count = Publisher.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class University(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)

class UniversityDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='details')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            count = UniversityDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)

class CountryDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='details')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            count = CountryDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Direction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='directions/', null=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

class DirectionDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=270, blank=True)

    class Meta:
        unique_together = ('direction', 'language',)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            count = DirectionDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='groups/', null=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)

class GroupDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
       related_name='group'
    )
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=270, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'language', 'slug')

    def save(self, *args, **kwargs):

        if self.is_active:
            GroupDetail.objects.filter(
                group=self.group
            ).exclude(
                id=self.id
            ).update(is_active=False)

        if not self.slug:
            base = slugify(self.name)
            count = GroupDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base

        super().save(*args, **kwargs)

class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='members/')
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='members'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='members'
    )

    orcid = models.URLField(blank=True)
    google_scholar = models.URLField(blank=True)
    scopus = models.URLField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class MemberDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    full_name = models.CharField(max_length=100,null=False, blank=False)
    affiliation = models.CharField(max_length=200,null=False, blank=False)
    about = models.TextField()
    slug = models.SlugField(max_length=120, blank=True)

    class Meta:
        unique_together = ('member', 'language', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name)
            count = MemberDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    publication_date = models.DateField()
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='publiosher')
    members = models.ManyToManyField(
        Member,
        through='MemberPublication',
        related_name='publications'
    )

class PublicationDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=255,null=False, blank=False)
    topic = models.CharField(max_length=150,null=False, blank=False)
    slug = models.SlugField(max_length=270, blank=True)

    class Meta:
        unique_together = ('publication', 'language', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = PublicationDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class MemberPublication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('member', 'publication')

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Interests(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    group = models.OneToOneField(Group,on_delete=models.CASCADE,related_name='group_interest')
    created = models.DateTimeField(auto_now_add=True)

class InterestDetail(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=100, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')

    interests = models.ForeignKey(
        Interests,
        on_delete=models.CASCADE,
        related_name='interests'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            count = InterestDetail.objects.filter(slug__startswith=base).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='news/')
    created_at = models.DateTimeField(auto_now_add=True)

class NewsTranslation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='translations'
    )

    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    class Meta:
        unique_together = ('news', 'language')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = NewsTranslation.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class NewsDetail(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    news = models.OneToOneField(News,on_delete=models.CASCADE,related_name='news_detail')

class NewsDetailTranslate(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    description = models.TextField()
    language = models.CharField(max_length=2,choices=LANGUAGE_CHOICES, default='uz')
    newsdetail = models.ForeignKey(NewsDetail, on_delete=models.CASCADE, related_name='news_detail_translate')

class Projects(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to = 'media/projacts/')
    amout = models.DecimalField(max_digits=10,decimal_places=2)
    sponsor_university = models.ForeignKey(University,on_delete=models.CASCADE)
    sponsor_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    status_projects = models.BooleanField()

class ProjectsTranslate(models.Model):
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=20, null=True)
    projects = models.ForeignKey(Projects, on_delete=models.CASCADE,related_name='translations')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = NewsTranslation.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)

class Achivment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/achivment/')
    created_at = models.DateTimeField(auto_now_add=True)
class AchivmentTranslation(models.Model):
    title =models.CharField(max_length=150)
    description  = models.TextField()
    slug = models.SlugField(max_length=20,null=True)
    achivment = models.ForeignKey(Achivment, on_delete=models.CASCADE, related_name='achivment')
    def save(self, *args, **kwargs):
        if not slug:
            base = slugify(self.title)
            count = AchivmentTranslation.objects.filter(
                slug__startswith =  base
            )
            self.slug = f"{base}-{count+1}" if count else base
        super ().save(*args,**kwargs)
    def __str__ (self):
        return self.title

class Partnership(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/achivment/')
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
class PartnershipDetail(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=10,null=True)
    partnership = models.ForeignKey(Partnership,on_delete=models.CASCADE, related_name='partnereship')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    def save(self, *args, **kwargs):
        if not slug:
            base = slugify(self.title)
            count = PartnershipDetail.objects.filter(
                slug__startswith = base
            )
            self.slug = f"{base}-{count+1}" if count else None
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title


class ReserchStudent(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/reserchStudent/')
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
class ReserchStudentDatail(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=10,null=True)
    reserchStudent = models.ForeignKey(ReserchStudent,on_delete=models.CASCADE, related_name='reserchStudent')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    
    def save(self, *args, **kwargs):
        if not slug:
            base = slugify(self.title)
            count = ReserchStudentDatail.objects.filter(
                slug__startswith = base
            )
            self.slug = f"{base}-{count+1}" if count else None
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title

class Resources(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/resources/')
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
class ResourcesDatail(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=10,null=True)
    resources = models.ForeignKey(Resources,on_delete=models.CASCADE, related_name='resources')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    
    def save(self, *args, **kwargs):
        if not slug:
            base = slugify(self.title)
            count = ResourcesDatail.objects.filter(
                slug__startswith = base
            )
            self.slug = f"{base}-{count+1}" if count else None
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title


class NewsActivities(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    image = models.ImageField(upload_to='media/news_group')
    created_at = models.DateTimeField(auto_now_add=True)
    creat_at = models.DateField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

class NewsActivitiesDetail(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2)
    slug = models.SlugField(max_length=10,null=True)
    newsdetail = models.ForeignKey(NewsActivities,on_delete=models.CASCADE, related_name='newsactive')
    def save(self, *args, **kwargs):
        base = slugify(self.title)
        count = NewsActivitiesDetail.objects.filter(
            slug__startswith = base
        )
        self.slug(f"{base}-{count+1}") if count else None
        super().save()
    def __str__(self):
        return self.title


class ConferencesSeminars(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    creat_at = models.DateField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

class ConferencesSeminarsDetail(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2)
    slug = models.SlugField(max_length=10,null=True)
    conferencesseminars = models.ForeignKey(NewsActivities,on_delete=models.CASCADE, related_name='conferencesseminars')
    def save(self, *args, **kwargs):
        base = slugify(self.title)
        count = ConferencesSeminarsDetail.objects.filter(
            slug__startswith = base
        )
        self.slug(f"{base}-{count+1}") if count else None
        super().save()
    def __str__(self):
        return self.title

class SliderGroup(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    creat_at = models.DateField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/slider/')
class SliderGroupDetail(models.Model):
    title = models.CharField(max_length=100)
    def __str__(self):
        return self.title

class GroupMedia(models.Model):
    id = models.UUIDField(primary_key=True, editable=True, default=uuid.uuid4)
    image = models.ImageField(upload_to = 'media/groupmedia/')
    video = models.URLField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE)





