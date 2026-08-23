"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api import auth, ping

app = FastAPI(title="Nuevo Hive API")
app.include_router(ping.router)
app.include_router(auth.router)
