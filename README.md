# Zcash Transaction API

A secure, authenticated API for Zcash transactions built with FastAPI. This API provides essential Zcash wallet functionality including user authentication, transaction sending, balance checking, and address management.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication system
- **Zcash Integration**: Direct integration with Zcash node via RPC
- **Transaction Management**: Send Zcash transactions with validation
- **Wallet Operations**: Check balances, validate addresses, manage accounts
- **RESTful API**: Clean, documented API endpoints
- **Security**: Password hashing, token-based authentication

## 🛠️ Prerequisites

- **Python 3.8+**
- **Zcash Node**: Running Zcash daemon with RPC enabled
- **Git**

## ⚙️ Zcash Node Configuration

Ensure your Zcash node is configured with RPC access. Update the credentials in:
`zbet/backend/app/zcash_mod/__init__.py`

```python
ZCASH_RPC_USER = "your_rpc_username"
ZCASH_RPC_PASSWORD = "your_rpc_password"
ZCASH_RPC_URL = "http://127.0.0.1:8232/"
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone git@github.com:ReadyMouse/BananaBetting.git
cd BananaBetting
```

### 2. Launch the API

```bash
./launch_backend.sh
```

The API will be available at: **http://localhost:3000**

## 🔑 API Endpoints

### Authentication
- `POST /register/` - Register a new user with Zcash wallet
- `POST /login/` - Login and receive access token
- `GET /token_status/` - Check token validity
- `GET /users/me/` - Get current user information

### Zcash Operations
- `POST /zcash/send/` - Send Zcash to an address
- `GET /zcash/balance/` - Get current user's balance
- `GET /zcash/address/` - Get user's Zcash addresses
- `POST /zcash/validate-address/` - Validate a Zcash address
- `GET /zcash/new-account/` - Create new Zcash account

### Utility
- `GET /health/` - Health check endpoint
- `GET /` - API information


## 🗂️ Project Structure
TODO: Update for front-end
```
zcash-transaction-api/
├── zbet/backend/
│   ├── app/
│   │   ├── zcash_mod/          # Zcash integration
│   │   │   ├── zcash_wallet.py # Wallet operations
│   │   │   ├── zcash_utils.py  # Address validation
│   │   │   └── __init__.py     # RPC configuration
│   │   ├── main_transactions.py # Main API application
│   │   ├── auth.py             # Authentication
│   │   ├── models.py           # Database models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── crud.py             # Database operations
│   │   └── database.py         # Database configuration
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Virtual environment
├── launch_backend.sh           # Launch script
└── README.md                   # This file
```

## 🛡️ Security Notes

- Change the JWT secret key in production (`auth.py`)
- Use zbet/backend/.env environment variables for sensitive configuration
- Ensure Zcash node RPC is properly secured
- Use HTTPS in production environments
- Regularly update dependencies

## 📄 License

This project is a proof-of-concept for development purposes.

**⚠️ IMPORTANT DISCLAIMER ⚠️**

This project was created for the **2025 ZecHub Hackathon** (https://hackathon.zechub.wiki/) and is intended **ONLY** for educational purposes, blockchain functionality testing, and hackathon demonstration.

**🚨 DO NOT USE IN PRODUCTION 🚨**

- This application could potentially constitute an illegal betting/gambling site in many jurisdictions
- Gambling laws vary significantly by location and this software does not comply with any regulatory requirements
- This is a proof-of-concept built for fun and to explore Zcash blockchain functionality
- The developers assume no responsibility for any legal issues arising from the use of this software
- Users are solely responsible for ensuring compliance with their local laws and regulations

**Technical Note**: This API requires a running Zcash node with RPC enabled. Ensure your node is properly configured and synchronized before using the transaction features.