from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib import messages

from .models import Event


class DateForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )


class EventCreation(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['name', 'location', 'Cover_image', 'description', 'start_date_time', 'end_date_time', ]

    def clean(self):
        print(self.cleaned_data)
        start_date_time = self.cleaned_data.get('start_date_time')
        end_date_time = self.cleaned_data.get('end_date_time')
        if start_date_time < timezone.now():
            raise ValidationError('Invalid event start date')
        elif end_date_time <= start_date_time:
            raise ValidationError('Invalid event end date')
        return start_date_time, end_date_time

    # def clean_end_date_time(self):
    #     if end_date_time <= self.clean_start_date_time():
    #         raise ValidationError('Invalid event end date')
    #     return end_date_time