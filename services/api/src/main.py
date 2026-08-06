"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api import ping

app = FastAPI(title="Nuevo Hive API")
app.include_router(ping.router)
