from itertools import combinations, chain, product
from decimal import getcontext
from dataclasses import dataclass

from src.plugins.tx_policy.external_data.pricing import get_usd_to_eur_rate

from src.plugins.tx_policy.policy.consts import ANY, AmountCurrency
from fireblocks_sdk import PolicyAction, PolicyAmountScope, PolicySrcOrDestType, PolicyTransactionType, \
    PolicyDestAddressType
from src.plugins.tx_policy.policy.transaction import Transaction
from src.plugins.tx_policy.policy.rule import FormattedPolicyRule, PolicyRule, convert_keys_to_snake_case

getcontext().prec = 30

@dataclass
class PolicyCheckResult:
    allow: bool
    matched_rule: FormattedPolicyRule


def get_aggregated_volume_and_amount_from_transaction_history(transaction_history: list[Transaction], initiator_agg,
                                                              src_agg_id,
                                                              dst_agg_id, asset_agg, transaction_types_agg,
                                                              tx_time_sec, interval_sec,
                                                              ):
    aggregated_value_usd = 0
    aggregated_amount = 0

    for historic_transaction in transaction_history:
        if initiator_agg is not None:
            if historic_transaction.initiator != initiator_agg:
                continue
        if asset_agg is not None:
            if historic_transaction.asset != asset_agg:
                continue
        if src_agg_id is not None:
            if historic_transaction.src_id != src_agg_id:
                continue
        if dst_agg_id is not None:
            if historic_transaction.dst_id != dst_agg_id:
                continue
        if historic_transaction.operation not in transaction_types_agg:
            continue
        try:
            if historic_transaction.timestamp < tx_time_sec - interval_sec or historic_transaction.timestamp > tx_time_sec:
                continue
        except AttributeError:
            print(historic_transaction)

        aggregated_amount += historic_transaction.amount
        aggregated_value_usd += historic_transaction.volume

    return aggregated_value_usd, aggregated_amount


