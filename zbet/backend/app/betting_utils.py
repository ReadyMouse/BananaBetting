"""
Betting system utilities and business logic.

This module contains betting system-specific logic that doesn't belong in CRUD operations.
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, serializers
from .zcash_mod import zcash_wallet
from .config import settings


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
    current_status = sport_event.get_current_status()
    if current_status != models.EventStatus.OPEN:
        if current_status == models.EventStatus.CLOSED:
            raise HTTPException(status_code=400, detail="Event has ended - betting is now closed")
        else:
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


def settle_event(db: Session, event_id: int, winning_outcome: str, pool_address: str = None) -> schemas.SettlementResponse:
    """
    Settle an event with the winning outcome and process all payouts.
    
    Args:
        db: Database session
        event_id: ID of the event to settle
        winning_outcome: The winning outcome name
        pool_address: Zcash address to send from (optional, uses config if not provided)
        
    Returns:
        SettlementResponse with settlement details and payout records
    """
    # Use configured pool address if none provided
    if pool_address is None:
        pool_address = settings.get_pool_address()
    # Get the event
    sport_event = db.query(models.SportEvent).filter(models.SportEvent.id == event_id).first()
    if not sport_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event can be settled
    current_status = sport_event.get_current_status()
    if current_status == models.EventStatus.SETTLED:
        raise HTTPException(status_code=400, detail="Event is already settled")
    
    if current_status not in [models.EventStatus.OPEN, models.EventStatus.CLOSED]:
        raise HTTPException(status_code=400, detail="Event is not open for settlement")
    
    # Validate winning outcome exists for this event
    _validate_winning_outcome(db, sport_event, winning_outcome)
    
    # Mark winning pool for pari-mutuel events
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        _mark_winning_pool(db, sport_event, winning_outcome)
    
    # Process all bets for this event
    payout_records = _process_event_payouts(db, sport_event, winning_outcome)
    
    # Build and send Zcash transaction if there are payouts
    transaction_id = None
    if payout_records:
        transaction_id = _send_batch_payouts(pool_address, payout_records)
        
        # Update payout records with transaction ID
        for payout_record in payout_records:
            payout = db.query(models.Payout).filter(models.Payout.bet_id == payout_record.bet_id).first()
            if payout:
                payout.zcash_transaction_id = transaction_id
                payout.is_processed = True
    
    # Mark event as settled
    sport_event.status = models.EventStatus.SETTLED
    # Set settlement time in EST
    from datetime import timezone, timedelta
    est_timezone = timezone(timedelta(hours=-5))
    sport_event.settled_at = datetime.now(est_timezone).replace(tzinfo=None)
    
    # Mark winning outcome in pari-mutuel event if applicable
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        pari_event = db.query(models.PariMutuelEvent).filter(
            models.PariMutuelEvent.sport_event_id == event_id
        ).first()
        if pari_event:
            pari_event.winning_outcome = winning_outcome
    
    db.commit()
    
    # Calculate totals
    total_payout_amount = sum(record.payout_amount for record in payout_records)
    
    return schemas.SettlementResponse(
        event_id=event_id,
        winning_outcome=winning_outcome,
        total_payouts=len(payout_records),
        total_payout_amount=total_payout_amount,
        transaction_id=transaction_id,
        settled_at=sport_event.settled_at.isoformat() + 'Z',
        payout_records=payout_records
    )


def _validate_winning_outcome(db: Session, sport_event: models.SportEvent, winning_outcome: str):
    """Validate that the winning outcome is valid for this event"""
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        # Check if outcome exists in pari-mutuel pools
        pari_event = db.query(models.PariMutuelEvent).filter(
            models.PariMutuelEvent.sport_event_id == sport_event.id
        ).first()
        
        if not pari_event:
            raise HTTPException(status_code=500, detail="Pari-mutuel event not found")
        
        pool = db.query(models.PariMutuelPool).filter(
            models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
            models.PariMutuelPool.outcome_name == winning_outcome
        ).first()
        
        if not pool:
            available_pools = db.query(models.PariMutuelPool).filter(
                models.PariMutuelPool.pari_mutuel_event_id == pari_event.id
            ).all()
            available_names = [p.outcome_name for p in available_pools]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid winning outcome: '{winning_outcome}'. Available options: {available_names}"
            )
    else:
        # For other betting systems, validate against existing bets
        existing_bet = db.query(models.Bet).filter(
            models.Bet.sport_event_id == sport_event.id,
            models.Bet.predicted_outcome == winning_outcome
        ).first()
        
        if not existing_bet:
            raise HTTPException(
                status_code=400, 
                detail=f"No bets found for outcome: '{winning_outcome}'"
            )


def _mark_winning_pool(db: Session, sport_event: models.SportEvent, winning_outcome: str):
    """Mark the winning pool for pari-mutuel events"""
    pari_event = db.query(models.PariMutuelEvent).filter(
        models.PariMutuelEvent.sport_event_id == sport_event.id
    ).first()
    
    if pari_event:
        # Reset all pools to not winning
        db.query(models.PariMutuelPool).filter(
            models.PariMutuelPool.pari_mutuel_event_id == pari_event.id
        ).update({"is_winning_pool": False})
        
        # Mark winning pool
        db.query(models.PariMutuelPool).filter(
            models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
            models.PariMutuelPool.outcome_name == winning_outcome
        ).update({"is_winning_pool": True})


def _process_event_payouts(db: Session, sport_event: models.SportEvent, winning_outcome: str) -> List[schemas.PayoutRecord]:
    """
    Process all bets for an event and create payout records for winners.
    
    Returns list of PayoutRecord objects for the settlement response.
    """
    payout_records = []
    
    # Get all confirmed bets for this event
    bets = db.query(models.Bet).filter(
        models.Bet.sport_event_id == sport_event.id,
        models.Bet.deposit_status == models.DepositStatus.CONFIRMED
    ).all()

    # Calculate total fees once for the entire event
    total_house_fees = 0.0
    total_creator_fees = 0.0
    total_validator_fees = 0.0
    
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        pari_event = db.query(models.PariMutuelEvent).filter(
            models.PariMutuelEvent.sport_event_id == sport_event.id
        ).first()
        
        if pari_event:
            # Find winning pool
            winning_pool = db.query(models.PariMutuelPool).filter(
                models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
                models.PariMutuelPool.outcome_name == winning_outcome
            ).first()
            
            if winning_pool:
                losing_pool_gross = pari_event.total_pool - winning_pool.pool_amount
                
                # Only calculate fees if there's a losing pool
                if losing_pool_gross > 0:
                    total_house_fees = losing_pool_gross * pari_event.house_fee_percentage
                    total_creator_fees = losing_pool_gross * pari_event.creator_fee_percentage
                    total_validator_fees = losing_pool_gross * pari_event.validator_fee_percentage

    # Process all bets
    for bet in bets:
        # Determine bet outcome
        if bet.predicted_outcome == winning_outcome:
            bet.outcome = models.BetOutcome.WIN
            
            # Calculate the settlement payout (fees already deducted for pari-mutuel)
            net_payout = _calculate_settlement_payout(db, sport_event, bet, winning_outcome)
            
            # Store payout details in bet
            bet.payout_amount = net_payout
            
            # Create payout record in database
            payout = models.Payout(
                user_id=bet.user_id,
                bet_id=bet.id,
                sport_event_id=sport_event.id,
                payout_amount=net_payout,
                recipient_address=bet.user.zcash_address,
                payout_type="user_winning",
                is_processed=False
            )
            db.add(payout)
            
            # Add to response records
            payout_records.append(schemas.PayoutRecord(
                user_id=bet.user_id,
                bet_id=bet.id,
                payout_amount=net_payout,
                payout_type="user_winning",
                recipient_address=bet.user.zcash_address
            ))
            
        else:
            # Losing bet
            bet.outcome = models.BetOutcome.LOSS
            bet.payout_amount = 0.0
    
    # Create house fee payout record if there are fees to collect
    if total_house_fees > 0:
        # Get house address from environment configuration
        house_address = settings.get_house_address()
        
        house_payout = models.Payout(
            user_id=None,  # No user for house fees
            bet_id=None,   # No specific bet
            sport_event_id=sport_event.id,
            payout_amount=total_house_fees,
            recipient_address=house_address,
            payout_type="house_fee",
            is_processed=False
        )
        db.add(house_payout)
        
        payout_records.append(schemas.PayoutRecord(
            user_id=None,
            bet_id=None,
            payout_amount=total_house_fees,
            payout_type="house_fee",
            recipient_address=house_address
        ))
    
    # Create creator fee payout record if there are fees to collect
    if total_creator_fees > 0:
        # Get creator address from the event data
        creator_address = sport_event.creator.zcash_address
        
        creator_payout = models.Payout(
            user_id=sport_event.creator_id,  # Get user id from the event data
            bet_id=None,   # No specific bet
            sport_event_id=sport_event.id,
            payout_amount=total_creator_fees,
            recipient_address=creator_address,
            payout_type="creator_fee",
            is_processed=False
        )
        db.add(creator_payout)
        
        payout_records.append(schemas.PayoutRecord(
            user_id=sport_event.creator_id,
            bet_id=None,
            payout_amount=total_creator_fees,
            payout_type="creator_fee",
            recipient_address=creator_address
        ))
    
    # Create validator fee payout record if there are fees to collect
    if total_validator_fees > 0:
        # TODO: Implement validator reward distribution when validation system is ready
        # For now, validator fees are calculated and reserved but not paid out
        # until we have a system to determine which validators to reward.
        # The fees will be held in the pool until validator distribution is implemented.
        
        # Note: When implementing validator rewards later, you'll need to:
        # 1. Get list of validators who participated in outcome verification
        # 2. Calculate their individual rewards (split total_validator_fees among them)
        # 3. Create individual payout records for each validator's address
        pass
    
    return payout_records


def _calculate_settlement_payout(db: Session, sport_event: models.SportEvent, bet: models.Bet, winning_outcome: str) -> float:
    """
    Calculate the settlement payout for a winning bet.
    
    For pari-mutuel: Returns net payout (fees already deducted from losing pool)
    For other systems: Returns gross payout (before fee deduction)
    
    This is the authoritative payout calculation used during settlement,
    separate from the display-only serializer calculations.
    """
    
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        # Get pari-mutuel event
        pari_event = db.query(models.PariMutuelEvent).filter(
            models.PariMutuelEvent.sport_event_id == sport_event.id
        ).first()
        
        if not pari_event:
            return bet.amount  # Fallback to bet amount
        
        # Find the winning pool
        winning_pool = db.query(models.PariMutuelPool).filter(
            models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
            models.PariMutuelPool.outcome_name == winning_outcome
        ).first()
        
        if not winning_pool or winning_pool.pool_amount <= 0:
            return bet.amount  # Fallback to bet amount
        
        # Calculate total losing pools (all pools except the winning one)
        losing_pool_gross = pari_event.total_pool - winning_pool.pool_amount
        
        # Special case: No losing pool means no one bet against the winners
        # In this case, just return everyone's bet without penalty (no fees)
        if losing_pool_gross <= 0:
            return bet.amount
        
        # Normal pari-mutuel formula:
        # Payout = Original Bet + (User's Bet / Winning Pool) × (Losing Pools - Fees)
        
        # Deduct fees from the losing pool (fees come off the top)
        total_fee_percentage = pari_event.house_fee_percentage + pari_event.creator_fee_percentage + pari_event.validator_fee_percentage
        losing_pool_after_fees = losing_pool_gross * (1 - total_fee_percentage)
        
        # User gets their bet back + proportional share of net losing money
        user_share_ratio = bet.amount / winning_pool.pool_amount
        share_of_losing_money = losing_pool_after_fees * user_share_ratio
        net_payout = bet.amount + share_of_losing_money
        
        return net_payout
        
    elif sport_event.betting_system_type == models.BettingSystemType.FIXED_ODDS:
        # Fixed odds: Bet Amount × Odds
        # TODO: Get actual odds from database when implemented
        # For now, use the same logic as serializer but this should be from stored odds
        odds_map = {
            "team_a_wins": 2.1, "team_b_wins": 1.9, "tie": 3.2, "draw": 3.2,
            "player_scores": 2.8, "player_assists": 3.1, "player_homers": 4.5,
            "over": 1.95, "under": 1.95, "option_a": 2.1, "option_b": 2.1,
        }
        
        odds = odds_map.get(bet.predicted_outcome, 2.1)  # Default 2.1x odds
        return bet.amount * odds
        
    elif sport_event.betting_system_type == models.BettingSystemType.SPREAD:
        # Spread betting: typically around 1.9x odds
        return bet.amount * 1.9
        
    else:
        # Fallback: 1:1 payout
        return bet.amount

def _send_batch_payouts(pool_address: str, payout_records: List[schemas.PayoutRecord]) -> str:
    """
    Send batch payouts using Zcash z_sendmany.
    
    Returns the transaction operation ID.
    """
    if not payout_records:
        raise HTTPException(status_code=400, detail="No payouts to process")
    
    # Build recipients list, consolidating multiple payouts to same address
    address_amounts = {}
    for record in payout_records:
        if record.recipient_address in address_amounts:
            address_amounts[record.recipient_address] += record.payout_amount
        else:
            address_amounts[record.recipient_address] = record.payout_amount
    
    # Convert to z_sendmany format
    recipients = [
        {"address": address, "amount": amount}
        for address, amount in address_amounts.items()
        if amount > 0  # Only send positive amounts
    ]
    
    if not recipients:
        raise HTTPException(status_code=400, detail="No valid recipients for payout")
    
    # Send the batch transaction
    try:
        operation_id = zcash_wallet.z_sendmany(
            from_address=pool_address,
            recipients=recipients,
            minconf=1
        )
        return operation_id
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to send batch payout transaction: {str(e)}"
        )
