from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from timezones.utils import adjust_datetime_to_timezone
from codrspace.models import Post, Media

FROM_TZ = 'US/Central'
TO_TZ = 'GMT'


class Command(BaseCommand):
    """
    Convert the timezones from CST to GMT for all models
    Note: One time script.
    """
    tz_params = {
        'from_tz': FROM_TZ,
        'to_tz': TO_TZ
    }

    def adjust_tz(self, dt):
        dt = adjust_datetime_to_timezone(dt, **self.tz_params)
        dt = dt.replace(tzinfo=None)
        return dt

    def handle(self, *args, **options):
        verbosity = options['verbosity']

        # Ajust all the user account timezones
        users = User.objects.all()
        for u in users:
            if verbosity >= 2:
                print 'Converting dates for user (%s)' % u.username
            u.last_login = self.adjust_tz(u.last_login)
            u.date_joined = self.adjust_tz(u.date_joined)
            u.save()

        # Adjust all the post timezones
        posts = Post.objects.all()
        for p in posts:
            if verbosity >= 2:
                print 'Converting post id (%s)' % p.pk
            p.publish_dt = self.adjust_tz(p.publish_dt)
            p.create_dt = self.adjust_tz(p.create_dt)
            p.update_dt = self.adjust_tz(p.update_dt)
            p.save()

        # Adjust all the post media timezones
        media_files = Media.objects.all()
        for m in media_files:
            if verbosity >= 2:
                print 'Converting media post id (%s)' % m.pk
            m.upload_dt = self.adjust_tz(m.upload_dt)
            m.save()

        

