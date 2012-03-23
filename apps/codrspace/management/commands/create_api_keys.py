from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import translation
from tastypie.models import ApiKey


class Command(BaseCommand):
    """Create api keys for existing users"""

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            print "Creating api key for %s" % user
            ApiKey.objects.create(user=user)
