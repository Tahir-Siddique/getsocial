import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getsocial.settings")
app = Celery("getsocial")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