class PolicyEngine:
    def __init__(self, rules, groups_to_users_mapping):
        self.rules = rules
        self.groups_to_users_mapping = groups_to_users_mapping
        self.transaction_history = []

    @staticmethod
    def from_policy_dict(policy_dict, groups_to_users_mapping):
        rules = policy_dict['policy']['rules']
        formatted_rules = []
        for rule in rules:
            snake_case = convert_keys_to_snake_case(rule)

            formatted_rules.append(FormattedPolicyRule(PolicyRule(**snake_case)))

        return PolicyEngine(formatted_rules, groups_to_users_mapping)

    def check_asset(self, tx, rule):
        return tx.asset == rule.asset or rule.asset == ANY

    def check_initiator(self, tx, rule):
        if rule.operators == ANY:
            return True

        if rule.operators['users'] is None:
            initiator_in_users_match = True
        else:
            initiator_in_users_match = tx.initiator in rule.operators['users']

        if rule.operators['users_groups'] is None:
            initiator_in_groups_match = True
        else:
            initiator_in_groups_match = False
            for group_id in rule.operators['users_groups']:
                group_users = self.groups_to_users_mapping[group_id]
                if tx.initiator in group_users:
                    initiator_in_groups_match = True
                    break

        return initiator_in_users_match and initiator_in_groups_match

    def check_value(self, tx, rule):
        if rule.amount_scope == PolicyAmountScope.SINGLE_TX:
            return tx.volume >= rule.amount

        elif rule.amount_scope == PolicyAmountScope.TIMEFRAME:
            initiator_agg = None if rule.amount_aggregation['operators'] == 'ACROSS_ALL_MATCHES' else tx.initiator
            src_agg_id = None if rule.amount_aggregation[
                                     'srcTransferPeers'] == 'ACROSS_ALL_MATCHES' else tx.src_id
            dst_agg_id = None if rule.amount_aggregation[
                                     'dstTransferPeers'] == 'ACROSS_ALL_MATCHES' else tx.dst_id
            asset_agg = None if rule.asset == ANY else rule.asset
            transaction_types_agg = [rule.transaction_type]

            if rule.transaction_type == PolicyTransactionType.CONTRACT_CALL:
                if rule.applyForApprove:
                    transaction_types_agg.append(PolicyTransactionType.APPROVE)
                if rule.applyForTypedMessage:
                    transaction_types_agg.append(PolicyTransactionType.TYPED_MESSAGE)

            aggregated_volume_usd, aggregated_amount = get_aggregated_volume_and_amount_from_transaction_history(
                transaction_history=self.transaction_history, initiator_agg=initiator_agg, src_agg_id=src_agg_id,
                dst_agg_id=dst_agg_id, interval_sec=rule.period_sec,
                tx_time_sec=tx.timestamp, asset_agg=asset_agg, transaction_types_agg=transaction_types_agg)

            aggregated_amount += tx.amount
            aggregated_volume_usd += tx.volume

            if rule.amount_currency == AmountCurrency.USD:
                return aggregated_volume_usd >= rule.amount
            elif rule.amount_currency == AmountCurrency.EUR:
                return aggregated_volume_usd * get_usd_to_eur_rate() >= rule.amount
            elif rule.amount_currency == AmountCurrency.NATIVE:
                return aggregated_amount >= rule.amount
            else:
                raise ValueError("amount_currency", rule.amount_currency)

        else:
            raise ValueError("amount_scope", rule.amount_scope)

    def check_source(self, tx, rule):
        return rule.src == ANY or any([self._check_src_object(tx, src_object) for src_object in rule.src])

    def _check_src_object(self, tx, src_object):
        id_match = src_object.id is None or src_object.id == ANY or src_object.id == tx.src_id
        type_match = src_object.type is None or src_object.type == ANY or src_object.type == tx.src_type
        subtype_match = src_object.subtype is None or src_object.subtype == ANY or src_object.subtype == tx.src_subtype
        return id_match and type_match and subtype_match

    def check_destination(self, tx, rule):
        return rule.dst == ANY or (
                rule.dstAddressType == 'ONE_TIME' and tx.dst_type == PolicySrcOrDestType.ONE_TIME_ADDRESS) or any(
            [self._check_dst_object(tx, dst_object) for dst_object in rule.dst])

    def _check_dst_object(self, tx, dst_object):
        id_match = dst_object.id is None or dst_object.id == ANY or dst_object.id == tx.dst_id
        type_match = dst_object.type is None or dst_object.type == ANY or dst_object.type == tx.dst_type
        subtype_match = dst_object.subtype is None or dst_object.subtype == ANY or dst_object.subtype == tx.dst_subtype
        return id_match and type_match and subtype_match

    def check_approvers(self, tx, rule):
        if rule.authorization_groups is None:
            return True
        authorizied_approvers_sets = self._get_authorizied_approvers_sets(tx, rule.authorizationGroups)
        approvers_set = set(tx.approvers)
        if rule.authorizationGroups['allowOperatorAsAuthorizer']:
            approvers_set.add(tx.initiator)
        return approvers_set in authorizied_approvers_sets

    def check_transaction_type(self, tx, rule):
        if rule.transaction_type == tx.operation:
            return True
        elif rule.transaction_type == PolicyTransactionType.CONTRACT_CALL:
            return rule.applyForApprove and tx.operation == PolicyTransactionType.APPROVE or rule.apply_for_typed_message and tx.operation == PolicyTransactionType.TYPED_MESSAGE

        return False

    def check_dst_address_type(self, tx, rule):
        if rule.dst_address_type == PolicyDestAddressType.ANY:
            return True
        elif rule.dst_address_type == PolicyDestAddressType.ONE_TIME:
            return tx.dst_type == PolicySrcOrDestType.ONE_TIME_ADDRESS
        elif rule.dst_address_type == PolicyDestAddressType.WHITELISTED:
            return tx.dst_type != PolicySrcOrDestType.ONE_TIME_ADDRESS
        else:
            raise ValueError("dstAddressType", rule.dstAddressType)

    def _get_authorizied_approvers_sets(self, tx, authorization_groups):
        authorizied_approvers_sets = []
        logic = authorization_groups['logic']

        for group in authorization_groups['groups']:
            threshold = group['th']

            users = set()
            if 'users' in group:
                users = set(group['users'])
            if authorization_groups['allowOperatorAsAuthorizer']:
                users.add(tx.initiator)
            if 'usersGroups' in group:
                user_group_ids = set(group['usersGroups'])
                for user_group_id in user_group_ids:
                    users = users.union(set(self.groups_to_users_mapping[user_group_id]))
            group_authorized_users = [set(combination) for combination in combinations(users, threshold)]
            authorizied_approvers_sets.append(group_authorized_users)

        if logic == 'OR':
            authorizied_approvers_sets = [set(link) for link in chain.from_iterable(authorizied_approvers_sets)]
        elif logic == 'AND':
            authorizied_approvers_sets = [set.union(*set_from_every_group) for set_from_every_group in
                                          product(*authorizied_approvers_sets)]
        else:
            raise ValueError("authorizationGroups logic", logic)

        return [set(authorizied_approvers_set) for authorizied_approvers_set in authorizied_approvers_sets]

    def check_tx(self, tx: Transaction):
        allow = False
        matched_rule = None

        for rule in self.rules:
            asset_match = self.check_asset(tx, rule)
            # initiator currently unsupported
            # initiator_match = self.check_initiator(tx, rule)
            initiator_match = True
            value_match = self.check_value(tx, rule)
            source_match = self.check_source(tx, rule)
            destination_match = self.check_destination(tx, rule)
            # approvers currently unsupported
            # approvers_match = self.check_approvers(tx, rule)
            approvers_match = True
            transaction_type_match = self.check_transaction_type(tx, rule)
            dst_address_type_match = self.check_dst_address_type(tx, rule)

            if all([asset_match, initiator_match, value_match, source_match, destination_match, approvers_match,
                    transaction_type_match, dst_address_type_match]):
                matched_rule = rule
                break

        if matched_rule is not None and matched_rule.action in (PolicyAction.ALLOW, PolicyAction.TWO_TIER):
            allow = True
            self.transaction_history.append(tx)

        return PolicyCheckResult(allow=allow, matched_rule=matched_rule)
