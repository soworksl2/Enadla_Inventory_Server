from datetime import datetime
from dataclasses import dataclass

@dataclass
class TokenInformation:

    user_info_id: str = None
    amount_of_tokens: int = 0
    datetime_last_token_recharge: datetime = None