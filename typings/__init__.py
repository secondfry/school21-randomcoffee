from typing import Optional, TypedDict


class Token(TypedDict):
    access_token: str
    created_at: Optional[int]
    expires_at: float
    expires_in: int
    refresh_token: str
    scope: Optional[str]
    token_type: str


class TokenUser(TypedDict):
    user_id: str
