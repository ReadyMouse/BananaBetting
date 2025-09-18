from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    zcash_account = Column(String, primary_key=False)
    zcash_address = Column(String, unique=True, index=True)
    zcash_transparent_address = Column(String, unique=True, index=True)
    balance = Column(String, unique=False, index=True)

