from pathlib import Path
import logging
from src.config.settings import settings
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.exception_handlers import (
    global_exception_handler,
)
from src.api.routes.chat import router as chat_router
from src.api.routes.health import router as health_router
from src.api.routes.observability import (
    router as observability_router,
)
from src.utils.logging_config import configure_logging


# =========================================================
# PATH CONFIGURATION
# =========================================================

# main.py
#   src/
#       api/
#           main.py
#
# Project root = main.py -> api -> src -> project root

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent.parent.parent
)

UI_DIRECTORY = (
    PROJECT_ROOT
    / "src"
    / "ui"
)

UI_INDEX_FILE = (
    UI_DIRECTORY
    / "index.html"
)


# =========================================================
# LOGGING
# =========================================================

configure_logging()

logger = logging.getLogger(__name__)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Production Support Platform",
    version=settings.app_version,
)


# =========================================================
# EXCEPTION HANDLING
# =========================================================

app.add_exception_handler(
    Exception,
    global_exception_handler,
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    chat_router,
    prefix="/api/v1",
)

app.include_router(
    observability_router,
    prefix="/api/v1",
)


# =========================================================
# CHAT UI
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(UI_DIRECTORY)
    ),
    name="static",
)


@app.get(
    "/",
    include_in_schema=False,
)
def chat_ui():
    return FileResponse(
        str(UI_INDEX_FILE)
    )


# =========================================================
# STARTUP
# =========================================================

logger.info(
    "AI Production Support Platform started"
)