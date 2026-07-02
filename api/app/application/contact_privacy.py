from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ListingStatus, UserRole
from app.infrastructure.database import DealerStoreModel, ListingModel, UserModel


def default_show_contact_for_role(role: UserRole) -> bool:
    return role == UserRole.DEALER


async def resolve_public_seller_contact(
    db: AsyncSession, listing: ListingModel
) -> str | None:
    if listing.status != ListingStatus.LIVE or not listing.show_contact_publicly:
        return None

    if listing.dealer_store_id:
        store = listing.dealer_store
        if store is None:
            store = await db.get(DealerStoreModel, listing.dealer_store_id)
        if store and store.phone:
            return store.phone

    seller = listing.seller
    if seller is None:
        seller = await db.get(UserModel, listing.seller_id)
    return seller.phone if seller else None
