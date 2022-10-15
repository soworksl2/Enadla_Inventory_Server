from datetime import datetime
from dataclasses import dataclass

from core.helpers import own_json

@dataclass
class TokenInformation:

    user_info_id: str = None
    amount_of_tokens: int = 0
    datetime_last_token_recharge: datetime = None

    def get_client_dict(self):
        output = {
            'user_info_id': self.user_info_id,
            'amount_of_tokens': self.amount_of_tokens,
            'datetime_last_token_recharge': self.datetime_last_token_recharge
        }

        return own_json.process_json_obj(output)
