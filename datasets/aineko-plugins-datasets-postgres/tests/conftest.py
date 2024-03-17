# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Fixtures for aineko-plugins-datasets-postgres tests."""
import psycopg
import pytest
from aineko.__main__ import cli
from aineko_plugins.datasets.postgres.postgres import PostgresDataset
from click.testing import CliRunner
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor

pytest.register_assert_rewrite("pytest_docker_fixtures")
from pytest_docker_fixtures import (  # pylint: disable=wrong-import-position
    images,
)

pytest_plugins = ["pytest_docker_fixtures"]
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="function")
def start_service():
    """Start Aineko service fixture for integration tests.

    The service is started before the test and stopped after the test.
    """
    cli_runner = CliRunner()
    result = cli_runner.invoke(cli, ["service", "restart", "--hard"])
    assert result.exit_code == 0
    yield
    result = cli_runner.invoke(cli, ["service", "down"])


images.configure(
    name="postgresql",
    image="postgres",
    version="latest",
    env={
        "POSTGRES_PASSWORD": "mysecretpassword",
        "POSTGRES_USER": "postgres",
    },
    options={"ports": {"5432": 5432}},
)


postgresql_in_docker = factories.postgresql_noproc(
    password="mysecretpassword", dbname="test"
)


@pytest.fixture
def database_with_table(pg, postgresql_in_docker):
    """Create a connected instance of the Postgres dataset with a test table.

    This fixture is used to test the Postgres dataset with a dockerized database
    and pre-created table named `test_table`. The table has 3 rows with the
    following values: `foo`, `bar`, `baz`.

    Upon completion of the test, all tables are deleted and the container is
    stopped.
    """
    with DatabaseJanitor(
        user=postgresql_in_docker.user,
        host=postgresql_in_docker.host,
        port=postgresql_in_docker.port,
        dbname=postgresql_in_docker.dbname,
        version=postgresql_in_docker.version,
        password=postgresql_in_docker.password,
    ):
        conn = psycopg.connect(
            dbname=postgresql_in_docker.dbname,
            user=postgresql_in_docker.user,
            password=postgresql_in_docker.password,
            host=postgresql_in_docker.host,
            port=postgresql_in_docker.port,
        )
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE test_table (id serial PRIMARY KEY, name "
            "VARCHAR(255));"
        )
        cur.execute(
            "INSERT INTO test_table (name) VALUES ('foo'), ('bar'), ('baz')"
        )
        conn.commit()
        yield psycopg.connect(
            dbname=postgresql_in_docker.dbname,
            user=postgresql_in_docker.user,
            password=postgresql_in_docker.password,
            host=postgresql_in_docker.host,
            port=postgresql_in_docker.port,
        )


@pytest.fixture
def database_without_table(pg, postgresql_in_docker):
    """Create a connected instance of the Postgres dataset without a test table.

    This fixture is used to test the Postgres dataset with a dockerized database
    and no pre-created table. Upon completion of the test, all tables are
    deleted and the container is stopped.
    """
    with DatabaseJanitor(
        user=postgresql_in_docker.user,
        host=postgresql_in_docker.host,
        port=postgresql_in_docker.port,
        dbname=postgresql_in_docker.dbname,
        version=postgresql_in_docker.version,
        password=postgresql_in_docker.password,
    ):
        yield psycopg.connect(
            dbname=postgresql_in_docker.dbname,
            user=postgresql_in_docker.user,
            password=postgresql_in_docker.password,
            host=postgresql_in_docker.host,
            port=postgresql_in_docker.port,
        )


@pytest.fixture
def postgres_db(postgresql_in_docker) -> PostgresDataset:
    """Create an instance of the Postgres dataset with predefined parameters."""
    dataset = PostgresDataset(
        name="test_table",
        host=postgresql_in_docker.host,
        dbname=postgresql_in_docker.dbname,
        user=postgresql_in_docker.user,
        password=postgresql_in_docker.password,
    )
    return dataset
