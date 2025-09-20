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
    creator_fee_percentage: float
    validator_fee_percentage: float
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
    event_end_time: str
    settlement_time: str  # Renamed from settlement_deadline for clarity
    settled_at: str | None = None
    betting_system_data: dict | None = None  # Generic field for any betting system data

    class Config:
        from_attributes = True


# Schemas for creating events
class SportEventCreate(BaseModel):
    title: str
    description: str
    category: str
    betting_system_type: str
    event_start_time: str
    event_end_time: str
    settlement_time: str  # Renamed from settlement_deadline for clarity


class PariMutuelPoolCreate(BaseModel):
    outcome_name: str
    outcome_description: str


class PariMutuelEventCreate(BaseModel):
    betting_pools: list[PariMutuelPoolCreate]


class CreateEventRequest(BaseModel):
    event_data: SportEventCreate
    pari_mutuel_data: PariMutuelEventCreate | None = None


# Bet schemas for responses
class BetResponse(BaseModel):
    id: int
    betId: str  # Use betId to match frontend interface
    amount: float
    predicted_outcome: str
    outcome: str | None = None
    status: str  # Computed from deposit_status and outcome
    placedAt: str  # bet_placed_at formatted
    settledAt: str | None = None
    potentialPayout: float | None = None  # Will be calculated based on betting system
    bet: SportEventResponse  # The event this bet is on

    class Config:
        from_attributes = True


class UserBetListResponse(BaseModel):
    bets: list[BetResponse]


# Bet placement request schema
class BetPlacementRequest(BaseModel):
    sport_event_id: int
    predicted_outcome: str
    amount: float
    
    class Config:
        from_attributes = True


# Statistics response schema
class StatisticsResponse(BaseModel):
    total_bets: int
    total_events: int
    total_users: int


# Settlement schemas
class SettlementRequest(BaseModel):
    winning_outcome: str
    
    class Config:
        from_attributes = True


class PayoutRecord(BaseModel):
    user_id: int | None = None  # Null for house/creator fees
    bet_id: int | None = None   # Null for house/creator fees
    payout_amount: float
    payout_type: str = "user_winning"  # "user_winning", "house_fee", "creator_fee", "validator_fee"
    recipient_address: str
    house_fee_deducted: float = 0.0
    creator_fee_deducted: float = 0.0
    
    class Config:
        from_attributes = True


class SettlementResponse(BaseModel):
    event_id: int
    winning_outcome: str
    total_payouts: int
    total_payout_amount: float
    transaction_id: str | None = None
    settled_at: str
    payout_records: list[PayoutRecord]
    
    class Config:
        from_attributes = True


class ValidationRequest(BaseModel):
    predicted_outcome: str
    confidence_level: str | None = None  # "high", "medium", "low"
    validation_notes: str | None = None
    
    class Config:
        from_attributes = True


class ValidationResponse(BaseModel):
    id: int
    user_id: int
    sport_event_id: int
    predicted_outcome: str
    validated_at: str
    confidence_level: str | None = None
    validation_notes: str | None = None
    is_correct_validation: bool | None = None
    validator_reward_amount: float | None = None
    
    class Config:
        from_attributes = True


class ValidationSummary(BaseModel):
    sport_event_id: int
    total_validations: int
    outcome_counts: dict[str, int]  # outcome -> count
    consensus_outcome: str | None = None
    consensus_percentage: float | None = None
    validation_deadline: str | None = None
    
    class Config:
        from_attributes = True
