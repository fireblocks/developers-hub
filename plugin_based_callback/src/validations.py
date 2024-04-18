import aiofiles
import logging
from src.exceptions import DatabaseUnsupportedError, ValidationError
from src.settings import DB_TYPE, DB_CLASS_MAP, PLUGINS, EXTRA_SIGNATURE_PUBLIC_KEY_PATH, SERVER_PORT, FIREBLOCKS_API_KEY, FIREBLOCKS_API_SECRET

logger = logging.getLogger(__name__)


async def validate_db_config() -> None:
    """Check if DB type is valid or empty. If empty and TxidValidation plugin is set -> fail validation"""
    if DB_TYPE not in DB_CLASS_MAP:
        if not (DB_TYPE is None or DB_TYPE == ""):
            raise DatabaseUnsupportedError(f"Unsupported DB type: {DB_TYPE}")
        else:
            if "txid_validation" in PLUGINS:
                raise ValueError(f"txid_validation plugin requires a valid DB setup")


async def validate_extra_sig_key() -> None:
    if "extra_signature" not in PLUGINS:
        return
    try:
        async with aiofiles.open(EXTRA_SIGNATURE_PUBLIC_KEY_PATH, "r"):
            return
    except FileNotFoundError:
        raise ValidationError(
            "Extra Signature plugin is configured but no validation key was found"
        )

async def validate_tx_policy() -> None:
    if "tx_policy_validation" not in PLUGINS:
        return
    if (not FIREBLOCKS_API_KEY) or not (FIREBLOCKS_API_SECRET):
        raise ValidationError(
            "Transaction Policy plugin is configured but no fireblocks api key or secret was found"
        )

async def run_validations() -> None:
    """Run all validations"""
    try:
        await validate_db_config()
        await validate_extra_sig_key()
        await validate_tx_policy()
        logger.info("Completed all validations")
    except Exception as e:
        raise
