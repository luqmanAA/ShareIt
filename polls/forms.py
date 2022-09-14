from django import forms

from .models import Poll, Choice


class PollForm(forms.ModelForm):
    required_css_class = 'required-field'

    class Meta:
        model = Poll
        fields = ["poll_text", "start_date", "end_date"]

    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            new_data = {
                "class": "form-control"
            }
            self.fields[str(field)].widget.attrs.update(new_data)


class ChoicesForm(forms.ModelForm):
    required_css_class = 'required-field'
    choice_text = forms.CharField(required=False)

    class Meta:
        model = Choice
        fields = ['choice_text']

    def __init__(self, *args, **kwargs):
        super(ChoicesForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[str(field)].label = "New Choice"
