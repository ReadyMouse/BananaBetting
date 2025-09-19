"""
Betting system utilities and business logic.

This module contains betting system-specific logic that doesn't belong in CRUD operations.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models


def update_pari_mutuel_pool_stats(db: Session, bet: models.Bet, sport_event: models.SportEvent):
    """Update pari-mutuel pool statistics when a bet is placed"""
    # Get the pari-mutuel event
    pari_event = db.query(models.PariMutuelEvent).filter(
        models.PariMutuelEvent.sport_event_id == sport_event.id
    ).first()
    
    if not pari_event:
        raise HTTPException(
            status_code=500, 
            detail="Pari-mutuel event not found for this sport event"
        )
    
    # Find the specific pool for this outcome
    pool = db.query(models.PariMutuelPool).filter(
        models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
        models.PariMutuelPool.outcome_name == bet.predicted_outcome
    ).first()
    
    if not pool:
        # Get available pools for better error message
        available_pools = db.query(models.PariMutuelPool).filter(
            models.PariMutuelPool.pari_mutuel_event_id == pari_event.id
        ).all()
        available_names = [p.outcome_name for p in available_pools]
        
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid predicted outcome: '{bet.predicted_outcome}'. Available options: {available_names}"
        )
    
    # Update pool statistics
    pool.pool_amount += bet.amount
    pool.bet_count += 1
    
    # Update total pool amount in pari-mutuel event
    pari_event.total_pool += bet.amount
    
    # Store pool ID in bet metadata for future reference
    bet.set_pari_mutuel_pool_id(pool.id)


def validate_bet_for_event(sport_event: models.SportEvent, predicted_outcome: str, amount: float):
    """Validate that a bet can be placed on the given event"""
    if sport_event.status != models.EventStatus.OPEN:
        raise HTTPException(status_code=400, detail="Betting is not open for this event")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    
    # Add betting system-specific validations here in the future
    # For example, checking minimum/maximum bet amounts, etc.


def process_bet_placement(db: Session, bet: models.Bet, sport_event: models.SportEvent):
    """Process betting system-specific logic after a bet is placed"""
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        update_pari_mutuel_pool_stats(db, bet, sport_event)
    elif sport_event.betting_system_type == models.BettingSystemType.FIXED_ODDS:
        # TODO: Implement fixed odds betting logic
        pass
    elif sport_event.betting_system_type == models.BettingSystemType.SPREAD:
        # TODO: Implement spread betting logic
        pass
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported betting system: {sport_event.betting_system_type}"
        )
