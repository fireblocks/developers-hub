import time

from src.plugins.tx_policy.policy.engine import PolicyEngine
from src.plugins.tx_policy.policy.transaction import Transaction, TransactionSource
from src.plugins.tx_policy.api import get_groups_to_users_mapping, get_active_policy

tx_dict = {
    "txId": "9c794cee-7e27-46c9-9e9a-ed68295ff06b",
    "operation": "TRANSFER",
    "sourceType": "VAULT",
    "sourceId": "0",
    "destType": "VAULT",
    "destId": "1",
    "asset": "ETH",
    "amount": 0.01,
    "amountStr": "0.010000000000000000",
    "requestedAmount": 0.01,
    "requestedAmountStr": "0.01",
    "fee": "0.000597803762241000",
    "destAddressType": "WHITELISTED",
    "destAddress": "0x5dC69B1Fbb13Bafd09af88a782F0F285772Ad5f8",
    "destinations": [
        {
            "amountNative": 0.01,
            "amountNativeStr": "0.01",
            "amountUSD": 18.74292937,
            "dstAddressType": "WHITELISTED",
            "dstId": "1",
            "dstWalletId": "",
            "dstName": "Network Deposits",
            "dstSubType": "",
            "dstType": "VAULT",
            "displayDstAddress": "0x5dC69B1Fbb13Bafd09af88a782F0F285772Ad5f8",
            "action": "ALLOW",
            "actionInfo": {
                "capturedRuleNum": 5,
                "rulesSnapshotId": 8164,
                "byGlobalPolicy": False,
                "byRule": True,
                "capturedRule": "{\"type\":\"TRANSFER\",\"transactionType\":\"TRANSFER\",\"asset\":\"*\",\"amount\":0,\"operators\":{\"wildcard\":\"*\"},\"applyForApprove\":true,\"action\":\"ALLOW\",\"src\":{\"ids\":[[\"*\"]]},\"dst\":{\"ids\":[[\"*\"]]},\"dstAddressType\":\"*\",\"amountCurrency\":\"USD\",\"amountScope\":\"SINGLE_TX\",\"periodSec\":0}"
            }
        }
    ],
    "rawTx": [
        {
            "keyDerivationPath": "[ 44, 60, 0, 0, 0 ]",
            "rawTx": "02ef0104843b9aca008506a0c1987d825208945dc69b1fbb13bafd09af88a782f0f285772ad5f8872386f26fc1000080c0",
            "payload": "77b4e74099ce90c08503c0e0bb6e672dbe1c5e3e127ce333bf22eb581cd3f6ce"
        }
    ],
    "players": [
        "21926ecc-4a8a-4614-bbac-7c591aa7efdd",
        "27900737-46f6-4097-a169-d0ff45649ed5",
        "f89cac50-c656-4e74-879f-041aff8d01b5"
    ],
    "requestId": "9c794cee-7e27-46c9-9e9a-ed68295ff06b"
}


def test_no_rules():
    groups_to_users_mapping = {}
    policy_dict = {
        "policy": {
            "rules": []
        }
    }

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert not result.allow


def test_simple_allow_rule():
    groups_to_users_mapping = {}
    policy_dict = {
        "policy": {
            "rules": [
                {
                    "type": "TRANSFER",
                    "transactionType": "TRANSFER",
                    "asset": "*",
                    "amount": 0,
                    "operators": {
                        "wildcard": "*"
                    },
                    "applyForApprove": True,
                    "action": "ALLOW",
                    "src": {
                        "ids": [
                            ["*"]
                        ]
                    },
                    "dst": {
                        "ids": [
                            ["*"]
                        ]
                    },
                    "dstAddressType": "*",
                    "amountCurrency": "USD",
                    "amountScope": "SINGLE_TX",
                    "periodSec": 0
                }

            ]
        }
    }

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert result.allow


def test_block_rule():
    groups_to_users_mapping = {}
    policy_dict = {
        "policy":
            {
                "rules": [
                    {
                        "type": "TRANSFER",
                        "transactionType": "TRANSFER",
                        "asset": "*",
                        "amount": 5,
                        "operators": {
                            "wildcard": "*"
                        },
                        "applyForApprove": True,
                        "action": "BLOCK",
                        "src": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dst": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dstAddressType": "*",
                        "amountCurrency": "USD",
                        "amountScope": "SINGLE_TX",
                        "periodSec": 0
                    },
                    {
                        "type": "TRANSFER",
                        "transactionType": "TRANSFER",
                        "asset": "*",
                        "amount": 0,
                        "operators": {
                            "wildcard": "*"
                        },
                        "applyForApprove": True,
                        "action": "ALLOW",
                        "src": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dst": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dstAddressType": "*",
                        "amountCurrency": "USD",
                        "amountScope": "SINGLE_TX",
                        "periodSec": 0
                    }

                ]}
    }

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert not result.allow


