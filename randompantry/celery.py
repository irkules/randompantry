from __future__ import absolute_import, unicode_literals

from celery import Celery
from celery.bin.celery import CeleryCommand
from celery.signals import worker_ready
from os import environ


# set the default Django settings module for the 'celery' program.
environ.setdefault('DJANGO_SETTINGS_MODULE', 'randompantry.settings')

app = Celery('randompantry')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


celery_is_running = False

@worker_ready.connect
def set_running(*args, **kwargs):
    celery_is_running = True
