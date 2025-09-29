# BananaBetting Functionality Testing Plan

## Overview
This document tracks comprehensive end-to-end testing of the BananaBetting application, with special focus on wallet functionality, betting flow, and transaction tracking.

## Test Environment Setup
- **Backend**: http://localhost:8000 (FastAPI)
- **Frontend**: http://localhost:3000 (Next.js)
- **Mobile Testing**: External phone wallet app
- **Database**: SQLite with seed data

---

## [DONE] Test Flow 1: User Creation & Wallet Generation

### Objective
Verify that new users can be created with properly generated wallet addresses and recovery keys.

### Test Steps
1. **Create New User**
   - Navigate to registration/signup page
   - Enter test credentials:
     - Email: `testuser@example.com`
     - Username: `testuser123`
     - Password: `SecurePass123!`
   - Submit registration

2. **Verify Wallet Generation**
   - Check that user receives:
     - Zcash shielded address (starting with `zs...`)
     - Zcash transparent address (starting with `t...`)
     - Recovery key/seed phrase
   - Verify addresses are unique and properly formatted

### Expected Results
- User successfully created in database
- Wallet addresses generated and stored
- Recovery information provided to user

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| User Creation | N/A | Generated addresses recorded | 0.00 ZEC | 🔄 Pending  | Initial wallet setup |

---

## [DONE] Test Flow 2: Profile Page & Balance Display

### Objective
Verify that user profile displays wallet addresses and current balance.

### Test Steps
1. **Navigate to Profile Page**
   - Login with test user credentials
   - Navigate to `/profile` page

2. **Verify Address Display**
   - Confirm shielded address is shown
   - Confirm transparent address is shown
   - Verify initial balance shows as 0.00 ZEC

3. **Test Refresh Functionality**
   - Verify refresh button is present and functional
   - Initial refresh should confirm 0.00 ZEC balance

### Expected Results
- Profile page displays both wallet addresses
- Balance shows 0.00 ZEC initially
- Refresh button works without errors

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| Profile Load | N/A | Display addresses | 0.00 ZEC | 🔄 Pending  | Initial profile view |

---

## [DONE] Test Flow 3: External Funding & Balance Update

### Objective
Test external funding of user wallet and balance refresh functionality.

### Test Steps
1. **External Wallet Funding**
   - Use mobile Zcash wallet app
   - Send test amount to user's shielded address
   - **Target Amount**: 0.00001 ZEC
   - Record transaction hash from mobile wallet

2. **Balance Refresh Testing**
   - Return to profile page
   - Click refresh button to check for new balance
   - Repeat refresh until balance updates
   - Verify correct amount is displayed

### Expected Results
- External transaction successfully sent
- Balance refresh detects incoming funds
- Correct amount displayed in profile

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| External Deposit | `[TO_BE_RECORDED]` | User shielded address | 0.00001 ZEC | 🔄 Pending | Mobile wallet → User |
| Balance Update | N/A | Profile refresh | ~0.00001 ZEC | 🔄 Pending | Confirmed balance |

---

## Test Flow 4: Bet Placement & Account Validation

### Objective
Verify that users can place bets and system validates sufficient account balance.

### Test Steps
1. **Navigate to Betting**
   - Go to active betting events page
   - Select a test event for betting

2. **Attempt Bet Placement**
   - Select betting option
   - Enter bet amount: `0.000001 ZEC`
   - Submit bet

3. **Verify Balance Check**
   - System should validate user has sufficient funds (0.00001  ZEC available)
   - Bet should be accepted and processed
   - User balance should be reduced by bet amount

### Expected Results
- Bet successfully placed
- Account balance validation works correctly
- User balance decreases to 0.000001 ZEC after bet

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| Bet Placement | `[TO_BE_RECORDED]` | User → Pool | 0.000001 ZEC | 🔄 Pending | Bet transaction |
| Balance Deduction | N/A | User account | -0.000001 ZEC | 🔄 Pending | Post-bet balance: ? ZEC |

---

## Test Flow 5: Pool Funding & Transaction Tracking

### Objective
Verify that bet funds are properly transferred to the betting pool with transaction tracking.

### Test Steps
1. **Monitor Pool Transfer**
   - After bet placement, verify funds move to pool account
   - Record transaction hash for bet → pool transfer
   - Verify pool balance increases by bet amount

2. **Transaction Verification**
   - Check blockchain explorer for transaction confirmation
   - Verify transaction details match expected amounts
   - Confirm transaction appears in system logs

