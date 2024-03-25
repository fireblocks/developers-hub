from typing import Optional
from dataclasses import dataclass
from src.authenticate import JWTAuthenticator


@dataclass
class CallbackResponse:
    """Data class for callback response structure"""

    authenticator: JWTAuthenticator
    action: str
    requestId: str
    rejectionReason: Optional[str] = None

    def get_response(self):
        """Return a signed valid JWT response"""
        return self.authenticator.sign_response(
            {
                "action": self.action,
                "requestId": self.requestId,
                "rejectionReason": self.rejectionReason,
            }
        )
