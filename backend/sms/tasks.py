from celery import shared_task


@shared_task
def send_sms_task(*, to, body):
    pass
