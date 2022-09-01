import uuid
from autoslug import AutoSlugField

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.


class ActiveObject(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_hidden=False)


class HiddenObject(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_hidden=True)


class Group(models.Model):
    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private')
    )

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='upload/group/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='upload/group/', null=True, blank=True)
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='group')
    member = models.ManyToManyField('accounts.Account', related_name='group_member')
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    slug = models.SlugField(max_length=250, unique=True)
    admin = models.ManyToManyField('accounts.Account', related_name='admin')

    class Meta:
        permissions = (("has_all_access", "Has all access"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forum:groups')


@receiver(pre_save, sender=Group)
def slugify_name(sender, instance, **kwargs):
    # if instance.slug is None:
    instance.slug = slugify(instance.name)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='post')
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.ImageField(upload_to='upload/posts/', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='post_likes')

    active_objects = ActiveObject()
    deleted_objects = HiddenObject()

    objects = models.Manager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('post-detail', args=[self.id])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='comment')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='comment_likes')
    slug = AutoSlugField(populate_from=id, max_length=300)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.content


@receiver(pre_save, sender=Comment)
def slugify_name(sender, instance, **kwargs):
    # if instance.slug is None:
    instance.slug += slugify(instance.content)


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='reply')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='reply_likes')

    def __str__(self):
        return self.content
