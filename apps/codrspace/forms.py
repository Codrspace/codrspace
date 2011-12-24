from django import forms
from codrspace.models import Post, Media, Setting


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'wmd-input'}),
        required=False
    )

    class  Meta:
        model = Post


class MediaForm(forms.ModelForm):

    class  Meta:
        model = Media


class SettingForm(forms.ModelForm):

    class  Meta:
        model = Setting
