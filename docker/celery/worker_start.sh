set -e
cd /opt/code/
celery worker -A celery_worker.celery --loglevel=info