# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
"""Objects from extra FastAPI submodule."""
from .health import health_router
from .main import FastAPI, consumers, producers

__all__ = ["consumers", "health_router", "producers", "FastAPI"]
