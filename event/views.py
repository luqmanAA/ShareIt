from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, View
from django.views.generic import UpdateView, ListView, DetailView

from .models import Event
from forum.models import Group
from accounts.models import Account


class CreateEventView(CreateView):
    model = Event
    template_name = 'event/event_create_form.html'
    fields = ('name', 'start_date_time', 'end_date_time')

    def form_valid(self, form):
        group = Group.objects.filter(id=self.kwargs['pk']).first()
        form.instance.host = self.request.user
        form.instance.group = group
        form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('forum:group-detail', args=[str('id')])


class EditEventView(UpdateView):
    model = Event
    fields = ('Cover_image', 'name', 'location', 'start_date_time', 'end_date_time')
    template_name = 'event/event_edit.html'
    success_url = '/'

    def get_initial(self):
        initial = super().get_initial()
        initial['start_date_time'] = 'Start date and time'
        initial['end_date_time'] = 'End date and time'
        return initial


class EventListView(ListView):
    model = Event
    template_name = 'event/event_list.html'


class EventDetailView(DetailView):
    model = Event
    template_name = 'event/event_detail.html'


class AcceptRejectInviteeView(View):

    def get(self, request, user_id, **kwargs):
        pass

