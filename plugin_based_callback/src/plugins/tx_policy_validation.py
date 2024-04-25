import logging
from typing import Dict, Any
from src.plugins.interface import PluginInterface
from src.exceptions import PluginError

from src.plugins.tx_policy.policy.engine import PolicyEngine
from src.plugins.tx_policy.policy.transaction import Transaction, TransactionSource
from src.plugins.tx_policy.api import get_groups_to_users_mapping, get_active_policy

logger = logging.getLogger(__name__)


class TxPolicyValidation(PluginInterface):
    def __init__(self):
        super().__init__()
        self._groups_to_users_mapping = None
        self._policy_dict = None
        self._policy_engine = None

    async def init(self, *args, **kwargs):
        self._groups_to_users_mapping = get_groups_to_users_mapping()
        self._policy_dict = get_active_policy()
        self._policy_engine = PolicyEngine.from_policy_dict(self._policy_dict, self._groups_to_users_mapping)

    async def process_request(self, data: Dict[str, Any]) -> bool:
        """Entry point - Validates the transaction against the policy"""
        tx = Transaction(data, TransactionSource.CALLBACK_HANDLER)

        try:
            result = self._policy_engine.check_tx(tx)
            logger.info(f"Approval result from TX Policy Validation Plugin is: {result}")
            return result.allow
        except Exception as e:
            raise PluginError(f"Unexpected error in TX Policy Validation plugin: {e}")

    def _create_db_instance(self):
        """No DB Access required"""
        pass

    def __repr__(self) -> str:
        return "<Transaction Policy Validation Plugin>"
