
class TokenInformation:
    def __init__(self, account_id = None, free_tokens = 0, normal_tokens = 0, last_charge_free_tokens = None) -> None:
        self.account_id = account_id
        self.free_tokens = free_tokens
        self.normal_tokens = normal_tokens
        self.last_charge_free_tokens = last_charge_free_tokens