from __future__ import annotations

import hashlib
import hmac
import uuid
from typing import Any

import httpx

from app.core.config import settings


class PaymentError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class RazorpayService:
    BASE_URL = "https://api.razorpay.com/v1"

    @property
    def configured(self) -> bool:
        return bool(settings.razorpay_key_id and settings.razorpay_key_secret)

    @property
    def public_key_id(self) -> str:
        return settings.razorpay_key_id

    def _auth(self) -> tuple[str, str]:
        if not self.configured:
            raise PaymentError("NOT_CONFIGURED", "Razorpay is not configured on the server")
        return settings.razorpay_key_id, settings.razorpay_key_secret

    async def create_order(self, *, amount_paise: int, receipt: str, notes: dict[str, str] | None = None) -> dict[str, Any]:
        if amount_paise < 100:
            raise PaymentError("INVALID_AMOUNT", "Minimum test amount is ₹1 (100 paise)")
        payload: dict[str, Any] = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
        }
        if notes:
            payload["notes"] = notes

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.BASE_URL}/orders",
                json=payload,
                auth=self._auth(),
            )

        if response.status_code >= 400:
            detail = response.text[:300]
            raise PaymentError("RAZORPAY_ERROR", f"Could not create Razorpay order ({response.status_code}): {detail}")

        data = response.json()
        return {
            "order_id": data["id"],
            "amount": data["amount"],
            "currency": data["currency"],
            "receipt": data.get("receipt"),
            "key_id": self.public_key_id,
        }

    def verify_signature(self, *, order_id: str, payment_id: str, signature: str) -> bool:
        if not self.configured:
            raise PaymentError("NOT_CONFIGURED", "Razorpay is not configured on the server")
        message = f"{order_id}|{payment_id}".encode()
        expected = hmac.new(
            settings.razorpay_key_secret.encode(),
            message,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


def new_receipt(prefix: str = "cm-test") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
