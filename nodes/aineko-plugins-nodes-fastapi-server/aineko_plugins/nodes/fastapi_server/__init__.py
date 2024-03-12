# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Aineko Plugin for running a FastAPI server."""
from .health import health_router
from .main import FastAPI, inputs, outputs

__all__ = ["health_router", "FastAPI", "inputs", "outputs"]
