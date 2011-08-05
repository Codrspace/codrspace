from django import forms
from codrspace.models import Post, Media


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'wmd-input'
        }))
    class Meta:
        model = Post


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
