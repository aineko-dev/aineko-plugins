# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Fixtures for aineko-plugins"""
import pytest
from aineko.__main__ import cli
from click.testing import CliRunner


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