def test_timerange_rule():
    groups_to_users_mapping = {}
    period = 1  # sec
    policy_dict = {
        "policy":
            {
                "rules": [
                    {
                        "type": "TRANSFER",
                        "transactionType": "TRANSFER",
                        "asset": "*",
                        "amount": 20,
                        "operators": {
                            "wildcard": "*"
                        },
                        "applyForApprove": True,
                        "action": "BLOCK",
                        "src": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dst": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dstAddressType": "*",
                        "amountCurrency": "USD",
                        "amountScope": "TIMEFRAME",
                        "periodSec": period,
                        "amountAggregation": {
                            "operators": "ACROSS_ALL_MATCHES",
                            "dstTransferPeers": "PER_SINGLE_MATCH",
                            "srcTransferPeers": "ACROSS_ALL_MATCHES"
                        }
                    },
                    {
                        "type": "TRANSFER",
                        "transactionType": "TRANSFER",
                        "asset": "*",
                        "amount": 0,
                        "operators": {
                            "wildcard": "*"
                        },
                        "applyForApprove": True,
                        "action": "ALLOW",
                        "src": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dst": {
                            "ids": [
                                ["*"]
                            ]
                        },
                        "dstAddressType": "*",
                        "amountCurrency": "USD",
                        "amountScope": "SINGLE_TX",
                        "periodSec": 0
                    }

                ]
            }

    }

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert result.allow

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    result = policy_engine.check_tx(tx)
    assert not result.allow

    time.sleep(period + 1)

    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    result = policy_engine.check_tx(tx)
    assert result.allow

def test_active_policy():
    groups_to_users_mapping = get_groups_to_users_mapping()
    policy_dict = get_active_policy()
    tx_dict = {
    "operation": "TRANSFER",
    "sourceType": "VAULT",
    "sourceId": "0",
    "destType": "VAULT",
    "destId": "0",
    "asset": "ETH",
    "amount": 0,
    "amountStr": "0",
    "destAddressType": "WHITELISTED",
    "destAddress": "0x5dC69B1Fbb13Bafd09af88a782F0F285772Ad5f8",
    "destinations": [
        {
            "amountNative": 0,
            "amountNativeStr": "0",
            "amountUSD": 0,
            "dstAddressType": "WHITELISTED",
            "dstId": "0",
            "dstWalletId": "",
            "dstSubType": "",
            "dstType": "VAULT",
            "displayDstAddress": "0x5dC69B1Fbb13Bafd09af88a782F0F285772Ad5f8",
            "action": "ALLOW",
        }
    ]
    }
    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert result.allow

def test_rule_with_groups():
    groups_to_users_mapping = {}
    policy_dict = {
        "policy": {
            "rules": [
                {
                    "type": "TRANSFER",
                    "transactionType": "TRANSFER",
                    "asset": "*",
                    "amount": 0,
                    "operators": {
                        "wildcard": "*"
                    },
                    "applyForApprove": True,
                    "action": "ALLOW",
                    "src": {
                        "ids": [
                            ["*"]
                        ]
                    },
                    "dst": {
                        "ids": [
                            ["*"]
                        ]
                    },
                    "dstAddressType": "*",
                    "amountCurrency": "USD",
                    "amountScope": "SINGLE_TX",
                    "periodSec": 0,
                    "authorizationGroups": {
                        "logic": "AND",
                        "groups": [
                            {
                                "th": 2,
                                "users": [
                                    "ffc54b8c-46f6-591f-b4ab-63a5c785fad1"
                                ],
                                "usersGroups": [
                                    "2c9baefd-0d0b-4570-83ed-ee62c2735b4c"
                                ]
                            },
                            {
                                "th": 1,
                                "users": [
                                    "54da9b5d-ece7-531b-a1a5-8a34234ea6c6"
                                ]
                            }
                        ],
                        "allowOperatorAsAuthorizer": False
                    }
                }

            ]
        }
    }
    tx = Transaction(tx_dict, TransactionSource.CALLBACK_HANDLER)
    policy_engine = PolicyEngine.from_policy_dict(policy_dict, groups_to_users_mapping)
    result = policy_engine.check_tx(tx)
    assert result.allow

test_simple_allow_rule()