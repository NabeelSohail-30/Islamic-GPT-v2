from django import forms
from .models import New_Data


class NewDataForm(forms.ModelForm):
    class Meta:
        model = New_Data
        fields = ['data']
