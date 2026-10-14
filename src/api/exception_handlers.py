import logging

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected application exceptions.

    Full exception details are logged internally.
    A safe generic response is returned to the API client.
    """

    logger.exception(
        "Unhandled application exception | method=%s | path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": (
                "An internal error occurred while "
                "processing the request."
            ),
        },
    )