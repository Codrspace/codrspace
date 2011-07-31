from django import forms
from codrspace.models import Post, Media


class PostForm(forms.ModelForm):

    class Meta:
        model = Post


class MediaForm(forms.ModelForm):

    class Meta:
        model = Media