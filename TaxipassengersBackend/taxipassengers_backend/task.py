import os
import requests
from taxipassengers_backend import celery

SMS_URL = os.environ.get('SMS_URL', 'http://167.172.57.163:7048/api/me/message/')
EMAIL_URL = os.environ.get('EMAIL_URL', 'http://167.172.57.163:7049/api/me/mail/')


def init_celery(celery, app):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


@celery.task()
def send_sms(data, header):
    response = requests.post(url=SMS_URL, data=data, headers=header)
    print(response.status_code)
    print('SMS SENT')


@celery.task()
def send_email(data, headers):
    response = requests.post(url=EMAIL_URL, data=data, headers=headers)
    print(response.status_code)
    print('MAIL SENT')
