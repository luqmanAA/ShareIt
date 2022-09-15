from django.contrib import admin

from .models import Choice, Poll, Vote


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('poll_text', "start_date", "end_date", 'created_date', 'was_published_recently')
    list_filter = ['created_date']


class VoterAdmin(admin.ModelAdmin):
    list_display = ('voter', 'poll', 'choice')


admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoterAdmin)