# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Fixtures for aineko-plugins"""
import os

import pytest
from aineko import ConfigLoader, Runner
from aineko.__main__ import cli
from click.testing import CliRunner


@pytest.fixture(scope="module")
def conf_directory():
    """Config directory fixture.

    Returns:
        str: Path to config directory
    """
    return os.path.join(os.path.dirname(__file__), "conf")


@pytest.fixture(scope="module")
def config_loader(test_pipeline_config_file: str):
    """Config loader fixture.

    Returns:
        ConfigLoader: Test config loader
    """
    return ConfigLoader(
        pipeline_config_file=test_pipeline_config_file,
    )


@pytest.fixture(scope="module")
def runner(test_pipeline_config_file: str):
    """Runner fixture.

    Returns:
        Runner: Test runner
    """
    return Runner(pipeline_config_file=test_pipeline_config_file)


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
