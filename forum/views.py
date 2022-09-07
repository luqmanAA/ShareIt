from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin
)
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
from .models import Comment, Group, Membership, Post, Reply
# Create your views here.


class FeedView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'forum/index.html')


class CreateGroupView(LoginRequiredMixin, CreateView):
    model = Group
    fields = ('name', 'description', 'avatar', 'privacy')

    def form_valid(self, form):
        form.save(commit=False)
        form.instance.owner_id = self.request.user.id
        form.save()
        # member = Account.objects.filter(id=self.request.user.id).first()
        # add group creator to members list
        Membership.objects.create(
            group_id=form.instance.id,
            user_id=self.request.user.id
        )
        return super().form_valid(form)


class EditGroupView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = ('name', 'description', 'avatar', 'cover_image', 'privacy')
    template_name_suffix = '_update_form'


class GroupListView(LoginRequiredMixin, ListView):
    model = Group


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data()
        context['membership_checked'] = self.object.member.filter(
            user_id=self.request.user.id
        )
        context['user_suspended'] = self.object.member.filter(
            user_id=self.request.user.id
        ).first().is_suspended
        return context


class JoinLeaveGroupView(LoginRequiredMixin, View):

    def post(self, request, slug, pk, **kwargs):
        group = Group.objects.filter(slug=slug).first()
        if group.member.filter(user_id=pk).exists():
            group.admin.remove(request.user)
            Membership.objects.filter(user_id=pk).delete()
            messages.error(
                request,
                f"You're no longer a member {group.name}"
            )
        else:
            Membership.objects.create(user_id=pk, group_id=group.id)
            messages.info(
                request,
                f"Welcome to {group.name}"
            )
        group.save()
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER')
        )


class MemberListVIew(LoginRequiredMixin, ListView):
    context_object_name = 'membership_list'
    template_name = 'forum/members.html'
    paginate_by = 10

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        # account = Account.objects.filter()
        return group.member.filter(is_suspended=False)
        # return group.member.filter()

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['group'] = Group.objects.filter(slug=self.kwargs['slug']).first()
        context['membership_checked'] = context['group'].member.filter(
            user_id=self.request.user.id
        )
        context['suspended_members'] = context['group'].member.filter(is_suspended=True)
        return context


class MakeAdminView(LoginRequiredMixin, View):

    def post(self, request, slug, pk, **kwargs):
        member = Account.objects.filter(id=pk).first()
        group = Group.objects.get(slug=slug)
        if group.admin.filter(username=member.username).exists():
            messages.add_message(
                self.request,
                messages.ERROR,
                f"{member.username} is already an admin"
            )
        elif group.admin.count() <= 3:
            group.admin.add(member)
            group.save()
            messages.add_message(
                self.request,
                messages.ERROR,
                f"You made {member.username} an admin"
            )
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                f"{group.name} has reached maximum number of admins"
            )
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER')
        )


class SuspendMemberView(LoginRequiredMixin, View):

    def post(self, request, slug, pk, **kwargs):
        try:
            if Group.objects.filter(slug=slug, owner_id=pk).exists():
                group = Group.objects.filter(slug=slug, owner_id=pk).first()
                messages.error(
                    request,
                    f"Can't suspend {group.owner.username} because they created this group"
                )
            else:
                group = Group.objects.get(slug=slug)
                member = Membership.objects.filter(
                    group=group,
                    user_id=pk
                ).first()
                print(member.is_suspended)
                member.is_suspended = not member.is_suspended
                member.save()
                if member.is_suspended:
                    messages.error(
                        request,
                        f"{member.user.username} has been suspended"
                    )
                else:
                    messages.error(
                        request,
                        f"{member.user.username} has been unsuspended"
                    )

            return HttpResponseRedirect(
                request.META.get('HTTP_REFERER')
            )

        except Group.DoesNotExist:
            messages.error(
                request,
                "No such group exist"
            )
            return HttpResponseRedirect(
                request.META.get('HTTP_REFERER')
            )



class AcceptJoinRequestView(LoginRequiredMixin, View):
    pass


class RejectJoinRequestView(LoginRequiredMixin, View):
    pass


class CreatePostView(LoginRequiredMixin, FormView):
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


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post


class PostDetailView(LoginRequiredMixin, View):
    pass


class CreateCommentView(LoginRequiredMixin, FormView):
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


class CreateReplyView(LoginRequiredMixin, CreateView):
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


class TogglePostLikeView(LoginRequiredMixin, View):

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


class ToggleCommentLikeVIew(LoginRequiredMixin, View):

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


class ToggleReplyLikeView(LoginRequiredMixin, View):

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


class TogglePostVisibilityView(LoginRequiredMixin, View):

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


class ToggleCommentVisibilityView(LoginRequiredMixin, View):

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
                "No such comment exists"
            )
            return HttpResponseRedirect(reverse(
                request.META.get('HTTP_REFERER')
            ))


class ToggleReplyVisibilityView(LoginRequiredMixin, View):

    def post(self, request, int, **kwargs):
        try:
            reply = Reply.objects.get(id=int)
            reply.is_hidden = not reply.is_hidden
            reply.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Reply.DoesNotExist:
            messages.add_message(
                self.request,
                messages.ERROR,
                "No such reply exists"
            )
            return HttpResponseRedirect(reverse(
                request.META.get('HTTP_REFERER')
            ))


class RemoveMemberView(LoginRequiredMixin, View):

    def post(self, request, slug, pk, **kwargs):
        group = Group.objects.filter(slug=slug).first()
        user = Account.objects.filter(id=pk).first()
        if Group.objects.filter(slug=slug, owner_id=pk).exists():
            messages.error(
                request,
                f"Can't remove {user.username} because they created this group"
            )
        elif Membership.objects.filter(user_id=pk).exists():
            group.admin.remove(user)
            Membership.objects.filter(user_id=pk).delete()
            # group.member.remove(user)
            group.save()
            messages.error(
                request,
                f"{user.username} is no longer a member of this group"
            )

        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER')
        )
