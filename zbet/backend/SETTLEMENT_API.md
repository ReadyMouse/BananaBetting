# Settlement and Payout API Documentation

This document describes the settlement and payout system for the Banana Betting platform.

## Overview

The settlement system handles the process of:
1. Determining the winning outcome of a betting event
2. Calculating payouts for all winning bets
3. Deducting appropriate fees
4. Sending batch Zcash transactions to distribute winnings
5. Recording all payout information in the database

## API Endpoints

### Settle Event
```
POST /api/events/{event_id}/settle
```

Settles a betting event with the final outcome and processes all payouts.

**Request Body:**
```json
{
  "winning_outcome": "team_a_wins"
}
```

**Response:**
```json
{
  "event_id": 1,
  "winning_outcome": "team_a_wins",
  "total_payouts": 3,
  "total_payout_amount": 15.75,
  "transaction_id": "opid-12345-abcdef",
  "settled_at": "2025-09-19T10:30:00Z",
  "payout_records": [
    {
      "user_id": 1,
      "bet_id": 5,
      "payout_amount": 8.50,
      "house_fee_deducted": 0.45,
      "creator_fee_deducted": 0.18,
      "user_address": "ztestsapling1user1address..."
    }
  ]
}
```

### Get Settlement Information
```
GET /api/events/{event_id}/settlement
```

Retrieves settlement information for an event (returns null if not settled).

**Response:** Same as settle endpoint, or `null` if event is not settled.

## Payout Calculation

### Pari-Mutuel System

For pari-mutuel betting, payouts are calculated as follows:

1. **Total Pool**: Sum of all bets across all outcomes
2. **Fee Deduction**: House fee + Creator fee (configured per event)
3. **Net Prize Pool**: Total Pool - Fees
4. **Individual Payout**: (User's Bet / Winning Pool) × Net Prize Pool

**Example:**
- Total bets: $100 (Pool A: $30, Pool B: $70)
- Fees: 7% = $7
- Net prize: $93
- If Pool A wins: Each $1 bet on A gets ($1/$30) × $93 = $3.10

### Fixed Odds System

For fixed odds betting:
- **Payout**: Bet Amount × Odds
- **Fees**: Applied after payout calculation (2% house, 1% creator)

### Spread Betting

Similar to fixed odds with spread-adjusted odds.

## Database Schema

### New Tables

**Payout Table:**
- `id`: Primary key
- `user_id`: Foreign key to users
- `bet_id`: Foreign key to bets  
- `sport_event_id`: Foreign key to sport_events
- `payout_amount`: Net payout amount in ZEC
- `house_fee_deducted`: House fee amount
- `creator_fee_deducted`: Creator fee amount
- `zcash_transaction_id`: Batch transaction hash
- `payout_processed_at`: Timestamp
- `is_processed`: Boolean status

### Updated Tables

**SportEvent:**
- `settled_at`: Timestamp when event was settled

**Bet:**
- `outcome`: WIN/LOSS/PUSH (set during settlement)
- `payout_amount`: Final payout amount
- `house_fee_deducted`: Fee amount deducted
- `creator_fee_deducted`: Creator fee deducted

**PariMutuelEvent:**
- `winning_outcome`: Name of winning outcome

**PariMutuelPool:**
- `is_winning_pool`: Boolean marking winning pool

## Zcash Integration

The system uses the `z_sendmany` RPC call to send batch payouts:

```python
# Recipients are consolidated by address
recipients = [
    {"address": "ztestsapling1user1...", "amount": 5.25},
    {"address": "ztestsapling1user2...", "amount": 3.80}
]

operation_id = z_sendmany(
    from_address="ztestsapling1house...",
    recipients=recipients,
    minconf=1
)
```

## Error Handling

The system validates:
- Event exists and is in OPEN status
- Winning outcome is valid for the event
- No double settlement
- Sufficient confirmed bets exist
- Valid Zcash addresses

Common error responses:
- `404`: Event not found
- `400`: Event already settled
- `400`: Invalid winning outcome
- `500`: Zcash transaction failed

## Testing

Run the settlement tests:

```bash
# Unit tests
python -m pytest tests/test_settlement.py

# Integration demo
python tests/test_settlement_integration.py
```

## Security Considerations

1. **Authorization**: Only event creators or admins should settle events
2. **House Address**: Should be configurable via environment variables
3. **Transaction Fees**: Monitor Zcash network fees for large batches
4. **Double Settlement**: System prevents duplicate settlements
5. **Audit Trail**: All payouts are permanently recorded

## Configuration

Environment variables needed:
```
HOUSE_ZCASH_ADDRESS=ztestsapling1house...
ZCASH_RPC_URL=http://localhost:8232
ZCASH_RPC_USER=username
ZCASH_RPC_PASSWORD=password
```

## Future Enhancements

1. **Automated Settlement**: Oracle integration for automatic settlement
2. **Partial Payouts**: Support for events with multiple settlement phases
3. **Fee Optimization**: Dynamic fee calculation based on network conditions
4. **Payout Scheduling**: Delayed payout execution
5. **Cross-Event Settlements**: Batch multiple event settlements
