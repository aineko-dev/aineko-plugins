# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
import pytest
from aineko_plugins.datasets.postgres.postgres import AsyncPostgresDataset

# pylint: disable=unused-argument


def test_new_read(database_with_table):
    cur = database_with_table.cursor()
    cur.execute("SELECT * FROM test_table")
    result = cur.fetchall()
    assert len(result) == 3
    cur.close()


@pytest.mark.asyncio
async def test_exists(database_with_table, postgres_db: AsyncPostgresDataset):
    """Test the exists method."""
    async with postgres_db as dataset:
        assert await dataset.exists() is True

    async with postgres_db as dataset:
        await dataset.delete(if_exists=True)
        assert await dataset.exists() is False


@pytest.mark.asyncio
async def test_delete(
    database_with_table,
    postgres_db: AsyncPostgresDataset,
    subtests,
):
    """Test the delete method."""
    with subtests.test("Test delete without if_exists"):
        async with postgres_db as dataset:
            assert await dataset.exists() is True
            await dataset.delete()
            assert await dataset.exists() is False

    with subtests.test("Test delete with if_exists(True)"):
        async with postgres_db as dataset:
            assert await dataset.exists() is False
            await dataset.create(
                schema={"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(255)"},
            )
            assert await dataset.exists() is True
            await dataset.delete(if_exists=True)
            assert await dataset.exists() is False

    with subtests.test("Test delete with if_exists(False)"):
        async with postgres_db as dataset:
            assert await dataset.exists() is False
            with pytest.raises(Exception):
                await dataset.delete(if_exists=False)


@pytest.mark.asyncio
async def test_create(
    database_without_table, postgres_db: AsyncPostgresDataset
):
    """Test the create method."""
    async with postgres_db as dataset:
        await dataset.create(
            schema={"id": "SERIAL PRIMARY KEY", "name": "VARCHAR(255)"},
        )
        assert await postgres_db.exists()


@pytest.mark.asyncio
async def test_write(database_with_table, postgres_db: AsyncPostgresDataset):
    """Test the write method."""
    async with postgres_db as dataset:
        await dataset.write(
            query="INSERT INTO test_table (name) VALUES ('test')",
        )
        cur = database_with_table.cursor()
        cur.execute("SELECT * FROM test_table")
        result = cur.fetchall()
        assert len(result) == 4
        cur.close()


@pytest.mark.asyncio
async def test_read(database_with_table, postgres_db: AsyncPostgresDataset):
    """Test the read method."""
    async with postgres_db as dataset:
        data = await dataset.read(query="SELECT * FROM test_table")
        expected_data = ["foo", "bar", "baz"]
        assert len(data) == 3
        for row, expected in zip(data, expected_data):
            assert row[1] == expected
