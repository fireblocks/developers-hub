import base64
import logging
import aiofiles
from pathlib import Path
from src import settings
from src.exceptions import PluginError
from src.plugins.interface import PluginInterface
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import load_pem_public_key


logger = logging.getLogger(__name__)


class ExtraSignature(PluginInterface):
    def __init__(self):
        super().__init__()
        self._public_key = None

    async def init(self, *args, **kwargs):
        self._public_key = await self._read_public_key()

    async def process_request(self, data: dict) -> bool:
        """Process the request by verifying the extra signature."""
        try:
            message = data.get("extraParameters", {}).get("message")
            signature = data.get("extraParameters", {}).get("extraSignature")
            if not signature or not message:
                raise PluginError("Missing extra signature/message")
            return await self._verify_signature(message, signature)
        except PluginError as e:
            logger.error(f"Failed to validate signature: {e}")
            raise

    @staticmethod
    async def _read_public_key() -> RSAPublicKey:
        """Reads the public key from file."""
        try:
            async with aiofiles.open(Path(settings.EXTRA_SIGNATURE_PUBLIC_KEY_PATH), "rb") as f:
                public_key_bytes = await f.read()
                return load_pem_public_key(public_key_bytes)
        except FileNotFoundError as e:
            logger.error(f"Error reading public key file: {e}")
            raise PluginError(f"Error reading public key file: {e}")

    async def _verify_signature(self, string_to_sign: str, signature: str) -> bool:
        """Verifies the signature of the provided string.
        Using RSA-SHA256"""
        try:
            signature_bytes = base64.b64decode(signature)
            self._public_key.verify(
                signature_bytes,
                string_to_sign.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            logger.info("Signature verified successfully.")
            return True
        except Exception as e:
            raise PluginError(f"Could not verify the extra signature: {e}")

    def _create_db_instance(self):
        """No DB Access required"""
        pass

    def __repr__(self) -> str:
        return "<Extra Signature Validation Plugin>"
