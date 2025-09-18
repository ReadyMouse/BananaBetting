from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    zcash_account: str
    zcash_address: str
    zcash_transparent_address: str
    balance: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class WalletAuth(BaseModel):
    wallet_address: str
    signature: str


class Transaction(BaseModel):
    address: str
    amount: float


# Betting schemas
class PariMutuelPoolResponse(BaseModel):
    id: int
    outcome_name: str
    outcome_description: str
    pool_amount: float
    bet_count: int
    payout_ratio: float | None = None
    is_winning_pool: bool = False

    class Config:
        from_attributes = True


class PariMutuelEventResponse(BaseModel):
    id: int
    minimum_bet: float
    maximum_bet: float
    house_fee_percentage: float
    oracle_fee_percentage: float
    total_pool: float
    winning_outcome: str | None = None
    betting_pools: list[PariMutuelPoolResponse] = []

    class Config:
        from_attributes = True


class SportEventResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    status: str
    betting_system_type: str
    created_at: str
    event_start_time: str
    settlement_deadline: str
    settled_at: str | None = None
    betting_system_data: dict | None = None  # Generic field for any betting system data

    class Config:
        from_attributes = True
