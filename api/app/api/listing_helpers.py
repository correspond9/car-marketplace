from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ListingOut
from app.application.contact_privacy import resolve_public_seller_contact
from app.infrastructure.database import ListingModel


async def listing_to_out(db: AsyncSession, listing: ListingModel) -> ListingOut:
    out = ListingOut.model_validate(listing)
    out.seller_contact_phone = await resolve_public_seller_contact(db, listing)
    return out
