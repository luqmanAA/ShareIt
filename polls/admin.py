from django.contrib import admin

from .models import Choice, Poll


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None, {'fields': ['poll_text']}),
    #     ('Date information', {'fields': ['created_date'], 'classes': ['collapse']}),
    # ]
    inlines = [ChoiceInline]
    list_display = ('poll_text', 'created_date', 'was_published_recently')
    list_filter = ['created_date']


admin.site.register(Poll, PollAdmin)