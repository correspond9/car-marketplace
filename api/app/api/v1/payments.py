from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.application.razorpay_service import PaymentError, RazorpayService, new_receipt
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/payments/razorpay", tags=["payments"])


class RazorpayConfigOut(BaseModel):
    configured: bool
    key_id: str | None = None
    mode: str


class RazorpayOrderCreate(BaseModel):
    amount_inr: float = Field(default=1.0, ge=1, le=5000, description="Amount in rupees for test checkout")


class RazorpayOrderOut(BaseModel):
    order_id: str
    amount: int
    currency: str
    receipt: str | None = None
    key_id: str


class RazorpayVerifyIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class RazorpayVerifyOut(BaseModel):
    verified: bool
    order_id: str
    payment_id: str


def _payment_http_error(exc: PaymentError) -> HTTPException:
    status_code = (
        status.HTTP_503_SERVICE_UNAVAILABLE
        if exc.code == "NOT_CONFIGURED"
        else status.HTTP_422_UNPROCESSABLE_ENTITY
        if exc.code == "INVALID_AMOUNT"
        else status.HTTP_502_BAD_GATEWAY
    )
    return HTTPException(
        status_code=status_code,
        detail={"error": {"code": exc.code, "message": exc.message}},
    )


@router.get("/config", response_model=RazorpayConfigOut)
async def razorpay_config(
    user: Annotated[UserModel, Depends(get_current_user)],
) -> RazorpayConfigOut:
    service = RazorpayService()
    key_id = service.public_key_id or None
    mode = "test" if key_id and key_id.startswith("rzp_test_") else "live" if key_id else "unconfigured"
    return RazorpayConfigOut(configured=service.configured, key_id=key_id, mode=mode)


@router.post("/orders", response_model=RazorpayOrderOut)
async def create_razorpay_order(
    body: RazorpayOrderCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
) -> RazorpayOrderOut:
    service = RazorpayService()
    amount_paise = int(round(body.amount_inr * 100))
    try:
        order = await service.create_order(
            amount_paise=amount_paise,
            receipt=new_receipt(),
            notes={"user_id": str(user.id), "purpose": "production_test"},
        )
    except PaymentError as exc:
        raise _payment_http_error(exc) from exc
    return RazorpayOrderOut.model_validate(order)


@router.post("/verify", response_model=RazorpayVerifyOut)
async def verify_razorpay_payment(
    body: RazorpayVerifyIn,
    user: Annotated[UserModel, Depends(get_current_user)],
) -> RazorpayVerifyOut:
    service = RazorpayService()
    try:
        verified = service.verify_signature(
            order_id=body.razorpay_order_id,
            payment_id=body.razorpay_payment_id,
            signature=body.razorpay_signature,
        )
    except PaymentError as exc:
        raise _payment_http_error(exc) from exc

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_SIGNATURE", "message": "Payment verification failed"}},
        )

    return RazorpayVerifyOut(
        verified=True,
        order_id=body.razorpay_order_id,
        payment_id=body.razorpay_payment_id,
    )
