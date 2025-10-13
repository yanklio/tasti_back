# Authentication API

This API handles user authentication, registration, and token management for the Tasti application.

## Base URL

```
/api/v1/auth/
```

## Endpoints

### 1. User Registration

Register a new user account.

**Endpoint:** `POST /api/v1/auth/register/`

**Request Body:**

```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required)",
  "first_name": "string (optional)",
  "last_name": "string (optional)"
}
```

**Response (201 Created):**

```json
{
  "message": "User registered successfully",
  "access": "jwt_access_token_string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "2025-01-01T00:00:00Z"
  }
}
```

**Notes:**

- Password must be at least 8 characters long
- Username must be unique
- Email must be unique and valid format
- JWT access token is returned immediately
- Refresh token is set as httpOnly cookie

---

### 2. User Login

Authenticate an existing user.

**Endpoint:** `POST /api/v1/auth/login/`

**Request Body:**

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (201 Created):**

```json
{
  "message": "User logged in successfully",
  "access": "jwt_access_token_string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "2025-01-01T00:00:00Z"
  }
}
```

**Notes:**

- Use either username or email for authentication
- JWT access token is returned
- Refresh token is set as httpOnly cookie for security

---

### 3. User Logout

Log out the current user by clearing the refresh token cookie.

**Endpoint:** `POST /api/v1/auth/logout/`

**Request Body:** None (authentication required)

**Response (200 OK):**

```json
{
  "message": "Logout successful"
}
```

**Notes:**

- Requires authentication (Bearer token in Authorization header)
- Clears the httpOnly refresh token cookie
- Access token remains valid until expiry

---

### 4. Token Refresh

Refresh an expired access token using the refresh token from cookies.

**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Request Body:** None

**Response (200 OK):**

```json
{
  "access": "new_jwt_access_token_string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "date_joined": "2025-01-01T00:00:00Z"
  }
}
```

**Notes:**

- Reads refresh token from httpOnly cookie
- Returns new access token
- Optionally rotates refresh token if configured
- No authentication header required (uses cookie)

## Authentication Flow

1. **Registration/Login**: Get access token and refresh token (in cookie)
2. **API Requests**: Include `Authorization: Bearer <access_token>` header
3. **Token Expiry**: When access token expires, call refresh endpoint
4. **Logout**: Call logout endpoint to clear refresh token

## Security Notes

- Refresh tokens are stored in httpOnly cookies to prevent XSS attacks
- Access tokens should be stored securely (localStorage is not recommended)
- Tokens expire and need to be refreshed periodically
- Passwords are hashed using Django's secure hashing

## Error Responses

**Invalid Credentials (Login):**

```json
{
  "non_field_errors": ["Invalid credentials."]
}
```

**Missing Fields (Registration/Login):**

```json
{
  "username": ["This field is required."],
  "password": ["This field is required."]
}
```

**Duplicate Username/Email (Registration):**

```json
{
  "username": ["A user with that username already exists."]
}
```

**Invalid Refresh Token:**

```json
{
  "error": "Invalid or expired refresh token"
}
```
