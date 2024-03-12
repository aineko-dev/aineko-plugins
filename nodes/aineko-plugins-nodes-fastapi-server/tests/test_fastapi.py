# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Tests that a pipeline with the FastAPI app runs correctly."""
import os
import time
from pathlib import Path

import pytest
import ray
import requests
from aineko import AbstractNode, Runner
from aineko.datasets.kafka import KafkaDataset


class FastAPIChecker(AbstractNode):
    """Node that checks that the FastAPI server is running."""

    def _execute(self, params: dict):
        """Checks that the FastAPI server is running."""
        results = {}

        time.sleep(5)

        response = requests.get("http://localhost:8000/write")
        results["write"] = response.status_code

        response = requests.get("http://localhost:8000/next")
        results["next"] = response.json()

        response = requests.get("http://localhost:8000/last")
        results["last"] = response.json()

        response = requests.get("http://localhost:8000/health")
        results["health"] = response.status_code

        self.outputs["test_result"].write(results)

        self.activate_poison_pill()


@pytest.mark.integration
def test_fastapi_node(start_service):
    """Integration test to check that FastAPI node works.

    Spin up a pipeline containing the fastapi node and a FastAPIChecker
    node that queries the api server using the fastapi endpoints.
    The FastAPIChecker node uses the endpoints to write messages and
    other ones to read messages.
    """

    test_config = Path(os.path.dirname(__file__)) / "test_fastapi.yml"
    runner = Runner(pipeline_config_file=test_config)
    try:
        runner.run()
    except ray.exceptions.RayActorError:
        # This is expected because we activated the poison pill
        pass

    dataset = KafkaDataset(name="test_result", params={})
    dataset.create()
    dataset.initialize(
        create="consumer",
        node_name="consumer",
        pipeline_name="test_fastapi",
        has_pipeline_prefix=True,
    )

    test_results = dataset.next()
    assert test_results["message"]["write"] == 200
    assert test_results["message"]["next"]["message"] == 1
    assert test_results["message"]["last"]["message"] == 3
    assert test_results["message"]["health"] == 200
