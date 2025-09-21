# Settlement System Implementation

## Overview

The Banana Betting platform now has a complete settlement system that handles the final resolution of betting events, calculates payouts, and distributes winnings to users. This document outlines the implemented features and how to use them.

## Key Features Implemented

### ✅ 1. Manual Settlement
- **Endpoint**: `POST /api/events/{event_id}/settle`
- **Authorization**: Only event creators can settle their events
- **Function**: Immediately settle an event with a specified winning outcome
- **Payouts**: Calculates and distributes payouts to winners, house, creator, and validators

### ✅ 2. Consensus-Based Settlement  
- **Endpoint**: `POST /api/events/{event_id}/settle-with-consensus`
- **Authorization**: Only event creators can trigger consensus settlement
- **Function**: Uses validator consensus (60% agreement, min 3 validators) to determine winner
- **Automatic**: Can be triggered automatically when consensus is reached

### ✅ 3. Automatic Deadline Processing
- **Endpoint**: `POST /api/admin/process-expired-events`
- **Function**: Processes events past their settlement deadline
- **Logic**:
  - Try consensus settlement first
  - If no consensus, cancel event and refund all bets
- **Automation**: Can be called by cron job script

### ✅ 4. Payout Distribution
- **Winners**: Receive calculated payouts based on betting system type
- **House**: Receives configured percentage of losing pool
- **Creator**: Receives configured percentage of losing pool  
- **Validators**: Correct validators share validator fee pool
- **Zcash**: All payouts sent via batch `z_sendmany` transactions

### ✅ 5. Frontend Settlement Interface
- **Page**: `/settle-bets`
- **Features**:
  - Shows events eligible for settlement (past end time, before deadline)
  - Manual settlement with outcome selection
  - Automatic consensus settlement option
  - Real-time feedback with transaction details

### ✅ 6. Monitoring and Administration
- **Endpoint**: `GET /api/admin/expired-events`
- **Function**: Monitor events past deadline that need processing
- **Details**: Shows validation counts, consensus status, hours past deadline

## Settlement Flow

### For Pari-Mutuel Events:

1. **Event Creation**: Creator sets house fee %, creator fee %, validator fee %
2. **Betting Phase**: Users place bets, pools accumulate funds
3. **Event Occurs**: Real-world event happens
4. **Validation Phase**: Community validates the outcome
5. **Settlement**:
   - Manual: Creator chooses winning outcome
   - Consensus: System uses validator consensus
   - Automatic: Cron job processes expired events
6. **Payout Calculation**:
   ```
   Total Pool = Sum of all bets
   Losing Pool = Total Pool - Winning Pool
   Fees = Losing Pool × (house% + creator% + validator%)
   Net Prize = Losing Pool - Fees
   User Payout = User Bet + (User Bet / Winning Pool) × Net Prize
   ```
7. **Distribution**: Batch Zcash transaction sends all payouts

### Special Case: PUSH/TIE Outcomes

When an event is settled as "push" or "tie":
- **All bets are refunded**: Every bettor gets their original bet amount back
- **No fees are collected**: House, creator, and validator fees are 0
- **No winners or losers**: All bet outcomes are marked as PUSH
- **Full refund transaction**: Single batch transaction refunds all bettors

## API Endpoints

### Settlement Endpoints
```
POST /api/events/{id}/settle
POST /api/events/{id}/settle-with-consensus
GET  /api/events/{id}/settlement
```

### Admin Endpoints  
```
GET  /api/admin/expired-events
POST /api/admin/process-expired-events
```

## Automation Setup

### Cron Job Configuration
Add to crontab for hourly processing:
```bash
0 * * * * /path/to/venv/bin/python /path/to/scripts/process_expired_events.py
```

### Environment Variables Required
```bash
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
API_BASE_URL=http://localhost:8000
DATABASE_URL=your_database_url
HOUSE_ZCASH_ADDRESS=your_house_address
ZCASH_RPC_URL=http://localhost:8232
ZCASH_RPC_USER=your_rpc_user  
ZCASH_RPC_PASSWORD=your_rpc_password
```

## Database Schema Changes

### Enhanced Enum Values
- `BetOutcome.PUSH` - For ties, cancelled events, or any situation requiring automatic refunds

### Existing Tables Enhanced
- `sport_events.settled_at` - Settlement timestamp
- `bets.outcome` - WIN/LOSS/PUSH (PUSH triggers automatic refund)
- `bets.payout_amount` - Final payout amount
- `payouts` - All payout records with transaction IDs

## Error Handling

### Authorization Errors
- **403**: Only event creators can settle events
- **404**: Event not found

### Validation Errors  
- **400**: Event already settled
- **400**: Insufficient validations for consensus
- **400**: Invalid winning outcome

### Transaction Errors
- **500**: Zcash transaction failed
- **500**: Database operation failed

## Testing

### Manual Testing
1. Create an event with pari-mutuel betting
2. Place some bets on different outcomes
3. Validate the event outcome
4. Settle the event (manual or consensus)
5. Verify payouts in Zcash wallet

### Automated Testing
```bash
cd zbet/backend
python -m pytest tests/test_settlement.py -v
python tests/test_settlement_integration.py
```

## Future Enhancements

### Planned Features
1. **Oracle Integration**: Automatic event outcome detection
2. **Partial Settlements**: Multi-phase settlement for complex events
3. **Advanced Scheduling**: Time-based settlement triggers
4. **Enhanced Monitoring**: Web dashboard for settlement status
5. **Fee Optimization**: Dynamic fee calculation
6. **Cross-Event Batching**: Batch settlements across multiple events

### Security Improvements
1. **Admin Roles**: Proper admin user system
2. **Settlement Locks**: Prevent double settlement
3. **Audit Logging**: Complete settlement audit trail
4. **Rate Limiting**: Prevent API abuse

## Support

For issues or questions about the settlement system:
1. Check the API documentation in `SETTLEMENT_API.md`
2. Review test cases in `tests/test_settlement*.py`
3. Monitor logs during settlement processing
4. Use the admin endpoints to check event status

The settlement system is now fully functional and ready for production use with proper monitoring and automation setup.
