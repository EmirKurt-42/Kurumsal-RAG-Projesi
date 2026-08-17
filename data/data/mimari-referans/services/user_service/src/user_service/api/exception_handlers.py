"""Translate domain errors into HTTP responses.

Routes stay free of try/except blocks: any domain exception raised deep in
the application bubbles up here and is mapped to a status code. The domain
says "this e-mail is already registered"; deciding that this means *409*
is strictly an HTTP concern and therefore lives in the api layer.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from user_service.domain import exceptions as domain

_STATUS_BY_EXCEPTION: dict[type[domain.DomainError], int] = {
    domain.UserNotFoundError: status.HTTP_404_NOT_FOUND,
    domain.EmailAlreadyRegisteredError: status.HTTP_409_CONFLICT,
    domain.InvalidEmailError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    domain.InvalidFullNameError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach a single handler covering the whole domain error hierarchy."""

    async def handle_domain_error(request: Request, exc: domain.DomainError) -> JSONResponse:
        status_code = _STATUS_BY_EXCEPTION.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    # Starlette walks the exception's MRO, so registering the base class
    # routes every DomainError subclass through this handler.
    app.add_exception_handler(domain.DomainError, handle_domain_error)  # type: ignore[arg-type]
