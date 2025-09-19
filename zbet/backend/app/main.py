from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
    
from sqlalchemy.orm import Session
from typing import Annotated, Optional

from . import auth, crud, models, schemas, cleaners, serializers, betting_utils
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


# Betting API endpoints
@app.get("/api/events", response_model=list[schemas.SportEventResponse])
def get_betting_events(
    skip: int = 0, 
    limit: int = 100, 
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get all betting events with optional status filter"""
    events = crud.get_sport_events(db, skip=skip, limit=limit, status=status)
    
    # Convert events to response format using model's to_dict method
    response_events = []
    for event in events:
        event_data = event.to_dict(db)
        response_events.append(schemas.SportEventResponse(**event_data))
    
    return response_events


@app.get("/api/events/{event_id}", response_model=schemas.SportEventResponse)
def get_betting_event(event_id: int, db: Session = Depends(get_db)):
    """Get a single betting event by ID"""
    event = crud.get_sport_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Convert to response format using model's to_dict method
    event_data = event.to_dict(db)
    return schemas.SportEventResponse(**event_data)


@app.post("/api/events", response_model=schemas.SportEventResponse)
def create_betting_event(
    event_request: schemas.CreateEventRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new betting event"""
    try:
        # Validate the event data
        event_data = event_request.event_data
        
        # Basic validation
        if not event_data.title.strip():
            raise HTTPException(status_code=400, detail="Event title is required")
        if not event_data.description.strip():
            raise HTTPException(status_code=400, detail="Event description is required")
        
        # Validate datetime strings and ensure they're in the future
        try:
            event_start_time = datetime.fromisoformat(event_data.event_start_time.replace('Z', '+00:00')).replace(tzinfo=None)
            settlement_deadline = datetime.fromisoformat(event_data.settlement_deadline.replace('Z', '+00:00')).replace(tzinfo=None)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        now = datetime.utcnow()
        if event_start_time <= now:
            raise HTTPException(status_code=400, detail="Event start time must be in the future")
        if settlement_deadline <= event_start_time:
            raise HTTPException(status_code=400, detail="Settlement deadline must be after event start time")
        
        # Validate category
        try:
            models.EventCategory(event_data.category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {event_data.category}")
        
        # Validate betting system type
        try:
            models.BettingSystemType(event_data.betting_system_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid betting system type: {event_data.betting_system_type}")
        
        # Create the sport event
        sport_event = crud.create_sport_event(db, event_data)
        
        # Handle pari-mutuel specific data
        if event_data.betting_system_type == "pari_mutuel":
            if not event_request.pari_mutuel_data:
                raise HTTPException(status_code=400, detail="Pari-mutuel data is required for pari-mutuel events")
            
            pari_data = event_request.pari_mutuel_data
            
            # Validate pari-mutuel data
            if len(pari_data.betting_pools) < 2:
                raise HTTPException(status_code=400, detail="At least 2 betting pools are required")
            
            # Validate betting pools
            outcome_names = []
            for pool in pari_data.betting_pools:
                if not pool.outcome_name.strip():
                    raise HTTPException(status_code=400, detail="Pool outcome name is required")
                if not pool.outcome_description.strip():
                    raise HTTPException(status_code=400, detail="Pool outcome description is required")
                
                outcome_name = pool.outcome_name.lower().strip()
                if outcome_name in outcome_names:
                    raise HTTPException(status_code=400, detail="Outcome names must be unique")
                outcome_names.append(outcome_name)
            
            # Create the pari-mutuel event and pools
            crud.create_pari_mutuel_event(db, sport_event.id, pari_data)
        
        # Return the created event with all data
        event_dict = sport_event.to_dict(db)
        return schemas.SportEventResponse(**event_dict)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic error message
        print(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@app.get("/api/users/me/bets", response_model=list[schemas.BetResponse])
def get_current_user_bets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all bets for the current authenticated user"""
    try:
        bets = crud.get_user_bets(db, user_id=current_user.id, skip=skip, limit=limit)
        
        # Transform bets to response format
        bet_responses = []
        for bet in bets:
            try:
                bet_response = serializers.transform_bet_to_response(bet, db)
                bet_responses.append(bet_response)
            except Exception as e:
                print(f"Error transforming bet {bet.id}: {str(e)}")
                # Skip this bet and continue with others
                continue
        
        return bet_responses
        
    except Exception as e:
        print(f"Error fetching user bets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user bets")


@app.post("/api/bets", response_model=schemas.BetResponse)
def place_bet(
    bet_request: schemas.BetPlacementRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Place a new bet for the current authenticated user"""
    try:
        # Get the sport event and validate
        sport_event = crud.get_sport_event(db, bet_request.sport_event_id)
        if not sport_event:
            raise HTTPException(status_code=404, detail="Sport event not found")
        
        # Validate the bet request
        betting_utils.validate_bet_for_event(sport_event, bet_request.predicted_outcome, bet_request.amount)
        
        # Create the bet record
        bet = crud.create_bet(db, bet_request, current_user.id)
        
        # Process betting system-specific logic
        betting_utils.process_bet_placement(db, bet, sport_event)
        db.commit()  # Commit all changes
        
        # Transform to response format
        bet_response = serializers.transform_bet_to_response(bet, db)
        
        return bet_response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error placing bet: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to place bet")


@app.get("/api/statistics", response_model=schemas.StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """Get overall platform statistics"""
    try:
        # Count total bets (only confirmed deposits)
        total_bets = db.query(models.Bet).filter(
            models.Bet.deposit_status == models.DepositStatus.CONFIRMED
        ).count()
        
        # Count total events
        total_events = db.query(models.SportEvent).count()
        
        # Count total users
        total_users = db.query(models.User).count()
        
        return schemas.StatisticsResponse(
            total_bets=total_bets,
            total_events=total_events,
            total_users=total_users
        )
        
    except Exception as e:
        print(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")