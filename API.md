# OPTC Farming Bot API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently uses Bearer token authentication (to be implemented with OPTC API)

## Endpoints

### Health Check
```
GET /health
```
Returns health status of the API

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-10T12:00:00"
}
```

## Account Management

### List All Accounts
```
GET /accounts
```

**Response:**
```json
{
  "accounts": [
    {
      "id": "uuid",
      "username": "player1",
      "level": 42,
      "status": "active",
      "created_at": "2024-01-10T10:00:00"
    }
  ],
  "count": 1
}
```

### Create Account
```
POST /accounts
```

**Request Body:**
```json
{
  "username": "newplayer",
  "password": "password123",
  "email": "player@example.com"
}
```

**Response:**
```json
{
  "message": "Account created successfully",
  "account": {
    "id": "uuid",
    "username": "newplayer",
    "email": "player@example.com",
    "level": 1,
    "status": "active",
    "created_at": "2024-01-10T12:00:00"
  }
}
```

### Get Account Details
```
GET /accounts/{account_id}
```

**Response:**
```json
{
  "account": {
    "id": "uuid",
    "username": "player1",
    "email": "player@example.com",
    "level": 42,
    "berry": 10000,
    "gold": 5000,
    "experience": 50000,
    "status": "active",
    "created_at": "2024-01-10T10:00:00"
  }
}
```

### Delete Account
```
DELETE /accounts/{account_id}
```

**Response:**
```json
{
  "message": "Account deleted successfully"
}
```

## Farming Management

### Start Farming
```
POST /farming/start
```

**Request Body:**
```json
{
  "account_id": "uuid",
  "mode": "all",
  "strategy": "moderate"
}
```

**Modes:** `story`, `events`, `missions`, `grinding`, `all`

**Strategies:** `aggressive`, `moderate`, `conservative`

**Response:**
```json
{
  "message": "Farming started",
  "session": {
    "session_id": "uuid",
    "account_id": "uuid",
    "mode": "all",
    "strategy": "moderate",
    "status": "active",
    "start_time": "2024-01-10T12:00:00",
    "runs": 0
  }
}
```

### Stop Farming
```
POST /farming/stop/{session_id}
```

**Response:**
```json
{
  "message": "Farming stopped",
  "session": {
    "session_id": "uuid",
    "account_id": "uuid",
    "status": "stopped",
    "end_time": "2024-01-10T13:00:00"
  }
}
```

### Get Farming Status
```
GET /farming/status/{session_id}
```

**Response:**
```json
{
  "session": {
    "session_id": "uuid",
    "account_id": "uuid",
    "mode": "all",
    "status": "active",
    "runs": 25
  },
  "account_stats": {
    "level": 42,
    "berry": 25000,
    "gold": 10000,
    "experience": 100000
  }
}
```

### List Farming Sessions
```
GET /farming/sessions
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "account_id": "uuid",
      "mode": "all",
      "status": "active",
      "start_time": "2024-01-10T12:00:00",
      "runs": 25
    }
  ],
  "count": 1
}
```

## Statistics

### Account Statistics
```
GET /stats/accounts
```

**Response:**
```json
{
  "total_accounts": 5,
  "active_accounts": 4,
  "average_level": 35.2,
  "total_rewards_earned": 250000
}
```

### Farming Statistics
```
GET /stats/farming
```

**Response:**
```json
{
  "total_sessions": 10,
  "active_sessions": 2,
  "total_runs": 500
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

Currently not implemented. Rate limiting will be added in future versions.

## Webhooks

To be implemented in future versions for real-time farming updates.

## Examples

### Create and Start Farming
```bash
# Create account
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer1",
    "password": "secure_password",
    "email": "farmer@example.com"
  }'

# Start farming
curl -X POST http://localhost:5000/api/farming/start \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "returned-id-from-create",
    "mode": "all",
    "strategy": "moderate"
  }'
```
