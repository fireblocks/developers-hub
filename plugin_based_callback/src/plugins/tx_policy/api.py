from fireblocks_sdk import FireblocksSDK
from src.settings import FIREBLOCKS_API_KEY, FIREBLOCKS_API_SECRET

FIREBLOCKS_API_URL = 'https://api.fireblocks.io'  # Choose the right api url for your workspace type

fireblocks = FireblocksSDK(FIREBLOCKS_API_SECRET, FIREBLOCKS_API_KEY, api_base_url=FIREBLOCKS_API_URL)


def get_groups_to_users_mapping():
    result = fireblocks.get_user_groups()
    return {group['id']: group['memberIds'] for group in result if group['status'] == 'ACTIVE'}


def get_active_policy():
    active_policy = fireblocks.get_active_policy()
    return active_policy
