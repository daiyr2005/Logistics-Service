from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mysite.clients.auth_service import verify_user

router = APIRouter()
security = HTTPBearer()


@router.get("/profile")
async def profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    user = await verify_user(credentials.credentials)
    return user