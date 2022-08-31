from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .models import Comment, Group, Post, Reply
# Create your views here.


class FeedView(View):

    def get(self, request):
        return render(request, 'forum/index.html')


class CreateGroupView(CreateView):
    model = Group


class EditGroupView(UpdateView):
    model = Group


class GroupListView(ListView):
    model = Group


class GroupDetailView(DetailView):
    model = Group


class JoinLeaveGroupView(View):
    pass


class MemberListVIew(ListView):
    pass


class MakeAdminView(View):
    pass


class RemoveMemberView(View):
    pass


class SuspendMemberView(View):
    pass

class AcceptJoinRequestView(View):
    pass


class RejectJoinRequestView(View):
    pass


class CreatePostView(CreateView):
    model = Post


class EditPostView(UpdateView):
    model = Post


class PostListView(ListView):
    model = Post


class PostDetailView(View):
    pass


class CreateCommentView(CreateView):
    model = Comment


class CreateReplyView(CreateView):
    model = Reply


class TogglePostLikeView(View):
    pass


class ToggleCommentLikeVIew(View):
    pass


class ToggleReplyLikeView(View):
    pass


class TogglePostVisibilityView(View):
    pass


class ToggleCommentVisibilityView(View):
    pass


class ToggleReplyVisibilityView(View):
    pass
