# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Aineko plugin for using Ray Queue as datasets."""

from typing import Any, Dict, List, Literal, Optional

import ray
from aineko.core.dataset import AbstractDataset, DatasetCreationStatus
from ray.util.queue import Queue


class RayDataset(AbstractDataset):
    def __init__(self, name: str, params: Dict[str, Any], test: bool = False):
        self.name = name
        self.test = test

    def read(self) -> Any:
        """Read an entry from the Ray Queue dataset."""
        return ray.get(self.queue_actor.get.remote(block=False))

    def write(self, message: dict) -> Any:
        """Write an entry to the Ray Queue dataset."""
        self.queue_actor.put.remote(message)

    def create(
        self,
        dataset_prefix: Optional[str] = None,
    ) -> DatasetCreationStatus:
        """Create the Ray Queue dataset storage layer."""
        self.queue_actor = (
            ray.remote(Queue)
            .options(name=self.name, lifetime="detached")
            .remote()
        )

        return DatasetCreationStatus(dataset_name=self.name)

    def delete(self) -> Any:
        """Delete the Ray Queue dataset storage layer."""
        self.queue_actor.shutdown.remote()

    def initialize(
        self,
        create: Literal["consumer", "producer"],
        node_name: str,
        pipeline_name: str,
        prefix: Optional[str] = None,
        has_pipeline_prefix: bool = False,
    ) -> None:
        """Subclass implementation to initialize the dataset query layer."""

        if has_pipeline_prefix:
            actor_name = f"{pipeline_name}.{self.name}"
        else:
            actor_name = self.name

        if create == "producer":
            self.queue_actor = ray.get_actor(actor_name)
        elif create == "consumer":
            self.queue_actor = ray.get_actor(actor_name)

    def exists(self) -> bool:
        """Subclass implementation to check if the dataset exists."""
        return True

    def setup_test_mode(
        self,
        source_node: str,
        source_pipeline: str,
        input_values: Optional[List[dict]] = None,
    ) -> None:
        """Subclass implementation to set up the dataset for testing."""
        raise NotImplementedError
