from datetime import datetime

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse

from accounts.models import Account
from forum.models import Group


class Event(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    host = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name='Event name')
    slug = models.SlugField(max_length=150, unique=True, null=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=300, verbose_name='Event Location')
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    Cover_image = models.ImageField(upload_to='upload/event/', default='img/cover_bg.jfif')
    members = models.ManyToManyField(Account, related_name='event_members')
    confirmed_invitees = models.IntegerField(default=0)
    unconfirmed_invitees = models.IntegerField(default=0)

    class Meta:
        ordering = ('-start_date_time',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event:event', args=[str('id')])


@receiver(pre_save, sender=Event)
def save_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)
    return instance.slug