import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from api.main import app
from database.session import get_db
from database.models import Base
from database import models

TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(TEST_DATABASE_URL,
                                  connect_args = {"check_same_thread": False},
                                  poolclass = StaticPool,
                                  echo = True
                                  )

TestingSessionLocal = sessionmaker(bind=engine_test, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(engine_test)
    Base.metadata.create_all(engine_test)
    
    yield  
    
    Base.metadata.drop_all(engine_test)

@pytest.fixture(scope="function")
def session() -> Session:
    with engine_test.connect() as connection:
        with connection.begin() as transaction:
            with TestingSessionLocal(bind=connection) as session:
                yield session
            transaction.rollback()

@pytest.fixture(scope="function")
def client(session: Session):
    def _get_test_db():
        yield session
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app=app, base_url="http://test") as ac:
        yield ac
        app.dependency_overrides.clear()