### Expected Results
- Funds successfully transferred to pool account
- Transaction hash recorded and trackable
- Pool balance accurately reflects received funds

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| Pool Transfer | `[TO_BE_RECORDED]` | User → Pool Account | 0.000001 ZEC | 🔄 Pending | Bet funds to pool |

---

## Test Flow 6: Event Settlement & Payout Distribution

### Objective
Test event settlement and payout distribution using sendmany transaction.

### Test Setup for Simplified Testing
To avoid creating multiple small accounts that need to be drained later, we'll use different shielded addresses from the same test wallet for:
- **Event Creator**: `zs1test_creator_address...`
- **Validators**: `zs1test_validator1_address...`, `zs1test_validator2_address...`
- **Platform Fee**: `zs1test_platform_address...`
- **Charity Donation**: `taddress`

### Test Steps
1. **Event Settlement**
   - Navigate to event settlement page
   - Select the test event with placed bets
   - Set event outcome (e.g., "Team A Wins")
   - Submit settlement

2. **Payout Processing**
   - Click "Process Payouts" button
   - System should calculate distributions:
     - Winners: Proportional share of pool
     - Event Creator: Fee percentage
     - Validators: Validation rewards
     - Platform: Service fee

3. **Sendmany Execution**
   - System executes single sendmany transaction
   - Multiple outputs to different addresses
   - Record the master transaction hash

### Expected Results
- Event successfully settled
- Payout calculations correct
- Single sendmany transaction processes all distributions
- All recipients receive correct amounts

### Transaction Records
| Action | Transaction ID | Address | Amount | Status | Notes |
|--------|---------------|---------|---------|---------|-------|
| Settlement Payout | `[TO_BE_RECORDED]` | Pool → Multiple Recipients | Various | 🔄 Pending | Sendmany distribution |
| Winner Payout | Same as above | Pool → Winner | ~4.25 ZEC | 🔄 Pending | Winner's share |
| Creator Fee | Same as above | Pool → Creator | ~0.25 ZEC | 🔄 Pending | Event creator fee |
| Validator Rewards | Same as above | Pool → Validators | ~0.30 ZEC | 🔄 Pending | Validation incentives |
| Platform Fee | Same as above | Pool → Platform | ~0.20 ZEC | 🔄 Pending | Service fee |

---

## Key Transaction Addresses for Testing

### Test User Wallet
- **Shielded Address**: `[TO_BE_GENERATED]`
- **Transparent Address**: `[TO_BE_GENERATED]`
- **Recovery Key**: `[TO_BE_SECURED]`

### System Pool Account
- **Pool Address**: `[TO_BE_CONFIGURED]`
- **Purpose**: Holds all active bet funds

### Test Recipient Addresses (Same Wallet, Different Addresses)
- **Event Creator**: `[TO_BE_CONFIGURED]`
- **Validator 1**: `[TO_BE_CONFIGURED]` 
- **Validator 2**: `[TO_BE_CONFIGURED]`
- **Platform Fee**: `[TO_BE_CONFIGURED]`

---

## Success Criteria

### ✅ User Management
- [ ] New user creation with wallet generation
- [ ] Wallet addresses properly formatted and unique
- [ ] Recovery keys provided and secure

### ✅ Wallet Functionality  
- [ ] Profile page displays addresses and balance
- [ ] External funding works correctly
- [ ] Balance refresh detects new funds accurately
- [ ] Balance validation prevents insufficient fund bets

### ✅ Betting Flow
- [ ] Bet placement processes correctly
- [ ] Funds transfer to pool with transaction tracking
- [ ] Account balances update in real-time

### ✅ Settlement & Payouts
- [ ] Event settlement calculates payouts correctly
- [ ] Sendmany transaction distributes funds properly
- [ ] All transaction hashes recorded for audit trail

---

## Notes & Observations

### Performance Notes
- Record transaction confirmation times
- Note any UI/UX issues during testing
- Document any error conditions encountered

### Security Considerations
- Verify all private keys are properly secured
- Confirm transaction signatures are valid
- Test edge cases for insufficient funds

### Future Enhancements
- Consider automated transaction monitoring
- Implement real-time balance updates via WebSocket
- Add transaction history page for users

---

## Test Execution Log

| Test Date | Tester | Flow Completed | Issues Found | Resolution |
|-----------|---------|---------------|---------------|------------|
| [Date] | [Name] | [Flow #] | [Description] | [Action Taken] |

---

*Last Updated: [Date]*
*Document Version: 1.0*
