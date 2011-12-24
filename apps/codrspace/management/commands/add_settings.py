from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from codrspace.models import Setting


class Command(BaseCommand):
    """
    Adds a setting entry for all users
    Note: one time script
    """
    def handle(self, *args, **options):
        verbosity = options['verbosity']
        users = User.objects.all()
        user_count = 0

        # add settngs for all users
        for user in users:
            setting = Setting.objects.filter(user=user)
            if not setting:
                s = Setting()
                s.user = user
                s.timezone = "US/Central"
                s.save()
                user_count += 1
                if verbosity >= 2:
                    print "Adding setting for user (%s)." % user.username
            else:
                if verbosity >= 2:
                    print 'User (%s) already has settings' % user.username
        
        print 'Added settings for %s users' % user_count
