# Tasti API Documentation

Welcome to the Tasti API documentation. This API provides endpoints for managing recipes and user authentication.

## Overview

The Tasti API is built with Django REST Framework and provides the following main features:

- **User Authentication**: Registration, login, logout, and token management
- **Recipe Management**: CRUD operations for recipes with image support
- **Image Storage**: S3-based image storage with presigned URLs

## API Structure

All API endpoints are prefixed with `/api/v1/`.

### Core Endpoints

- **Health Check**: `GET /api/v1/health/` - API status check

### Authentication

The API uses JWT (JSON Web Tokens) for authentication. Tokens are provided in login responses and should be included in the `Authorization` header as `Bearer <token>`.

### S3 Image Storage

Images are stored in Amazon S3 and accessed via presigned URLs. This provides secure, temporary access to images without exposing S3 credentials.

**How it works:**

- When uploading images, the API generates a presigned PUT URL
- Clients upload directly to S3 using this URL
- For viewing images, the API generates presigned GET URLs
- Images are automatically cleaned up when recipes are deleted

## Apps Documentation

- [Authentication API](./accounts.md) - User registration, login, and token management
- [Recipes API](./recipes.md) - Recipe CRUD operations with image support

## Health Check

**Endpoint:** `GET /api/v1/health/`

**Response:**

```json
{
  "status": "healthy",
  "message": "Tasti API is running!",
  "version": "1.0.0"
}
```

Use this endpoint to verify API availability and health.

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include a JSON object with an `error` field describing the issue.

## Rate Limiting

Currently, there are no explicit rate limits implemented, but this may be added in future versions for security.
