from django import forms
from codrspace.models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
