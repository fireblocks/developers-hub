import dataclasses
from fireblocks_sdk import PolicyRule

ANY = '*'


@dataclasses.dataclass
class SrcDst:
    id: str = None
    type: str = None
    subtype: str = None


class AuthorizationGroup:
    users = 'users'
    usersGroups = 'usersGroups'


def convert_keys_to_snake_case(input_dict):
    snake_case_dict = {}
    for key, value in input_dict.items():
        snake_case_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
        if snake_case_key not in rule_attributes:
            continue
        snake_case_dict[snake_case_key] = value
    return snake_case_dict


rule_attributes = [
    'type',
    'action',
    'asset',
    'amount_currency',
    'amount_scope',
    'amount',
    'period_sec',
    'external_descriptor',
    'operator',
    'operators',
    'transaction_type',
    'operator_services',
    'designated_signer',
    'designated_signers',
    'src_type',
    'src_sub_type',
    'src_id',
    'src',
    'dst_type',
    'dst_sub_type',
    'dst_id',
    'dst',
    'dst_address_type',
    'authorizers',
    'authorizers_count',
    'authorization_groups',
    'amount_aggregation',
    'raw_message_signing',
    'apply_for_approve',
    'apply_for_typed_message'
]


class FormattedPolicyRule(PolicyRule):
    def __init__(self, policy_rule: PolicyRule):
        policy_dict = convert_keys_to_snake_case(policy_rule.to_dict())
        super().__init__(**policy_dict)
        self.operators = self.parse_operators(policy_rule.operators)
        self.src = self.parse_src_dst(policy_rule.src)
        self.dst = self.parse_src_dst(policy_rule.dst)
        self.amount = float(self.amount)

    def format_policy_rule_object(self, policy_rule_object):
        policy_rule_object.operators = self.parse_operators(policy_rule_object.operators)
        policy_rule_object.src = self.parse_src_dst(policy_rule_object.src)
        policy_rule_object.dst = self.parse_src_dst(policy_rule_object.dst)
        return policy_rule_object

    @staticmethod
    def parse_src_dst(src_dst_dict):
        src_dst_objects = []
        for id_object in src_dst_dict['ids']:
            if id_object == [ANY]:
                return ANY
            elif len(id_object) == 2:
                src_dst_objects.append(SrcDst(id=id_object[0], type=id_object[1]))
            elif len(id_object) == 3:
                src_dst_objects.append(SrcDst(id=id_object[0], type=id_object[1], subtype=id_object[2]))
        return src_dst_objects

    @staticmethod
    def parse_operators(operators):
        if operators == {"wildcard": ANY}:
            return ANY
        parsed_operators = dict(users=operators.get(AuthorizationGroup.users),
                                users_groups=operators.get(AuthorizationGroup.usersGroups))
        return parsed_operators
