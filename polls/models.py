import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account
from forum.models import Group


class Poll(models.Model):
    poll_text = models.CharField(max_length=200, null=True)
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    poll_author = models.ForeignKey(Account, on_delete=models.CASCADE, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created_date <= now

    was_published_recently.admin_order_field = 'created_at'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    class Meta:
        permissions = (
            ("can_create_poll", "Can create poll"),
        )

    def __str__(self):
        return self.poll_text

    def get_absolute_url(self):
        return reverse('polls:results', args=(self.id,))

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
