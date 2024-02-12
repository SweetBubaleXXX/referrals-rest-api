from fastapi import APIRouter

from .endpoints import auth, referrals, users

v1_router = APIRouter()

v1_router.include_router(auth.router, prefix="/auth")
v1_router.include_router(referrals.router, prefix="/referrals")
v1_router.include_router(users.router, prefix="/users")
