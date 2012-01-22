from datetime import datetime
from django import forms
from codrspace.models import Post, Media, Setting
from codrspace.utils import localize_date
from django.conf import settings


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'wmd-input'}),
        required=False
    )

    publish_dt = forms.DateTimeField(
        input_formats=['%a, %b %d %Y %I:%M %p'],
        required=False
    )

    class  Meta:
        model = Post

    def clean_publish_dt(self):
        date = self.cleaned_data['publish_dt']

        if date:
            date = localize_date(date, from_tz=self.timezone, to_tz=settings.TIME_ZONE)

        return date

    def __init__(self, *args, **kwargs):
        # checking for user argument here for a more
        # localized form
        self.user = None
        self.timezone = None

        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)

        super(PostForm, self).__init__(*args, **kwargs)

        # disable publish_dt if draft
        if not self.instance.status or self.instance.status == 'draft':
            self.fields['publish_dt'].widget.attrs['disabled'] = 'disabled'

        # get the published dt
        publish_dt = self.instance.publish_dt
        if not publish_dt:
            publish_dt = datetime.now()

        # adjust the date/time to the users preference
        if self.user and not self.user.is_anonymous():
            user_settings = Setting.objects.get(user=self.user)
            self.timezone = user_settings.timezone

            publish_dt = localize_date(publish_dt, to_tz=self.timezone)
        else:
            self.timezone = 'US/Central'
            publish_dt = localize_date(publish_dt, to_tz=self.timezone)

        self.initial['publish_dt'] = publish_dt


class MediaForm(forms.ModelForm):

    class  Meta:
        model = Media


class SettingForm(forms.ModelForm):

    class  Meta:
        model = Setting
