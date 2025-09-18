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
