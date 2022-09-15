from django.urls import path
from . import views

app_name = 'event'

urlpatterns = [
    path('', views.EventListView.as_view(), name='event-list'),
    path('create/', views.CreateEventView.as_view(), name='create-event'),
    path('<int:pk>/edit/', views.EditEventView.as_view(), name='event-edit'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('calendar/', views.EventOnCalendar.as_view(), name='calendar'),
]