# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Main module for running a FastAPI server with Aineko.

This module contains the inputs and outputs class that give access to the
node's inputs and outputs from within the FastAPI app. It also contains the
FastAPI node class that runs the uvicorn server.

We recommend no more than 1 FastAPI node per pipeline since the Inputs and
Outputs objects are namespaced at the pipeline level. If you must have multiple
FastAPI nodes, we recommend using different datasets to avoid namespace
collisions.
"""

from typing import Optional, Union

import uvicorn
from aineko import AbstractNode
from aineko.core.dataset import AbstractDataset


class Inputs(dict):
    """Class to contain inputs."""

    def __setitem__(
        self, key: Union[str, int, tuple], value: AbstractDataset
    ) -> None:
        """Checks that item is of type AbstractDataset before setting.

        Args:
            key: Name of the dataset
            value: AbstractDataset object to be stored

        Raises:
            ValueError: If value is not a subtype of AbstractDataset
        """
        if not isinstance(value, AbstractDataset):
            raise ValueError(
                f"Value must be a subtype of AbstractDataset, not {type(value)}"
            )
        super().__setitem__(key, value)


class Outputs(dict):
    """Class to contain outputs."""

    def __setitem__(
        self, key: Union[str, int, tuple], value: AbstractDataset
    ) -> None:
        """Checks that item is of type AbstractDataset before setting.

        Args:
            key: Name of the dataset
            value: AbstractDataset object to be stored

        Raises:
            ValueError: If value is not a subtype of AbstractDataset
        """
        if not isinstance(value, AbstractDataset):
            raise ValueError(
                f"Value must be a subtype of AbstractDataset, not {type(value)}"
            )
        super().__setitem__(key, value)


inputs = Inputs()
outputs = Outputs()


class FastAPI(AbstractNode):
    """Node for creating a FastAPI app with a gunicorn server.

    `node_params` should contain the following keys:

        app: path to FastAPI app
        port (optional): port to run the server on. Defaults to 8000.
        log_level (optional): log level to log messages from the uvicorn server.
            Defaults to "info".

    To access the inputs and outputs from your FastAPI app, import the `inputs`
    and `outputs` variables from `aineko_plugins.nodes.fastapi_server`. Use
    them as you would use `self.inputs` and `self.outputs` in a regular node.

    We recommend no more than 1 FastAPI node per pipeline since the Inputs and
    Outputs objects are namespaced at the pipeline level.

    Example usage in pipeline.yml:
    ```yaml title="pipeline.yml"
    pipeline:
      nodes:
        fastapi:
          class: aineko_plugins.nodes.fastapi_server.FastAPI
          inputs:
            - test_sequence
          node_params:
            app: my_awesome_pipeline.fastapi:app
            port: 8000
    ```
    where the app points to a FastAPI app. See
    [FastAPI documentation](https://fastapi.tiangolo.com/){:target="_blank"}
    on how to create a FastAPI app.

    Example usage in FastAPI app:
    ```python title="fastapi.py"
    from aineko_plugins.nodes.fastapi_server import inputs, outputs

    @app.get("/query")
    async def query():
        msg = inputs["test_sequence"].next()
        return msg
    ```
    """

    def _pre_loop_hook(self, params: Optional[dict] = None) -> None:
        """Initialize node state. Set env variables for Fast API app."""
        for key, value in self.inputs.items():
            inputs[key] = value
        for key, value in self.outputs.items():
            outputs[key] = value

    def _execute(self, params: dict) -> None:
        """Start the API server."""
        config = uvicorn.Config(
            app=params.get("app"),  # type: ignore
            port=params.get("port", 8000),
            log_level=params.get("log_level", "info"),
            host="0.0.0.0",
        )
        server = uvicorn.Server(config)
        server.run()
