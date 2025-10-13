# Recipes API

This API provides CRUD operations for managing recipes, including image upload and management using S3 storage.

## Base URL

```
/api/v1/recipes/
```

## S3 Image Storage

Recipes can have associated images stored in Amazon S3. The API uses presigned URLs for secure image upload and access:

**How S3 Integration Works:**

- **Upload**: API generates presigned PUT URLs for direct S3 upload
- **Access**: API generates presigned GET URLs for temporary image access
- **Storage**: Images are stored with unique keys in the `recipes/` folder
- **Cleanup**: Images are automatically deleted when recipes are removed

**Security Benefits:**

- No S3 credentials exposed to clients
- Temporary, signed URLs prevent unauthorized access
- Direct S3 upload reduces server load

## Recipe Model

```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "image_bucket_key": "string|null",
  "image_download_url": "string|null",
  "owner": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Endpoints

### 1. List Recipes

Get a paginated list of all recipes.

**Endpoint:** `GET /api/v1/recipes/`

**Request:** No body required

**Query Parameters:**

- `page` (integer): Page number for pagination
- `page_size` (integer): Items per page

**Response (200 OK):**

```json
{
  "count": 25,
  "next": "http://api.example.com/api/v1/recipes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Spaghetti Carbonara",
      "description": "Classic Italian pasta dish",
      "image_bucket_key": "recipes/uuid123.jpg",
      "image_download_url": "https://s3-url...",
      "owner": "chef_mario",
      "created_at": "2025-01-01T12:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

---

### 2. Create Recipe

Create a new recipe. Optionally generate a presigned URL for image upload.

**Endpoint:** `POST /api/v1/recipes/`

**Request Body:**

```json
{
  "title": "string (required)",
  "description": "string (required)",
  "request_presigned_url": "boolean (optional)",
  "filename": "string (optional)"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "title": "Spaghetti Carbonara",
  "description": "Classic Italian pasta dish",
  "image_bucket_key": null,
  "image_download_url": null,
  "owner": "chef_mario",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "presigned_upload_url": "https://s3-url...",
  "image_upload_key": "recipes/uuid123.jpg"
}
```

**Notes:**

- `request_presigned_url: true` generates S3 upload URL in response
- `filename` specifies image filename (defaults to "image")
- If URL generation fails, response includes `presigned_url_error` field

---

### 3. Get Recipe Details

Retrieve a specific recipe by ID.

**Endpoint:** `GET /api/v1/recipes/{id}/`

**Request:** No body required

**Response (200 OK):**

```json
{
  "id": 1,
  "title": "Spaghetti Carbonara",
  "description": "Classic Italian pasta dish",
  "image_bucket_key": "recipes/uuid123.jpg",
  "image_download_url": "https://s3-url...",
  "owner": "chef_mario",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

---

### 4. Update Recipe

Update an existing recipe. Only the owner can update.

**Endpoint:** `PUT /api/v1/recipes/{id}/`

**Request Body:**

```json
{
  "title": "string (optional)",
  "description": "string (optional)"
}
```

**Response (200 OK):** Same as recipe detail response

**Notes:**

- Only owner can update their recipes
- Partial updates supported via PATCH method

---

### 5. Delete Recipe

Delete a recipe and its associated image. Only the owner can delete.

**Endpoint:** `DELETE /api/v1/recipes/{id}/`

**Request:** No body required

**Response (204 No Content):** Empty response

**Notes:**

- Automatically deletes associated image from S3
- Only recipe owner can delete

---

### 6. Update Recipe Image

Update or clear a recipe's image.

**Endpoint:** `PATCH /api/v1/recipes/{id}/update_image/`

**Request Body:**

```json
{
  "image_bucket_key": "string|null|empty"
}
```

**Response (200 OK):**

```json
{
  "status": "image updated"
}
```

**Notes:**

- Set `image_bucket_key` to S3 key to update image
- Set to `null`, empty string, or whitespace to clear image
- Old image is automatically deleted when replaced
- Only recipe owner can update image

---

### 7. Generate Presigned URL

Generate presigned URLs for S3 operations (GET/PUT).

**Endpoint:** `POST /api/v1/recipes/presigned_url/`

**Request Body:**

```json
{
  "method": "GET|PUT (required)",
  "key": "string (optional)",
  "filename": "string (optional)",
  "expiration": "integer (optional, default: 3600)"
}
```

**Response (200 OK):**

```json
{
  "presigned_url": "https://s3-url...",
  "key": "recipes/uuid123.jpg",
  "method": "PUT",
  "expires_in": 3600
}
```

**Notes:**

- Keys are automatically prefixed with `recipes/` if not already
- For PUT operations, `filename` generates unique S3 key
- Expiration time in seconds (default 1 hour)

## Image Upload Flow

1. **Create Recipe with Upload URL:**

   ```json
   POST /api/v1/recipes/
   {
     "title": "My Recipe",
     "description": "Description",
     "request_presigned_url": true,
     "filename": "recipe-image.jpg"
   }
   ```

2. **Upload Image to S3:**

   ```javascript
   const response = await fetch(uploadUrl, {
     method: "PUT",
     body: imageFile,
     headers: { "Content-Type": "image/jpeg" },
   });
   ```

3. **Update Recipe with Image Key:**
   ```json
   PATCH /api/v1/recipes/{id}/update_image/
   {
     "image_bucket_key": "returned_image_key"
   }
   ```

## Permissions

- **List/Get**: No authentication required (public recipes)
- **Create**: Authentication required
- **Update/Delete**: Only recipe owner
- **Image Operations**: Authentication required

## Error Responses

**Validation Error:**

```json
{
  "title": ["This field is required."]
}
```

**Permission Denied:**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found:**

```json
{
  "detail": "Not found."
}
```

**S3 URL Generation Error:**

```json
{
  "error": "Error generating presigned URL: connection failed"
}
```

**Invalid Presigned URL Request:**

```json
{
  "error": "Method must be GET or PUT"
}
```
