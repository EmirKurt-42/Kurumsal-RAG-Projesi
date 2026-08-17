"""HTTP endpoints for order management. Thin by design."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from order_service.api.dependencies import (
    get_create_order,
    get_get_order,
    get_list_user_orders,
)
from order_service.api.v1.schemas.order import CreateOrderRequest, OrderResponse
from order_service.application.dto import CreateOrderInput, OrderItemInput
from order_service.application.use_cases.create_order import CreateOrder
from order_service.application.use_cases.get_order import GetOrder
from order_service.application.use_cases.list_user_orders import ListUserOrders

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CreateOrderRequest,
    use_case: Annotated[CreateOrder, Depends(get_create_order)],
) -> OrderResponse:
    """Place a new order for an existing user."""
    output = await use_case.execute(
        CreateOrderInput(
            user_id=payload.user_id,
            currency=payload.currency,
            items=tuple(
                OrderItemInput(
                    product_name=item.product_name,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                )
                for item in payload.items
            ),
        )
    )
    return OrderResponse.model_validate(output)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    use_case: Annotated[GetOrder, Depends(get_get_order)],
) -> OrderResponse:
    """Fetch a single order by id."""
    return OrderResponse.model_validate(await use_case.execute(order_id))


@router.get("", response_model=list[OrderResponse])
async def list_user_orders(
    user_id: Annotated[UUID, Query(description="Owner of the orders to list.")],
    use_case: Annotated[ListUserOrders, Depends(get_list_user_orders)],
) -> list[OrderResponse]:
    """List one user's orders, newest first."""
    return [OrderResponse.model_validate(order) for order in await use_case.execute(user_id)]
