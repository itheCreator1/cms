import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="session")
def postgres_database_url():
    database_url = make_url(os.environ["DATABASE_URL"])
    test_database = f"cms_test_{uuid4().hex}"
    administrative_url = database_url.set(database="postgres")
    administrative_engine = create_engine(
        administrative_url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )

    with administrative_engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{test_database}"'))

    try:
        yield database_url.set(database=test_database).render_as_string(
            hide_password=False
        )
    finally:
        with administrative_engine.connect() as connection:
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{test_database}" WITH (FORCE)')
            )
        administrative_engine.dispose()
