import os
import pytest

from app.settings import settings
from typing import Any, Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import get_application
from app.database.database import Base, get_db
from app.models.all_models import *


engine = create_engine(
    # settings.get_database_url(),
    settings.db_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a fresh database on each test case.
    """
    print ("------ test_conf:app() -------")
    Base.metadata.create_all(engine)  # Create the tables.
    _app = get_application()
    print ("------ test_conf:app()--yield -------")
    yield _app
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(app: FastAPI) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """
    print ("------ test_conf:db_session() -------")
    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


# def override_get_db():
#     try:
#         db = SessionTesting()
#         yield db
#     finally:
#         db.close()

# @pytest.fixture(scope='session')
# def conf():
#     # app = create_app(config_object=TestConfig)
#     with app.app_context():
#         Base.metadata.create_all()  # Create tables in the in-memory database
#         yield app
#         Base.metadata.drop_all()  # Clean up after tests

# @pytest.fixture(scope='function')
# def client(app):
#     return app.test_client()

# @pytest.fixture(scope='function')
# def session(app):
#     with app.app_context():
#         connection = db.engine.connect()
#         transaction = connection.begin()
#         options = dict(bind=connection, binds={})
#         session = db.create_scoped_session(options=options)
#         db.session = session
#         yield session
#         transaction.rollback()  # Rollback changes after each test
#         session.remove()

