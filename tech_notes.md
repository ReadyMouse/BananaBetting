# Technical Notes: Zcash Integration for Sports Betting System

## Overview
This document summarizes the technical discussion and design decisions for integrating Zcash into the BananaBetting sports betting system during the hackathon development.

## The Problem: Understanding Zcash Node Architecture

### Initial Challenge
The project initially attempted to use public Zcash nodes (like `zec.rocks:443`) for wallet functionality including transactions, `sendmany`, and account creation. However, these nodes are **light wallet servers** (lightwalletd/zaino), not full JSON-RPC nodes with wallet capabilities.

### Key Technical Distinction

#### Light Wallet Servers vs Full Nodes
There are two types of Zcash nodes:

1. **Light Wallet Servers** (lightwalletd, zaino)
   - gRPC endpoints for read-only operations
   - Used by mobile wallets, zingo-cli, zcash-devtool
   - Don't require syncing the full 300GB blockchain
   - **Cannot perform wallet operations** like sending transactions
   - Public nodes like zec.rocks exclusively host these

2. **Full Nodes** (zcashd, zebra)
   - JSON-RPC API similar to bitcoind
   - Required for wallet functionality (sending/receiving Zcash)
   - Must sync the full blockchain
   - Currently only zcashd supports wallet functionality
   - Used by exchanges and "serious users"

### Architecture Behind Public Light Wallet Servers
- Light wallet servers are powered by full nodes behind the scenes
- The full nodes expose JSON-RPC on private networks to allow lightwalletd to sync
- **These JSON-RPC endpoints are NOT exposed to the internet**
- Users never directly access the full node's wallet functionality

## Design Decision: Wallet Implementation Options

### Option 1: Self-Hosted zcashd (Recommended)
**Pros:**
- Production-grade, battle-tested
- Full JSON-RPC wallet functionality
- Bitcoin API compatibility (familiar to Bitcoin developers)
- Complete control over wallet operations

**Cons:**
- Requires syncing 300GB blockchain
- Infrastructure overhead
- Setup complexity with zcash-wallettool

**Implementation Requirements:**
- Fully-synced zcashd node
- JSON-RPC exposed to allowlisted IPs
- Password protection for RPC
- Wallet creation using zcash-wallettool
- Seed phrase backup

### Option 2: Light Wallet Integration (zingo-cli/zcash-devtool)
**Pros:**
- No blockchain sync required
- Faster setup for hackathon
- Lighter infrastructure

**Cons:**
- "Toys" according to community experts
- Not production-grade
- No direct API exposure (CLI tools only)
- Would require source modification for API integration
- Higher risk of headaches

## Final Decision Rationale

### Chosen Approach: Self-Hosted zcashd
Despite the infrastructure complexity, we chose to implement a self-hosted zcashd node because:

1. **Reliability**: Production-grade solution used by exchanges
2. **API Compatibility**: Bitcoin-like JSON-RPC familiar to developers
3. **Future-Proofing**: Scalable solution if the project moves beyond hackathon
4. **Complete Functionality**: Access to all wallet operations needed for sports betting

### Context Considerations
- **Hackathon Environment**: While light wallet solutions might suffice for a hackathon, the sports betting use case requires reliable transaction handling
- **Production Potential**: While it's just a hackathon project building on solid foundations is preferred
- **Community Direction**: zcashd is being deprecated by end of year in favor of Z3 stack (zebra+zaino+zallet), but remains the current production standard

## Future Migration Path: Z3 Stack
The Zcash community is developing a new stack to replace zcashd:
- **Zebra**: Full node (replaces zcashd)
- **Zaino**: Indexing layer for efficient querying
- **Zallet**: Wallet functionality with JSON-RPC (replaces zcashd wallet)

This will maintain Bitcoin API compatibility while modernizing the infrastructure.

## Transaction Broadcasting Architecture
Important note: In the light wallet model, the server never has access to user private keys:
1. User's wallet signs transactions with their private keys
2. Signed transactions are submitted to light wallet servers
3. Servers relay transactions to the P2P network
4. This design enables mobile wallet functionality without compromising security

## Implementation Notes
- The chosen zcashd approach requires careful security configuration
- JSON-RPC must be properly secured with authentication
- Seed phrase backup is critical for wallet recovery
- Consider the 300GB sync time in deployment planning

---
*Last Updated: September 19, 2025*
*Based on community discussion regarding Zcash node architecture and wallet functionality requirements*
