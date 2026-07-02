from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    dealer_stores,
    dev_seed,
    favorites,
    health,
    inquiries,
    listings,
    moderation,
    notifications,
    payments,
    platform,
    reports,
    reviews,
    saved_searches,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(dealer_stores.router)
api_router.include_router(listings.router)
api_router.include_router(inquiries.router)
api_router.include_router(reviews.router)
api_router.include_router(favorites.router)
api_router.include_router(reports.router)
api_router.include_router(saved_searches.router)
api_router.include_router(moderation.router)
api_router.include_router(admin.router)
api_router.include_router(platform.router)
api_router.include_router(notifications.router)
api_router.include_router(payments.router)
api_router.include_router(health.router)
api_router.include_router(dev_seed.router)
