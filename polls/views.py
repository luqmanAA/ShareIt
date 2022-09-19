from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.forms.models import modelformset_factory  # modelform for querysets
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic, View

from forum.models import Group, Membership

from .forms import PollForm, ChoicesForm
from .models import Poll, Choice, Vote
from forum.views import GroupMixin


class PollListVIew(GroupMixin, generic.ListView):
    model = Poll
    template_name = 'polls/polls_list.html'

    def get_queryset(self):
        return Poll.objects.filter(group=self.group).order_by("-created_date")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PollListVIew, self).get_context_data(**kwargs)
        votes = Vote.objects.filter(voter=self.request.user)
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        # poll = Poll.objects.filter(group=group).first().start_date
        context["votes"] = votes
        context["slug"] = self.kwargs['slug']
        context["current_date"] = date.today()
        return context


class PollCreateView(GroupMixin, LoginRequiredMixin, View):
    def get(self, request, slug):
        poll_form = PollForm()
        ChoiceFormset = formset_factory(ChoicesForm, extra=3)
        formset = ChoiceFormset()
        context = {
            'poll_form': poll_form,
            'formset': formset,
            'group': self.group,
            'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
        }
        return render(request,
                      "polls/poll_create_view.html",
                      context=context)

    def post(self, request, slug):
        poll_form = PollForm(request.POST)
        ChoiceFormset = formset_factory(ChoicesForm, extra=0)
        formset = ChoiceFormset(request.POST or None)

        if all([poll_form.is_valid(), formset.is_valid()]):
            if request.user in self.group.admin.all():
                parent = poll_form.save(commit=False)
                parent.poll_author = self.request.user
                parent.group = self.group
                parent.save()
                for form in formset:
                    child = form.save(commit=False)
                    child.poll = parent
                    child.save()
                messages.success(request, "Your poll has been created successfully.")
                return redirect("forum:polls:poll-list", slug)
            else:
                messages.error(request, "You are not allowed to edit this poll.")
                return HttpResponseForbidden()
        else:
            messages.error(request, "There's error in your input(s). Verify your date formats")
            poll_form = PollForm(request.POST)
            ChoiceFormset = formset_factory(ChoicesForm, extra=0)
            formset = ChoiceFormset(request.POST or None)
            context = {
                'poll_form': poll_form,
                'formset': formset,
                'group': self.group,
                'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
            }
            return render(request,
                          "polls/poll_create_view.html",
                          context=context)


class PollEditView(GroupMixin, LoginRequiredMixin, View):
    def get(self, request, slug, pk):
        poll = get_object_or_404(Poll, pk=pk)
        poll_form = PollForm(instance=poll)
        ChoiceFormset = modelformset_factory(Choice, form=ChoicesForm, extra=0)
        choices_qs = poll.choice_set.all()
        # delete all empty choices
        for choice in choices_qs:
            if not choice.choice_text:
                choice.delete()
        formset = ChoiceFormset(request.POST or None, queryset=choices_qs)
        context = {
            'poll_form': poll_form,
            'formset': formset,
            'poll': poll,
            'group': self.group,
            'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
        }
        return render(request, "polls/poll_edit.html", context)

    def post(self, request, slug, pk):
        poll = get_object_or_404(Poll, pk=pk)
        poll_form = PollForm(request.POST, instance=poll)
        ChoiceFormset = modelformset_factory(Choice, form=ChoicesForm, extra=0)
        choices_qs = poll.choice_set.all()
        formset = ChoiceFormset(request.POST or None, queryset=choices_qs)

        if all([poll_form.is_valid(), formset.is_valid()]):
            if request.user in self.group.admin.all():
                parent = poll_form.save(commit=False)
                parent.save()
                for form in formset:
                    child = form.save(commit=False)
                    child.poll = parent
                    child.save()
                messages.success(request, "Your poll has been updated successfully.")
                return redirect("forum:polls:poll-list", slug)
            else:
                messages.error(request, "You are not allowed to edit this poll.")
                return HttpResponseForbidden()
        context = {
            'poll_form': poll_form,
            'formset': formset,
            'poll': poll,
            'group': self.group,
            'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
        }
        messages.error(request, "Form not valid. No field should be empty.")
        return render(request, "polls/poll_edit.html", context)


class PollDetailView(LoginRequiredMixin, View):
    model = Poll
    template_name = 'polls/polls_detail.html'
    poll_id = 0

    def get(self, request, slug, pk, **kwargs):
        poll = Poll.objects.filter(id=pk).first()
        votes = Vote.objects.filter(voter=self.request.user)
        context = {
            'poll': poll,
            'votes': votes,
        }
        return render(
            request,
            'polls/polls_detail.html',
            context
        )


class ResultsView(GroupMixin, LoginRequiredMixin, generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        return Poll.objects.filter(group=group)

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context["current_date"] = date.today()
        return context


class VoteView(View, LoginRequiredMixin):

    def post(self, request, poll_id, slug, **kwargs):
        current_date = date.today()
        poll = get_object_or_404(Poll, pk=poll_id)
        if Membership.objects.get(user=request.user, group=poll.group).is_suspended == True:
            return redirect(f"/group/{slug}/polls/{poll.id}/results/?command=eligibility&sl={poll.group.slug}")

        if poll.start_date > current_date:
            return redirect(f"/group/{slug}/polls/{poll.id}/results/?command=session_resume&sl={poll.group.slug}")

        if poll.end_date < current_date:
            return redirect(f"/group/{slug}/polls/{poll.id}/results/?command=session_ended&sl={poll.group.slug}")

        if Vote.objects.filter(poll_id=poll_id, voter_id=request.user.id).exists():
            return redirect(f"/group/{slug}/polls/{poll.id}/results/?command=verification&sl={poll.group.slug}")
        try:
            selected_choice = poll.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            messages.error(request, "You didn't select an option")
            return render(request, 'polls/polls_list.html')
        else:
            selected_choice.votes += 1
            selected_choice.save()
            Vote.objects.create(voter=request.user, poll=poll, choice=selected_choice)
            messages.success(request, "Your vote has been successfully recorded")
            return HttpResponseRedirect(poll.get_absolute_url())
