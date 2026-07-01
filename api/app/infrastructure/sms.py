from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SMSService:
    async def send_otp(self, phone: str, otp: str) -> None:
        if settings.sms_provider == "mock":
            logger.info("mock_sms_sent", phone=phone[-4:], provider="mock")
            return
        if settings.sms_provider == "msg91":
            await self._send_msg91(phone, otp)
            return
        raise RuntimeError(f"Unsupported SMS provider: {settings.sms_provider}")

    async def _send_msg91(self, phone: str, otp: str) -> None:
        import httpx

        if not settings.msg91_auth_key:
            raise RuntimeError("MSG91_AUTH_KEY not configured")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://control.msg91.com/api/v5/flow/",
                headers={"authkey": settings.msg91_auth_key},
                json={
                    "template_id": "otp_template",
                    "recipients": [{"mobiles": phone.replace("+", ""), "otp": otp}],
                },
                timeout=10.0,
            )
            response.raise_for_status()
        logger.info("sms_sent", phone=phone[-4:], provider="msg91")
