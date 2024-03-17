# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Aineko plugin for using PostgreSQL databases as datasets."""
import os
from types import TracebackType
from typing import Any, Dict, List, Optional, Type

import boto3
from aineko.core.dataset import (
    AbstractDataset,
    DatasetCreationStatus,
    DatasetError,
)
from mypy_boto3_rds import RDSClient
from psycopg import Cursor, errors, rows, sql
from psycopg.abc import Params, Query
from psycopg_pool import ConnectionPool


class AWSDatasetHelper:
    """Utility class for connecting to datasets on AWS."""

    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """Initialize the AWSDatasetHelper.

        The values for the AWS credentials and region name can be
        provided as arguments to the constructor. If not provided,
        the values will be read from the following environment variables:

            - AWS_ACCESS_KEY_ID
            - AWS_SECRET_ACCESS_KEY
            - AWS_REGION

        Args:
            aws_access_key_id: AWS access key ID.
            aws_secret_access_key: AWS secret access key.
            region_name: AWS region name.
        """
        self.aws_access_key_id = aws_access_key_id or os.environ.get(
            "AWS_ACCESS_KEY_ID"
        )
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        )
        self.region_name = region_name or os.environ.get("AWS_DEFAULT_REGION")

    def get_rds_endpoint(self, db_instance_identifier: str) -> str:
        """Get the RDS endpoint for a given RDS instance.

        Args:
            db_instance_identifier: RDS instance identifier.
        """
        rds_client: RDSClient = boto3.client(
            "rds",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )
        db_instances = rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_identifier
        )
        db_instance = db_instances["DBInstances"][0]
        return db_instance["Endpoint"]["Address"]


class PostgresDataset(AbstractDataset):
    """Synchronous dataset for interacting with a PostgreSQL table.

    Example usage:
        ```python
        with PostgresDataset(
            name="my_table",
            host="localhost",
            dbname="my_db",
            user="my_user",
            password="my_password",
        ) as dataset:
            result = dataset.read("SELECT * FROM my_table")
            print(result)
        ```
    """

    def __init__(
        self,
        name: str,
        host: str,
        dbname: str,
        user: str,
        password: str,
    ):
        """Initialize the PostgresDataset.

        Args:
            name: Name of the table in the database.
            host: Hostname of the database server.
            dbname: Name of the database.
            user: Username to connect to the database.
            password: Password to connect to the database.
        """
        self.name = name
        self._host = host
        self._dbname = dbname
        self._user = user
        self._password = password

        self._pool: ConnectionPool

    def __enter__(self) -> "PostgresDataset":
        """Context manager entry point for PostgresDataset.

        This method is automatically called when the 'with' statement is used
        with an instance of PostgresDataset. It initializes a synchronous
        connection pool to the PostgreSQL database and opens the connection.

        Returns:
            An instance of PostgresDataset with an open connection pool.
        """
        self._pool = ConnectionPool(
            f"dbname={self._dbname} user={self._user} password={self._password}"
            f" host={self._host}",
            open=False,
        )
        self._pool.open()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """Ccontext manager exit point for PostgresDataset.

        This method is automatically called when the 'with' statement is
        exited. It closes the connection pool to the PostgreSQL database.
        """
        if self._pool.closed is False:
            self._pool.close()

    def initialize(self) -> None:
        # TODO: figure out how to handle this
        raise NotImplementedError("Use async context manager instead.")

    def create(
        self,
        schema: Dict[str, str],
        extra_commands: str = "",
    ) -> DatasetCreationStatus:
        """Create a new postgres table.

        Executes the SQL command:

            ```SQL
            CREATE TABLE table_name (column_name column_type, ...)
            ```

        Extra SQL commands can be supplied and will be added to
        the back.

        Args:
            schema: mapping between column name and column
                type. Type must be a valid SQL type.
            extra_commands: extra SQL commands to be added
                to the table creation query.
        """
        query = sql.SQL(
            "CREATE TABLE {name} ({schema}) {extra_commands};"
        ).format(
            name=sql.Identifier(self.name),
            schema=sql.SQL(
                (",").join([f"{key} {value}" for key, value in schema.items()])
            ),
            extra_commands=sql.SQL(extra_commands),
        )
        self.execute_query(query)
        return DatasetCreationStatus(dataset_name=self.name)

    def read(self, query: Query) -> List[Any]:
        """Performs a read operation on the Postgres database.

        Args:
            query: SQL query to execute.

        Returns:
            A list of rows returned by the query.
        """
        cursor = self.execute_query(query=query)
        return cursor.fetchall()

    def write(
        self,
        query: Query,
        parameters: Optional[Params] = None,
    ) -> Optional[List]:
        """Performs a write operation on the Postgres database.

        Args:
            query: SQL query to execute.
            parameters: Parameters to be passed to the query. Defaults to None.

        Returns:
            A list of rows returned by the query if the query produced results.
            None otherwise.
        """
        cursor = self.execute_query(query, parameters=parameters)
        try:
            return cursor.fetchall()
        except errors.ProgrammingError as e:
            if "the last operation didn't produce a result" in str(e):
                return None
            raise e

    def delete(self, if_exists: bool = False) -> None:
        """Drops the table from the Postgres database.

        Args:
            if_exists: If table does not exist, do not raise error.
                Defaults to False.
        """
        if if_exists:
            query = "DROP TABLE IF EXISTS {name};"
        else:
            query = "DROP TABLE {name};"

        self.execute_query(
            sql.SQL(query).format(name=sql.Identifier(self.name)),
        )

    def exists(self) -> bool:
        """Queries the database to check if the table exists.

        Returns:
            True if the table exists, False otherwise.
        """
        cursor = self.execute_query(
            query="""
                    SELECT EXISTS(
                        SELECT FROM information_schema.tables
                        WHERE table_name = %(name)s);
                    """,
            parameters={"name": self.name},
        )
        result = cursor.fetchone()
        if result:
            return bool(result[0])
        return False

    def execute_query(
        self,
        query: Query,
        parameters: Optional[Params] = None,
    ) -> Cursor[rows.TupleRow]:
        """Handles execution of PostgreSQL queries.

        Args:
            query: SQL query to execute.
            parameters: Parameters to be passed to the query. Defaults to None.

        Returns:
            Cursor: Cursor object for the executed query. Can be used to
                         fetch results.

        Raises:
            DatasetError: If the query execution fails for any reason.
        """
        with self._pool.connection() as conn:
            try:
                cursor: Cursor = conn.execute(query=query, params=parameters)
                conn.commit()
                return cursor
            except Exception as exc:
                conn.rollback()
                raise DatasetError(
                    f"Failed to execute query: {query!r}"
                ) from exc

    def setup_test_mode(self) -> None:
        raise NotImplementedError("Test mode not yet implemented.")
