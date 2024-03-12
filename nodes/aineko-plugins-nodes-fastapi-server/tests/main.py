# Copyright 2023 Aineko Authors
# SPDX-License-Identifier: Apache-2.0
from aineko_plugins.nodes.fastapi_server import health_router, inputs, outputs
from fastapi import FastAPI

app = FastAPI()

app.include_router(health_router)


@app.get("/next", status_code=200)
async def query():
    msg = inputs["messages"].next()
    return msg


@app.get("/last", status_code=200)
async def assignment():
    msg = inputs["messages"].read(how="last", timeout=1)
    return msg


@app.get("/write", status_code=200)
async def write():
    outputs["messages"].write(1)
    outputs["messages"].write(2)
    outputs["messages"].write(3)
    return
