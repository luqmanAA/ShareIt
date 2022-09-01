from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic, View

from forum.models import Group

from .forms import PollForm, ChoiceForm
from .models import Poll, Choice


class PollListVIew(generic.ListView):
    model = Poll
    template_name = 'polls/polls_list.html'

    def get_queryset(self):
        group = Group.objects.filter(slug=self.kwargs['slug']).first()
        return Poll.objects.filter(group=group)

    # # def get(self, request, ):
    # #     polls = Poll.objects.order_by('-created_date')[:5]
    # #     print(polls)
    # #     context = {
    # #         "polls": polls
    # #     }
    #
    #     return render(request, "polls/polls_list.html", context)


class PollCreateView(View):
    def get(self, request, slug):
        context = {'slug':slug}
        return render(request,
                      "polls/poll_create_view.html",
                      context=context)

    def post(self, request, slug):
        poll_form = PollForm(request.POST)
        choice_form = ChoiceForm(request.POST)
        if poll_form.is_valid() and choice_form.is_valid():
            group = Group.objects.filter(slug=slug).first()
            data = Poll()
            data.poll_text = poll_form.cleaned_data["poll_text"]
            data.group = group
            data.poll_author = request.user
            data.save()

            choice_1 = choice_form.cleaned_data['choice_1']
            choice_2 = choice_form.cleaned_data['choice_2']
            choice_3 = choice_form.cleaned_data['choice_3']
            choice_4 = choice_form.cleaned_data['choice_4']

            Choice.objects.create(poll=data, choice_text=choice_1)
            Choice.objects.create(poll=data, choice_text=choice_2)
            Choice.objects.create(poll=data, choice_text=choice_3)
            Choice.objects.create(poll=data, choice_text=choice_4)
            messages.success(request, "Poll created successfully!")
            return redirect("polls:poll-list")
        else:
            messages.error(request, "There's error in your input(s)")
            context = {
                "poll_form":PollForm(request.POST),
                "choice_form": ChoiceForm(request.POST)
            }
            return render(request, "polls/poll_create_view.html", context)


class PollDetailView(View):
    # model = Poll
    # template_name = 'polls/polls_detail.html'

    def get(self, request, slug, pk, **kwargs):
        poll = Poll.objects.filter(id=pk).first()
        context = {'poll': poll}
        return render(
            request,
            'polls/polls_detail.html',
            context
        )




class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error("You didn't select an option")
        return render(request, 'polls/polls_list.html')
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(poll.get_absolute_url())
