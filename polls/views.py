from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic, View

from forum.models import Group, Membership

from .forms import PollForm, ChoiceForm
from .models import Poll, Choice, Vote
from forum.views import GroupMixin


class PollListVIew(GroupMixin, generic.ListView):
    model = Poll
    template_name = 'polls/polls_list.html'

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        return Poll.objects.filter(group=group)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PollListVIew, self).get_context_data(**kwargs)
        votes = Vote.objects.filter(voter=self.request.user)
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        poll = Poll.objects.filter(group=group).first().start_date
        context["votes"] = votes
        context["slug"] = self.kwargs['slug']
        context["current_date"] = date.today()
        return context


class PollCreateView(GroupMixin, LoginRequiredMixin, View):
    def get(self, request, slug):
        poll_form = PollForm()
        choice_form = ChoiceForm()
        context = {
            'poll_form': poll_form,
            'choice_form': choice_form,
            'group': self.group,
            'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
        }
        return render(request,
                      "polls/poll_create_view.html",
                      context=context)

    def post(self, request, slug):
        print(request.POST)
        poll_form = PollForm(request.POST)
        choice_form = ChoiceForm(request.POST)
        for field in poll_form:
            print("Field Error:", field.name, field.errors)
        if poll_form.is_valid() and choice_form.is_valid():
            data = Poll()
            data.poll_text = poll_form.cleaned_data["poll_text"]
            data.start_date = poll_form.cleaned_data["start_date"]
            data.end_date = poll_form.cleaned_data["end_date"]
            data.group = self.group
            data.poll_author = request.user
            data.save()

            choice_1 = choice_form.cleaned_data.get("choice_1")
            choice_2 = choice_form.cleaned_data.get("choice_2")
            choice_3 = choice_form.cleaned_data.get("choice_3")
            choice_4 = choice_form.cleaned_data.get("choice_4")

            Choice.objects.create(poll=data, choice_text=choice_1)
            Choice.objects.create(poll=data, choice_text=choice_2)
            Choice.objects.create(poll=data, choice_text=choice_3)
            Choice.objects.create(poll=data, choice_text=choice_4)
            messages.success(request, "Poll created successfully!")
            return redirect("forum:polls:poll-list", slug=slug)
        else:
            messages.error(request, "There's error in your input(s). Verify your date formats")
            poll_form = PollForm(request.POST)
            choice_form = ChoiceForm(request.POST)
            context = {
                'poll_form': poll_form,
                'choice_form': choice_form,
                'group': self.group,
                'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
            }
            return render(request,
                          "polls/poll_create_view.html",
                          context=context)


class PollEditView(GroupMixin, View):
    def get(self, request, slug, pk):
        poll = get_object_or_404(Poll, pk=pk)
        poll_form = PollForm(instance=poll)
        choices = Choice.objects.filter(poll=poll)
        context = {
            'poll_form': poll_form,
            'choices': choices,
            'poll': poll,
            'group': self.group,
            'membership_checked': self.group.member.filter(user_id=self.request.user.id).exists()
        }
        return render(request, "polls/poll_edit.html", context)

    def post(self, request, slug, pk):
        poll = get_object_or_404(Poll, pk=pk)
        poll_form = PollForm(request.POST, instance=poll)
        choices = Choice.objects.filter(poll=poll)
        choice_form = ChoiceForm(request.POST)

        for choice in choices:
            choice.delete()

        if choice_form.is_valid() and poll_form.is_valid():
            choice_1 = choice_form.cleaned_data.get('choice_1')
            choice_2 = choice_form.cleaned_data.get('choice_2')
            choice_3 = choice_form.cleaned_data.get('choice_3')
            choice_4 = choice_form.cleaned_data.get('choice_4')

            Choice.objects.create(poll=poll, choice_text=choice_1)
            Choice.objects.create(poll=poll, choice_text=choice_2)
            Choice.objects.create(poll=poll, choice_text=choice_3)
            Choice.objects.create(poll=poll, choice_text=choice_4)

            poll_form.save()
            messages.success(request, "Your poll has been updated successfully.")
            return redirect("forum:polls:poll-list", slug)

        context = {
            "poll_form": poll_form,
            "poll": poll,
        }
        messages.error(request, "Form not valid")
        return render(request, "accounts/dashboard.html", context)


class PollDetailView(View):
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
