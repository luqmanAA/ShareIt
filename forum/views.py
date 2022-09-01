from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView

from accounts.models import Account

from .forms import CreateCommentForm, CreatePostForm, CreateReplyForm
from .models import Comment, Group, Post, Reply
# Create your views here.


class FeedView(View):

    def get(self, request):
        return render(request, 'forum/index.html')


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ('name', 'description', 'avatar', 'privacy')

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.owner_id = self.request.user.id
        form.instance.member_id = self.request.user.id
        return super().form_valid(form)


class EditGroupView(UpdateView):
    model = Group
    fields = ('name', 'description', 'avatar', 'cover_image', 'privacy')
    template_name_suffix = '_update_form'


class GroupListView(LoginRequiredMixin, ListView):
    model = Group


class GroupDetailView(DetailView):
    model = Group


class JoinLeaveGroupView(View):

    def post(self, request, slug, pk, **kwargs):
        group = Group.objects.filter(slug=slug).first()
        if group.member.filter(id=pk).exists():
            group.admin.remove(request.user)
            group.member.remove(request.user)
            messages.add_message(
                self.request,
                messages.ERROR,
                f"You're no longer a member {group.name}"
            )
        else:
            group.admin.add(request.user)
            group.member.add(request.user)
            messages.add_message(
                self.request,
                messages.ERROR,
                f"Welcome to {group.name}"
            )
        group.save()
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER')
        )


class MemberListVIew(ListView):
    model = Group
    template_name = 'forum/members.html'

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        # return group.member.filter(is_suspended=False)
        return group.member.filter()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        print(context)
        context['group'] = Group.objects.filter(slug=self.kwargs['slug']).first()
        return context


class MakeAdminView(View):

    def post(self, request, slug, pk, **kwargs):
        member = Account.objects.filter(id=pk).first()
        group = Group.objects.filter(slug=slug, member=member).first()
        if group.admin.count() <= 3:
            group.admin.add(member)
            group.save()
        messages.add_message(
            self.request,
            messages.ERROR,
            f"{group.name} has reached maximum number of admins"
        )
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER')
        )


class SuspendMemberView(View):
    pass


class AcceptJoinRequestView(View):
    pass


class RejectJoinRequestView(View):
    pass


class CreatePostView(FormView):
    form_class = CreatePostForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        form.instance.author = self.request.user
        form.instance.group = group
        form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('forum:group-detail', kwargs={'slug': self.kwargs['slug'], })


class EditPostView(UpdateView):
    model = Post


class PostListView(ListView):
    model = Post


class PostDetailView(View):
    pass


class CreateCommentView(FormView):
    form_class = CreateCommentForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        post = Post.objects.filter(id=self.kwargs['pk']).first()
        form.instance.author = self.request.user
        form.instance.post = post
        form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('forum:group-detail', kwargs={
            'slug': self.kwargs['slug']
        })


class CreateReplyView(CreateView):
    form_class = CreateReplyForm
    template_name = 'forum/post_form.html'

    def form_valid(self, form):
        comment = Comment.objects.filter(id=self.kwargs['int']).first()
        form.instance.author = self.request.user
        form.instance.comment_id = comment.id
        form.save()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('forum:group-detail', kwargs={
            'slug': self.kwargs['slug']
        })


class TogglePostLikeView(View):

    def get(self, request, slug, pk, **kwargs):
        try:
            post = Post.objects.get(id=pk)
            if post.likes.filter(id=request.user.id).exists():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
            post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Post.DoesNotExist:
            return HttpResponseRedirect(reverse('forum:home'))


class ToggleCommentLikeVIew(View):

    def get(self, request, int, **kwargs):
        try:
            comment = Comment.objects.get(id=int)
            if comment.likes.filter(id=request.user.id).exists():
                comment.likes.remove(request.user)
            else:
                comment.likes.add(request.user)
            comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Comment.DoesNotExist:
            return HttpResponseRedirect(reverse('forum:home'))


class ToggleReplyLikeView(View):

    def get(self, request, str, **kwargs):
        try:
            reply = Reply.objects.get(id=str)
            if reply.likes.filter(id=request.user.id).exists():
                reply.likes.remove(request.user)
            else:
                reply.likes.add(request.user)
            reply.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Reply.DoesNotExist:
            return HttpResponseRedirect(reverse('forum:home'))


class TogglePostVisibilityView(View):

    def post(self, request, pk, **kwargs):
        try:
            post = Post.objects.get(id=pk)
            post.is_hidden = not post.is_hidden
            post.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Post.DoesNotExist:
            messages.add_message(
                self.request,
                messages.ERROR,
                "No such post exists"
            )
            return HttpResponseRedirect(reverse(
                request.META.get('HTTP_REFERER')
            ))


class ToggleCommentVisibilityView(View):

    def post(self, request, int, **kwargs):
        try:
            comment = Comment.objects.get(id=int)
            comment.is_hidden = not comment.is_hidden
            comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Comment.DoesNotExist:
            messages.add_message(
                self.request,
                messages.ERROR,
                "No such post exists"
            )
            return HttpResponseRedirect(reverse(
                request.META.get('HTTP_REFERER')
            ))


class ToggleReplyVisibilityView(View):

    def post(self, request, str, **kwargs):
        try:
            reply = Reply.objects.get(id=str)
            reply.is_hidden = not reply.is_hidden
            reply.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Reply.DoesNotExist:
            messages.add_message(
                self.request,
                messages.ERROR,
                "No such post exists"
            )
            return HttpResponseRedirect(reverse(
                request.META.get('HTTP_REFERER')
            ))