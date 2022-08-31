import uuid

from django.db import models
from django.urls import reverse

# Create your models here.


class ActiveObject(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_hidden=False)


class HiddenObject(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_hidden=True)


class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to='upload/group/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='upload/group/', null=True, blank=True)
    owner = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='group')
    member = models.ManyToManyField('accounts.Account', related_name='group_member')


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='post')
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.ImageField(upload_to='upload/posts/', null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='post_likes')

    active_objects = ActiveObject()
    deleted_objects = HiddenObject()

    objects = models.Manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('post-detail', args=[self.id])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='comment')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='post_likes')


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='comment')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
    likes = models.ManyToManyField('accounts.Account', related_name='post_likes')
