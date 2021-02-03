import pytest
from faker import Faker

from taxipassengers_backend.app import create_app

fake = Faker()


@pytest.fixture
def app():
    application = create_app()

    application.app_context().push()
    # Initialise the DB
    application.db.create_all()

    return application
