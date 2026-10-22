
import os
import httpx
from fastapi import HTTPException, status

AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://127.0.0.1:8005"
)


async def verify_user(token: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/verify/",
            headers={"Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return response.json()


