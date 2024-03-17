# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
import pytest
from aineko_plugins.datasets.postgres.postgres import PostgresDataset

# pylint: disable=unused-argument


def test_new_read(database_with_table):
    cur = database_with_table.cursor()
    cur.execute("SELECT * FROM test_table")
    result = cur.fetchall()
    assert len(result) == 3
    cur.close()


def test_exists(database_with_table, postgres_db: PostgresDataset):
    """Test the exists method."""
    with postgres_db as dataset:
        assert dataset.exists() is True

    with postgres_db as dataset:
        dataset.delete(if_exists=True)
        assert dataset.exists() is False


def test_delete(
    database_with_table,
    postgres_db: PostgresDataset,
    subtests,
):
    """Test the delete method."""
    with subtests.test("Test delete without if_exists"):
        with postgres_db as dataset:
            assert dataset.exists() is True
            dataset.delete()
            assert dataset.exists() is False

    with subtests.test("Test delete with if_exists(True)"):
        with postgres_db as dataset:
            assert dataset.exists() is False
            dataset.create(
                schema={"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(255)"},
            )
            assert dataset.exists() is True
            dataset.delete(if_exists=True)
            assert dataset.exists() is False

    with subtests.test("Test delete with if_exists(False)"):
        with postgres_db as dataset:
            assert dataset.exists() is False
            with pytest.raises(Exception):
                dataset.delete(if_exists=False)


def test_create(database_without_table, postgres_db: PostgresDataset):
    """Test the create method."""
    with postgres_db as dataset:
        dataset.create(
            schema={"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(255)"},
        )
        assert postgres_db.exists()


def test_write(database_with_table, postgres_db: PostgresDataset):
    """Test the write method."""
    with postgres_db as dataset:
        dataset.write(
            query="INSERT INTO test_table (name) VALUES ('test')",
        )
        cur = database_with_table.cursor()
        cur.execute("SELECT * FROM test_table")
        result = cur.fetchall()
        assert len(result) == 4
        cur.close()


def test_read(database_with_table, postgres_db: PostgresDataset):
    """Test the read method."""
    with postgres_db as dataset:
        data = dataset.read(query="SELECT * FROM test_table")
        expected_data = ["foo", "bar", "baz"]
        assert len(data) == 3
        for row, expected in zip(data, expected_data):
            assert row[1] == expected
