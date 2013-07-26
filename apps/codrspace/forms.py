from datetime import datetime
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.utils.text import slugify

from codrspace.models import Post, Media, Setting, STATUS_CHOICES
from codrspace.utils import localize_date

VALID_STATUS_CHOICES = ', '.join([sc[0] for sc in STATUS_CHOICES])


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'wmd-input'}),
        required=False
    )

    publish_dt = forms.DateTimeField(
        input_formats=['%a, %b %d %Y %I:%M %p'],
        required=False
    )

    class Meta:
        model = Post

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        posts = Post.objects.filter(slug=slug, author=self.user)

        if len(posts) > 0:
            if self.instance:
                for post in posts:
                    if post.pk == self.instance.pk:
                        return slug

            msg = 'You already have a post with this slug "%s"' % (slug)
            raise forms.ValidationError(msg)

        return slug

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

        # add span class to charfields
        for field in self.fields.values():
            if isinstance(field, forms.fields.CharField):
                if 'class' in field.widget.attrs:
                    field.widget.attrs['class'] = "%s %s" % (
                        field.widget.attrs['class'],
                        'span8',
                    )
                else:
                    field.widget.attrs['class'] = 'span8'

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


class APIPostForm(forms.ModelForm):
    title = forms.CharField(max_length=200, required=True)
    content = forms.CharField(required=False)
    slug = forms.SlugField(max_length=75, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, error_messages={
        'invalid_choice': 'Please use a valid status. Valid choices are %s' % VALID_STATUS_CHOICES
    })
    publish_dt = forms.DateTimeField(required=False)
    create_dt = forms.DateTimeField(required=False)
    update_dt = forms.DateTimeField(required=False)

    class Meta:
        model = Post

    def __init__(self, *args, **kwargs):
        self.user = None

        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)

        # call the original init
        super(APIPostForm, self).__init__(*args, **kwargs)

        # order the fields so that the clean_field gets called in
        # a specific order which makes validation easier
        ordered_fields = OrderedDict([
            ('title', self.fields['title'],),
            ('content', self.fields['content'],),
            ('slug', self.fields['slug'],),
            ('publish_dt', self.fields['publish_dt'],),
            ('status', self.fields['status'],),
            ('create_dt', self.fields['create_dt'],),
            ('update_dt', self.fields['update_dt'],),
        ])
        self.fields = ordered_fields

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        title = self.cleaned_data['title']

        # autogenerate a slug if it isn't provided
        if not self.instance.pk and not slug:
            slug = slugify(title)

        posts = Post.objects.filter(slug=slug, author=self.user)

        if len(posts) > 0:
            if self.instance.pk:
                for post in posts:
                    if post.pk == self.instance.pk:
                        return slug

            dup_post = posts[0]
            msg = 'You already have a post with this slug "%s" (id: %d)' % (
                                                             slug, dup_post.pk)
            raise forms.ValidationError(msg)

        return slug

    def clean_status(self):
        status = self.cleaned_data['status']
        publish_dt = None

        if 'publish_dt' in self.cleaned_data:
            publish_dt = self.cleaned_data['publish_dt']

        if status == 'published' and not publish_dt:
            raise forms.ValidationError(
                'Please set the publish date/time (publish_dt) if status is set to published. Note that publish_dt is in UTC. (GMT)'
            )

        return status


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media


class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting

    def __init__(self, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.fields.CharField):
                field.widget.attrs.update({'class': 'span10'})


class FeedBackForm(forms.Form):
    email = forms.EmailField(required=True)
    comments = forms.CharField(widget=forms.Textarea(), required=True)

    def __init__(self, *args, **kwargs):
        super(FeedBackForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, forms.fields.CharField):
                field.widget.attrs.update({'class': 'span10'})
