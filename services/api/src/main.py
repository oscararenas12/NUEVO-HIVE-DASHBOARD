"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api import auth, ping
from src.api.users import views as users_views

app = FastAPI(title="Nuevo Hive API")
app.include_router(ping.router)
app.include_router(auth.router)
app.include_router(users_views.router)
