"""Translate domain and application errors into HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from order_service.application.exceptions import UserServiceUnavailableError
from order_service.domain import exceptions as domain

_STATUS_BY_EXCEPTION: dict[type[domain.DomainError], int] = {
    domain.OrderNotFoundError: status.HTTP_404_NOT_FOUND,
    domain.UserNotFoundError: status.HTTP_404_NOT_FOUND,
    domain.EmptyOrderError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    domain.InvalidQuantityError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    domain.InvalidAmountError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    domain.CurrencyMismatchError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers for the domain hierarchy and application failures."""

    async def handle_domain_error(request: Request, exc: domain.DomainError) -> JSONResponse:
        status_code = _STATUS_BY_EXCEPTION.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    async def handle_dependency_down(
        request: Request, exc: UserServiceUnavailableError
    ) -> JSONResponse:
        # A downstream outage is not the client's fault: 503 + retry hint.
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
            headers={"Retry-After": "5"},
        )

    app.add_exception_handler(domain.DomainError, handle_domain_error)  # type: ignore[arg-type]
    app.add_exception_handler(UserServiceUnavailableError, handle_dependency_down)  # type: ignore[arg-type]
