import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

os.environ["DJANGO_SETTINGS_MODULE"] = "dash.settings"

from django.conf import settings

sys.path.insert(0, join(settings.PROJECT_ROOT))

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()