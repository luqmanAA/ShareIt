from django.urls import path

from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.PollListVIew.as_view(), name='poll-list'),
    path('create', views.PollCreateView.as_view(), name='poll-create'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<slug:slug>/<int:poll_id>/vote/', views.VoteView.as_view(), name='vote'),
    path('<int:pk>/edit', views.PollEditView.as_view(), name="poll-edit"),
]
