import uvicorn
import logging.config
from src import validations
from contextlib import asynccontextmanager
from src.authenticate import authenticate_jwt
from src.logs.log_config import logging_config
from fastapi.responses import PlainTextResponse
from src.callback_response import CallbackResponse
from fastapi import FastAPI, Request, HTTPException
from src.plugins.plugin_manager import PluginManager
from src.exceptions import ValidationError, DatabaseUnsupportedError, PluginLoadError

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

plugin_manager = PluginManager()


@asynccontextmanager
async def on_startup(app: FastAPI):
    """Life span generator - execute validations and load plugins on `startup` event.
    Nothing to execute on `shutdown` event"""
    try:

        await validations.run_validations()
        plugin_specs = validations.PLUGINS
        await plugin_manager.load_plugins(plugin_specs)
        logger.info(
            f"Callback handler is running with the following plugins: {plugin_manager.get_plugins()}"
        )
        yield
    except ValidationError as e:
        logger.exception(f"Validation Error: {e}")
    except (DatabaseUnsupportedError, ValueError, PluginLoadError) as e:
        logger.exception(f"{e}")
    finally:
        exit(1)

app = FastAPI(lifespan=on_startup)


@app.post("/v2/tx_sign_request")
@authenticate_jwt
async def tx_approval(request: Request, decoded_payload=None, authenticator=None):
    """Transaction Approval endpoint:
    https://developers.fireblocks.com/reference/transaction-signing-request-approval"""
    try:
        approval_result = await plugin_manager.process_request(decoded_payload)
        if approval_result is None:
            response_action = "IGNORE"
        elif approval_result is False:
            response_action = "REJECT"
        else:
            response_action = 'APPROVE'

        reason = (
            None
            if approval_result
            else "Callback Handler Logic denied the transaction approval"
        )

        response = CallbackResponse(
            authenticator,
            response_action,
            decoded_payload["requestId"],
            reason
        ).get_response()

        return PlainTextResponse(response)
    except Exception as e:
        logger.exception(
            f"Transaction Approval process failed with the following error: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v2/config_change_sign_request")
@authenticate_jwt
async def change_approval(request: Request):
    """Configuration Change Approval - #TODO"""
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=validations.SERVER_PORT)
