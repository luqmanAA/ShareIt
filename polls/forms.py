from django import forms
from .models import Poll, Choice


class PollForm(forms.ModelForm):

    class Meta:
        model = Poll
        fields = ["poll_text", "start_date", "end_date"]

    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        self.fields["start_date"].widget.attrs["placeholder"] = "mm/dd/yyyy"
        self.fields["end_date"].widget.attrs["placeholder"] = "mm/dd/yyyy"


class ChoiceForm(forms.Form):
    choice_1 = forms.CharField(max_length=50, required=True)
    choice_2 = forms.CharField(max_length=50, required=True)
    choice_3 = forms.CharField(max_length=50, required=False)
    choice_4 = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        super(ChoiceForm, self).__init__(*args, **kwargs)
        self.fields["choice_3"].widget.attrs["placeholder"] = "Not required"
        self.fields["choice_4"].widget.attrs["placeholder"] = "Not required"



