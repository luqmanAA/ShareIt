from django.urls import path
from . import views

app_name = 'event'

urlpatterns = [
    path('even', views.CreateEventView.as_view(), name='create-event'),
    path('all-event', views.EventListView.as_view(), name='event-list'),
    path('event-edit<slug:slug>', views.EditEventView.as_view(), name='event-edit'),
    path('event-detail/<slug:slug>', views.EventDetailView.as_view(), name='event-detail'),
]