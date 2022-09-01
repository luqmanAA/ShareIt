from django.urls import path

from .views import (
    CreateCommentView, CreatePostView, CreateGroupView, CreateReplyView,
    EditGroupView, FeedView, GroupListView, GroupDetailView,
    JoinLeaveGroupView, MakeAdminView, MemberListVIew, PostListView, PostDetailView,
    SuspendMemberView, ToggleCommentLikeVIew, TogglePostLikeView, ToggleReplyLikeView
)

app_name = 'forum'

urlpatterns = [
    path('', FeedView.as_view(), name='home'),
    path('group/create', CreateGroupView.as_view(), name='group-create'),
    path('groups', GroupListView.as_view(), name='groups'),
    path('group/<slug:slug>', GroupDetailView.as_view(), name='group-detail'),
    path('group/<slug:slug>/edit', EditGroupView.as_view(), name='group-edit'),
    path('group/<slug:slug>/members', MemberListVIew.as_view(), name='members'),
    path('group/<slug:slug>/member/<int:pk>/join-leave', JoinLeaveGroupView.as_view(), name='join-leave'),
    path('group/<slug:slug>/posts', PostListView.as_view(), name='group-posts'),
    path('group/<slug:slug>/post/create', CreatePostView.as_view(), name='create-post'),
    path('group/<slug:slug>/post/<uuid:pk>/like-unlike',
         TogglePostLikeView.as_view(),
         name='like-post'),
    path('group/<slug:slug>/post/<uuid:pk>/comment',
         CreateCommentView.as_view(),
         name='add-comment'),
    path('group/<slug:slug>/post/<uuid:pk>/comment/<int:int>/reply',
         CreateReplyView.as_view(),
         name='add-reply'),
    path('group/<slug:slug>/post/<uuid:pk>/comment/<int:int>/like-dislike',
         ToggleCommentLikeVIew.as_view(),
         name='like-comment'
         ),
    path('group/<slug:slug>/post/<uuid:pk>/comment/<int:int>/reply/<str:str>/like-dislike',
         ToggleReplyLikeView.as_view(),
         name='like-reply'
         ),
    path('group/<slug:slug>/members/<int:pk>/suspend', SuspendMemberView.as_view(), name='suspend-member'),
    path('group/<slug:slug>/members/<int:pk>/make-admin', MakeAdminView.as_view(), name='make-admin'),

]