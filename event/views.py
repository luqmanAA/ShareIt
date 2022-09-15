from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, View
from django.views.generic import UpdateView, ListView, DetailView
from django.utils import timezone

from .models import Event
from forum.models import Group
from forum.views import GroupMixin
from forum.models import Membership


class CreateEventView(GroupMixin, LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'event/event_create_form.html'
    fields = ('name', 'location', 'Cover_image', 'description', 'start_date_time', 'end_date_time')

    def form_valid(self, form):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        if form.is_valid():
            form.instance.host = self.request.user
            form.instance.group = group
            form.save()
            return super().form_valid(form)

    def send_notification(self):
        pass

    def get_success_url(self) -> str:
        return reverse('forum:event:event-list', args=[self.kwargs['slug']])


class UpcomingExpiredEventView(LoginRequiredMixin, GroupMixin,View):
    def get(self, request, *args, **kwargs):
        pass


class EditEventView(GroupMixin, LoginRequiredMixin, UpdateView):
    raise_exception = False
    permission_required = 'event.change_event'
    login_url = '/'
    redirect_field_name = 'event-detail'

    model = Event
    fields = ('Cover_image', 'name', 'location', 'start_date_time', 'end_date_time')
    template_name = 'event/event_edit.html'
    success_url = '/'


class EventListView(GroupMixin, LoginRequiredMixin, ListView):
    model = Event
    template_name = 'event/event_list.html'
    records = {}

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        self.records['group'] = group
        return Event.objects.filter(
            group=group
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # group = Group.objects.filter(slug=self.kwargs['slug']).first()
        context['upcoming_events'] = Event.objects.filter(
            group=self.records['group'],
            start_date_time__gt=datetime.now()
        )
        context['past_events'] = Event.objects.filter(
            group=self.records['group'],
            end_date_time__lt=datetime.now()
        )
        context['ongoing_events'] = Event.objects.filter(
            group=self.records['group'],
            start_date_time=timezone.now()
        )
        return context


class EventDetailView(GroupMixin, LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'event/event_detail.html'


class EventOnCalendar(View):

    def get(self, request, *args, **kwargs):
        # group = Group.objects.filter(slug=self.kwargs['slug']).first()
        event = Event.objects.all()
        context = {
            'event': event
        }
        return render(request, 'calendar/calendar.html', context)


class AcceptRejectInviteeView(GroupMixin, LoginRequiredMixin, View):

    def get(self, request, event_id, **kwargs):
        pass



