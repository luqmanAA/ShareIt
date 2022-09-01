from django import forms
from .models import Poll, Choice


class PollForm(forms.Form):
    poll_text = forms.CharField(max_length=200, required=True)



class ChoiceForm(forms.Form):
    choice_1 = forms.CharField(max_length=50, required=True)
    choice_2 = forms.CharField(max_length=50, required=True)
    choice_3 = forms.CharField(max_length=50, required=False)
    choice_4 = forms.CharField(max_length=50, required=False)


