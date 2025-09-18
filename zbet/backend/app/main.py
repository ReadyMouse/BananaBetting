from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
    
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from . import auth, crud, models, schemas, cleaners
from .database import SessionLocal, engine

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000", "https://zbet-frontend.vercel.app" # React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependency
def authenticate_user(db: Session, zcash_address: str, password: str):
    user = crud.get_user_by_username(db, zcash_address)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + timedelta(minutes=300)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, auth.SECRET_KEY, algorithm=auth.ALGORITHM)
        return encoded_jwt
    

def get_current_user(db: Session = Depends(get_db), token: str = Depends(auth.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@app.get("/token_status/")
def check_token_status(token: str = Depends(auth.oauth2_scheme)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        expiration = payload.get("exp")
        current_time = datetime.now(timezone.utc).timestamp()

        if expiration < current_time:
            return {"status": "expired"}
        return {"status": "valid"}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/login/")
def login_for_access_token(db: Session = Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"},)
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.UserCreate = Depends(get_current_user)):
    return current_user

@app.post("/register/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    cleaners.validate_email(db, email=user.email)
    cleaners.validate_username(db, username=user.username)
    cleaners.validate_password(db, password=user.password)
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    users = crud.get_some_users(db, skip=skip, limit=limit, current_user_id=current_user.id)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user




# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.post("/zcash/send-to-address/")
def z_cash_send_to_address(transaction: schemas.Transaction, db: Session = Depends(get_db)):
    # Process Zcash transaction (add your Zcash-specific logic here)
    # For example: zcash_wallet.send_to_address(transaction.address, transaction.amount)
    
    return {
        "message": "Zcash transaction processed successfully",
        "address": transaction.address,
        "amount": transaction.amount
    }




import requests

API_KEY = '4e7768a1-449d-40c2-8048-c3dbe16a2170'

@app.get("/api/crypto")
def get_crypto_data(start: str, end: str):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical?symbol=ZEC&convert=USD&time_start={start}&time_end={end}"
    headers = {
        "X-CMC_PRO_API_KEY": API_KEY,
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()