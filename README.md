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
git clone <repository-url>
cd zSiren
```

### 2. Launch the API

```bash
./launch_backend.sh
```

The API will be available at: **http://localhost:3000**

## 📚 API Documentation

Once running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 💡 Usage Examples

### Register a New User
```bash
curl -X POST "http://localhost:8000/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "username",
       "password": "secure_password"
     }'
```

### Login
```bash
curl -X POST "http://localhost:8000/login/" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=username&password=secure_password"
```

### Send Zcash Transaction
```bash
curl -X POST "http://localhost:8000/zcash/send/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "address": "zcash_destination_address",
       "amount": 0.01
     }'
```

### Check Balance
```bash
curl -X GET "http://localhost:8000/zcash/balance/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🗂️ Project Structure

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

## 🔧 Development

### Manual Setup

```bash
cd zbet/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main_transactions:app --reload --host 127.0.0.1 --port 8000
```

### Environment Variables

You can set these environment variables to customize the setup:
- `ZCASH_RPC_URL`: Zcash node RPC URL
- `ZCASH_RPC_USER`: RPC username
- `ZCASH_RPC_PASSWORD`: RPC password

## 🛡️ Security Notes

- Change the JWT secret key in production (`auth.py`)
- Use environment variables for sensitive configuration
- Ensure Zcash node RPC is properly secured
- Use HTTPS in production environments
- Regularly update dependencies

## 📄 License

This project is a proof-of-concept for development purposes.

---

**Note**: This API requires a running Zcash node with RPC enabled. Ensure your node is properly configured and synchronized before using the transaction features.