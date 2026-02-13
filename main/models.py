from django.db import models
from django.utils.text import slugify
import uuid
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver



LANGUAGE_CHOICES = (
    ('uz', 'Uzbek'),
    ('ru', 'Russian'),
    ('en', 'English'),
)

STATUS_CHOISE = (
    ('new',"Yangi"),
    ('in_progress','Jarayonda'),
    ('completed','Tasdiqlandi'),
    ('rejected','Rad_etildi')
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
    slug = models.SlugField(max_length=255, unique=True, blank=True)
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
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
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
    image = models.ImageField(upload_to='media/groups/', null=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE
    )
    def __str__(self):
        return str(self.id)

class GroupDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
       related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
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
        related_name='members',null=True
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='members')
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='members'
    )

    orcid = models.URLField(blank=True,null=True)
    google_scholar = models.URLField(blank=True,null=True)
    scopus = models.URLField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=150,choices=STATUS_CHOISE, default='new')

    def __str__(self):
        return self.email

class MemberDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    full_name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=200,null=True, blank=True)
    about = models.TextField(null=True, blank=True)
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
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='publisher')
    members = models.ManyToManyField(
        Member,
        through='MemberPublication',
        related_name='publication_member'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='group_publication'
    )

class PublicationDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='details'
    )
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    title = models.CharField(max_length=255,null=False, blank=False)
    topic = models.TextField()
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


class Projects(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to = 'media/projacts/')
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    sponsor_university = models.ForeignKey(University,on_delete=models.CASCADE)
    sponsor_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    status = models.BooleanField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,related_name='preoject', null=True, blank=True)


class ProjectsTranslate(models.Model):
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=20, null=True)
    projects = models.ForeignKey(Projects, on_delete=models.CASCADE,related_name='translations')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = ProjectsTranslate.objects.filter(
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
    slug = models.SlugField(max_length=150,null=True)
    achivment = models.ForeignKey(Achivment, on_delete=models.CASCADE, related_name='achivment')
    language = models.CharField(max_length=2,choices=LANGUAGE_CHOICES,default='uz')
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = AchivmentTranslation.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super ().save(*args,**kwargs)
    def __str__ (self):
        return self.title

class Partnership(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/achivment/')
    created_at = models.DateTimeField(auto_now_add=True)
class PartnershipDetail(models.Model):
    title = models.CharField(max_length=100,null=False)
    description = models.TextField()
    slug = models.SlugField(max_length=110,null=True)
    partnership = models.ForeignKey(Partnership,on_delete=models.CASCADE, related_name='partnereship')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = PartnershipDetail.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title

class ReserchStudent(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='research_students')
    image = models.ImageField(upload_to = 'media/reserchStudent/')
    created_at = models.DateTimeField(auto_now_add=True)
class ReserchStudentDatail(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=100,null=True)
    reserchStudent = models.ForeignKey(ReserchStudent,on_delete=models.CASCADE, related_name='reserchStudent')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = ReserchStudentDatail.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title

class Resources(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    group = models.OneToOneField(Group,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/resources/')
    created_at = models.DateTimeField(auto_now_add=True)
class ResourcesDatail(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=100,null=True)
    resources = models.ForeignKey(Resources,on_delete=models.CASCADE, related_name='resources')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='uz')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            count = ResourcesDatail.objects.filter(
                slug__startswith=base
            ).count()
            self.slug = f"{base}-{count+1}" if count else base
        super ().save(*args,**kwargs)

    def __str__(self):
        return self.title

class NewsActivities(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    image = models.ImageField(upload_to='media/news_group')
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
class NewsActivitiesDetail(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2,default='uz')
    slug = models.SlugField(max_length=150,null=True,unique=True)
    newsdetail = models.ForeignKey(NewsActivities,on_delete=models.CASCADE, related_name='newsactive')
    def save(self, *args, **kwargs):
        base = slugify(self.title)
        count = NewsActivitiesDetail.objects.filter(
            slug__startswith=base
        ).count()
        if not self.slug:
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class ConferencesSeminars(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
class ConferencesSeminarsDetail(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=2,default='uz')
    slug = models.SlugField(max_length=100,null=True)
    conferencesseminars = models.ForeignKey(ConferencesSeminars, on_delete=models.CASCADE, related_name='conferencesseminars')
    def save(self, *args, **kwargs):
        base = slugify(self.title)
        count = ConferencesSeminarsDetail.objects.filter(
            slug__startswith=base
        ).count()
        if not self.slug:
            self.slug = f"{base}-{count+1}" if count else base
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class SliderGroup(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/slider/')
class SliderGroupDetail(models.Model):
    slider_group = models.ForeignKey(
        SliderGroup,
        related_name='details',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='uz')
    is_avtive = models.BooleanField(default=False)
    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('slider_group', 'language')


class GroupMedia(models.Model):
    id = models.UUIDField(primary_key=True, editable=True, default=uuid.uuid4)
    image = models.ImageField(upload_to = 'media/group-media/')
    video_url = models.URLField()
    group = models.ForeignKey(Group,on_delete=models.CASCADE,related_name='media')
    created_at = models.DateTimeField(auto_now_add=True)


def _delete_file(file_field):
    if file_field and file_field.name:
        storage = file_field.storage
        if storage.exists(file_field.name):
            storage.delete(file_field.name)


@receiver(post_delete)
def delete_images_on_delete(sender, instance, **kwargs):
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            _delete_file(getattr(instance, field.name))


@receiver(pre_save)
def delete_images_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    for field in sender._meta.fields:
        if not isinstance(field, models.ImageField):
            continue
        try:
            old_instance = sender._default_manager.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)
        if old_file and old_file != new_file:
            _delete_file(old_file)

class SosialLink(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    url = models.URLField()
    image = models.ImageField(upload_to='media/sosiallink/')
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

