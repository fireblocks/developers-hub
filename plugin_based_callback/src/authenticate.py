import aiofiles
import jwt
import logging
from src import helpers
from src import settings
from pathlib import Path
from functools import wraps
from typing import Callable
from fastapi import HTTPException, Request
from jwt import (
    InvalidTokenError,
    ExpiredSignatureError,
    InvalidSignatureError,
    DecodeError,
)

logger = logging.getLogger(__name__)


class JWTAuthenticator:
    def __init__(self):
        self._cosigner_public_key = None
        self._callback_private_key = None

    async def load_keys(self) -> None:
        """Load the callback private key and cosigner public key."""
        try:
            async with aiofiles.open(Path(settings.CALLBACK_PRIVATE_KEY_PATH), "r") as f1, \
                    aiofiles.open(Path(settings.COSIGNER_PUBLIC_KEY_PATH), "r") as f2:
                self._callback_private_key = await f1.read()
                self._cosigner_public_key = await f2.read()
        except FileNotFoundError as e:
            logger.error(f"Could not load keys: {e}")
            raise

    async def authenticate(self, request: Request) -> dict:
        """Validate JWT sent by the Co-Signer w/ cosigner public key"""
        try:
            # Use parse raw body helper method
            body = await helpers.parse_body(request)
            return jwt.decode(body, self._cosigner_public_key, algorithms=["RS256"])

        except ExpiredSignatureError:
            logger.error("Token has expired.")
            raise HTTPException(status_code=401, detail="Token has expired.")
        except InvalidSignatureError:
            logger.error("Token signature is invalid.")
            raise HTTPException(status_code=403, detail="Token signature is invalid.")
        except DecodeError:
            logger.error("Token could not be decoded.")
            raise HTTPException(status_code=403, detail="Token could not be decoded.")
        except InvalidTokenError:
            logger.error("Invalid token.")
            raise HTTPException(status_code=403, detail="Invalid token.")
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            raise HTTPException(status_code=403, detail="Failed to authenticate.")

    def sign_response(self, response: dict) -> str:
        """Sign Callback Response w/ callback private key"""
        return jwt.encode(
            payload=response, key=self._callback_private_key, algorithm="RS256"
        )


def authenticate_jwt(func: Callable) -> Callable:
    """Authenticate decorator"""

    @wraps(func)
    async def wrapper(request: Request, decoded_payload, authenticator):
        authenticator = JWTAuthenticator()
        await authenticator.load_keys()
        payload = await authenticator.authenticate(request)
        return await func(request, payload, authenticator)

    return wrapper
