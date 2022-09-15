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
from accounts.models import Account


class CreateEventView(GroupMixin, LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'event/event_create_form.html'
    fields = ('name', 'location', 'Cover_image', 'description', 'start_date_time', 'end_date_time')

    # def test_func(self):
    #     group = self.get_object()
    #     if self.request.user == group.admin:
    #         return True
    #     return redirect('forum:event:create-event')

    def form_valid(self, form):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        if form.is_valid():
            form.instance.host = self.request.user
            form.instance.group = group
            form.save()
            return super().form_valid(form)

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

    # def get(self, request, *args, pk, **kwargs):
    #     group = Group.objects.filter(slug=self.kwargs['slug']).first()
    #     event = Event.objects.filter(id=pk).first()
    #     context = {
    #         'event': event
    #     }
    #     return render(request, 'event/event_detail.html', context)


class AcceptRejectInviteeView(GroupMixin, LoginRequiredMixin, View):

    def get(self, request, user_id, event_id, **kwargs):
        event_id = Event.objects.get(id=event_id)

# Admin can create events - title, description, start time (including date), end
# time (including date), location (if applicable). Creating events send an invite to
# all group members.
# ◦ Admin can edit events that have not started or are expired.
# ◦ Admin should be able to view all events list
# ◦ Members should be able to view events on a calendar view
# ◦ Members should be able to respond to an event invite as yes, no or maybe.
# ◦ Admin should be able to view an event, view summary of invite information
# (total number of responses as well as number of responses for each type of
# responses and other data points you can think of)
