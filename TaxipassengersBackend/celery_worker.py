from taxipassengers_backend import celery
from taxipassengers_backend.app import create_app
from taxipassengers_backend.task import init_celery

app = create_app()

init_celery(celery, app)
