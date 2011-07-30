from django import forms
from codrspace.models import CodrSpace


class CodrForm(forms.ModelForm):

    class Meta:
        model = CodrSpace
