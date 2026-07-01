from fastapi import APIRouter

from app.api.v1 import auth, health, listings, moderation, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(listings.router)
api_router.include_router(moderation.router)
api_router.include_router(health.router)
