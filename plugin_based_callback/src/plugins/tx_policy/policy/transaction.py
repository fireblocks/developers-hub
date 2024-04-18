import time
from enum import Enum
from decimal import Decimal

from fireblocks_sdk import PolicyTransactionType

class TransactionSource(Enum):
    DATABASE = 'DATABASE'
    CALLBACK_HANDLER = 'CALLBACK_HANDLER'
    FIREBLOCKS_API = 'FIREBLOCKS_API'
    DICT = 'DICT'


class Transaction:
    def __init__(self, tx, tx_source: TransactionSource):
        self.id = None
        self.initiator = None
        self.approvers = []
        self.src_type = None
        self.src_id = None
        self.src_subtype = None
        self.src_address = None
        self.dst_type = None
        self.dst_id = None
        self.dst_subtype = None
        self.dst_address = None
        self.asset = None
        self.amount = None
        self.volume = None
        self.operation = None

        self.timestamp = int(time.time())

        if tx_source == TransactionSource.CALLBACK_HANDLER:
            self.from_callback_handler(tx)

    def from_callback_handler(self, tx):
        operation_str = tx['operation']
        if hasattr(PolicyTransactionType, operation_str):
            self.operation = getattr(PolicyTransactionType, operation_str)
        else:
            raise NotImplementedError("Operation", operation_str)

        self.asset = tx['asset']
        self.amount = Decimal(tx['amountStr'])

        self.src_id = tx['sourceId']
        self.src_type = tx['sourceType']

        self.dst_id = tx['destId']
        self.dst_type = tx['destType']
        self.dst_address = tx['destAddress']

        self.volume = 0

        for destination in tx['destinations']:
            self.volume += float(destination['amountUSD'])
            if destination['displayDstAddress'] == self.dst_address:
                self.dst_subtype = destination['dstSubType']

    def __str__(self):
        attributes = ", ".join([f"{attr}={getattr(self, attr)}" for attr in dir(self) if
                                not callable(getattr(self, attr)) and not attr.startswith("__")])
        return f"{self.__class__.__name__}({attributes})"
