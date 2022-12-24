
import time
from celery import shared_task

from apis.models import CustomUser
from .support_functions import enrich_user


@shared_task()
def enrich_data(user_id):
    print(user_id)
    time.sl
    user = CustomUser.objects.get(id=user_id)
    enrich_user(user, user.ip_address)
    print("Completed")
