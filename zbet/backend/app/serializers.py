"""
Data serializers for transforming database models to API response formats.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas


def _calculate_potential_payout(bet: models.Bet, sport_event: models.SportEvent, db: Session) -> float:
    """Calculate potential payout for a bet based on the betting system type"""
    
    # If the bet has already been settled, return the actual payout
    if bet.outcome is not None and bet.payout_amount is not None:
        return bet.payout_amount
    
    if sport_event.betting_system_type == models.BettingSystemType.PARI_MUTUEL:
        return _calculate_pari_mutuel_payout(bet, sport_event, db)
    elif sport_event.betting_system_type == models.BettingSystemType.FIXED_ODDS:
        return _calculate_fixed_odds_payout(bet, sport_event, db)
    elif sport_event.betting_system_type == models.BettingSystemType.SPREAD:
        return _calculate_spread_payout(bet, sport_event, db)
    else:
        # Fallback: return bet amount (1:1 payout)
        return bet.amount


def _calculate_pari_mutuel_payout(bet: models.Bet, sport_event: models.SportEvent, db: Session) -> float:
    """Calculate estimated payout for pari-mutuel betting"""
    pari_event = db.query(models.PariMutuelEvent).filter(
        models.PariMutuelEvent.sport_event_id == sport_event.id
    ).first()
    
    if not pari_event:
        return bet.amount
    
    # Find the pool for this bet's predicted outcome
    pool = db.query(models.PariMutuelPool).filter(
        models.PariMutuelPool.pari_mutuel_event_id == pari_event.id,
        models.PariMutuelPool.outcome_name == bet.predicted_outcome
    ).first()
    
    if not pool or pool.pool_amount <= 0:
        return bet.amount
    
    # Calculate fees
    house_fee = pari_event.house_fee_percentage
    creator_fee = pari_event.creator_fee_percentage
    total_fee_percentage = house_fee + creator_fee
    
    # Calculate pari-mutuel payout for display using correct formula
    # Payout = Original Bet + (User's Bet / Winning Pool) × Losing Pools - Fees
    # 
    # Example: 
    # - Total pools: $100 (Pool A: $30, Pool B: $70)
    # - Fees: 10% = $10
    # - If Pool A wins: each $1 bet on A gets $1 + ($1/$30) × $70 - fees
    
    if pool.pool_amount > 0:
        # Calculate losing pool total
        losing_pool_total = pari_event.total_pool - pool.pool_amount
        
        # User gets their bet back + proportional share of losing money
        user_share_ratio = bet.amount / pool.pool_amount
        share_of_losing_money = losing_pool_total * user_share_ratio
        gross_payout = bet.amount + share_of_losing_money
        
        # Deduct fees proportionally for display
        fee_amount = gross_payout * total_fee_percentage
        net_payout = gross_payout - fee_amount
        
        return net_payout
    else:
        # Edge case: no money in this pool yet
        return bet.amount


def _calculate_fixed_odds_payout(bet: models.Bet, sport_event: models.SportEvent, db: Session) -> float:
    """Calculate payout for fixed odds betting"""
    # TODO: Implement proper fixed odds storage and retrieval
    # For now, use realistic odds based on outcome type and category
    
    # Map outcome types to realistic odds
    odds_map = {
        # Standard binary outcomes
        "team_a_wins": 2.1,
        "team_b_wins": 1.9,
        "tie": 3.2,
        "draw": 3.2,
        
        # Player props - typically higher odds
        "player_scores": 2.8,
        "player_assists": 3.1,
        "player_homers": 4.5,
        
        # Over/under bets
        "over": 1.95,
        "under": 1.95,
        
        # Generic outcomes - fallback odds
        "option_a": 2.1,
        "option_b": 2.1,
    }
    
    # Get odds for this outcome, fallback to category-based default
    outcome_odds = odds_map.get(bet.predicted_outcome)
    
    if outcome_odds is None:
        # Category-based defaults
        if sport_event.category.value == "player-props":
            outcome_odds = 3.0
        elif sport_event.category.value == "banana-antics":
            outcome_odds = 2.8
        else:
            outcome_odds = 2.1
    
    return bet.amount * outcome_odds


def _calculate_spread_payout(bet: models.Bet, sport_event: models.SportEvent, db: Session) -> float:
    """Calculate payout for spread betting"""
    # TODO: Implement proper spread storage and retrieval
    # For spread betting, payouts are typically close to even money minus house edge
    
    # Standard spread betting odds (accounting for house edge)
    # Most spread bets offer around 1.90-1.95 odds
    spread_odds = 1.91
    
    # Could vary based on the specific spread or outcome
    if "favorite" in bet.predicted_outcome.lower():
        spread_odds = 1.87  # Slightly lower for favorites
    elif "underdog" in bet.predicted_outcome.lower():
        spread_odds = 1.95  # Slightly higher for underdogs
    
    return bet.amount * spread_odds


def transform_bet_to_response(bet: models.Bet, db: Session) -> schemas.BetResponse:
    """Transform a database bet to a BetResponse matching the frontend interface"""
    # Get the sport event for this bet
    sport_event = bet.sport_event
    if not sport_event:
        raise HTTPException(status_code=500, detail="Bet missing sport event")
    
    # Determine bet status based on deposit_status and outcome
    if bet.deposit_status == models.DepositStatus.PENDING:
        status = "pending"
    elif bet.deposit_status == models.DepositStatus.FAILED:
        status = "cancelled"
    elif bet.outcome == models.BetOutcome.WIN:
        status = "won"
    elif bet.outcome == models.BetOutcome.LOSS:
        status = "lost"
    elif bet.outcome == models.BetOutcome.PUSH:
        status = "cancelled"
    else:
        # Deposit confirmed but event not settled yet
        status = "pending"
    
    # Calculate potential payout based on betting system
    potential_payout = _calculate_potential_payout(bet, sport_event, db)
    
    # Format dates to ISO string
    placed_at = bet.bet_placed_at.isoformat() + 'Z'
    settled_at = None
    if bet.outcome is not None and sport_event.settled_at:
        settled_at = sport_event.settled_at.isoformat() + 'Z'
    
    # Get sport event data
    event_data = sport_event.to_dict(db)
    sport_event_response = schemas.SportEventResponse(**event_data)
    
    return schemas.BetResponse(
        id=bet.id,
        betId=f"bet-{bet.id:03d}",  # Format as bet-001, bet-002, etc.
        amount=bet.amount,
        predicted_outcome=bet.predicted_outcome,
        outcome=bet.outcome.value if bet.outcome else None,
        status=status,
        placedAt=placed_at,
        settledAt=settled_at,
        potentialPayout=potential_payout,
        bet=sport_event_response
    )
