# Auth Service

A FastAPI-based authentication and user management microservice.

## Features

- User registration and authentication
- JWT token-based authentication with refresh tokens
- Password hashing using bcrypt
- Rate limiting middleware
- Email utilities for verification and password reset
- RESTful API endpoints for user management
- PostgreSQL database integration

## Project Structure

```
auth-service/
├── main.py              # Main application entry point
├── config.py            # Service configuration
├── models.py            # Pydantic models & database schemas
├── database.py          # Database connection
├── auth.py              # Authentication core logic
├── dependencies.py      # FastAPI dependencies
├── routers/
│   ├── __init__.py
│   ├── auth_router.py   # Authentication endpoints
│   └── users_router.py  # User management endpoints
├── utils/
│   ├── __init__.py
│   ├── password.py      # Password hashing utilities
│   ├── jwt_handler.py   # JWT token management
│   └── email.py         # Email utilities (optional)
├── middleware/
│   ├── __init__.py
│   └── rate_limit.py    # Rate limiting middleware
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment file and configure:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Set up PostgreSQL database and update DATABASE_URL in .env

4. Run the service:
```bash
python main.py
```

The service will be available at `http://localhost:8001`

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### User Management
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update current user
- `GET /users/{user_id}` - Get user by ID
- `DELETE /users/me` - Deactivate account

### Health Check
- `GET /` - Service status
- `GET /health` - Health check

## Configuration

All configuration is handled through environment variables. See `.env.example` for available options.

## Security Features

- Password hashing with bcrypt
- JWT tokens with configurable expiration
- Rate limiting middleware
- CORS protection
- Input validation with Pydantic

## Development

To run in development mode with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```