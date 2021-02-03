from taxipassengers_backend.app import create_app
import taxipassengers_backend as app

application = create_app(celery=app.celery)
application.app_context().push()
