# API Usage Guide

This document provides examples of how to use the E-Commerce API endpoints.

## Authentication

### 1. Obtain JWT Token
```http
POST /api/token/
Content-Type: application/json

{
    "username": "admin",
    "password": "test"
}
```

**Response:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Products

### List Products
```http
GET /api/products/
```

**With Filters:**
```http
GET /api/products/?category=electronics&min_price=100&max_price=500&ordering=-created_at&pagenum=1&size=10
```

### Get Product Details
```http
GET /api/products/1/
```

### Create Product (Admin Only)
```http
POST /api/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "iPhone 15 Pro",
    "description": "Latest Apple smartphone",
    "price": "999.99",
    "stock": 50,
    "category": 1,
    "is_active": true
}
```

### Update Product (Admin Only)
```http
PUT /api/products/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "iPhone 15 Pro Max",
    "description": "Updated description",
    "price": "1099.99",
    "stock": 45,
    "category": 1,
    "is_active": true
}
```

## Categories

### List Categories
```http
GET /api/categories/
```

### Get Category by Slug
```http
GET /api/categories/electronics/
```

### Create Category (Admin Only)
```http
POST /api/categories/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "Smartphones",
    "slug": "smartphones",
    "description": "Mobile phones and accessories",
    "parent": 1
}
```

## Reviews

### List Reviews for a Product
```http
GET /api/reviews/?product=1
```

### Create Review
```http
POST /api/reviews/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "product": 1,
    "rating": 5,
    "title": "Excellent product!",
    "comment": "Really satisfied with my purchase. Highly recommended!"
}
```

### Update Review
```http
PUT /api/reviews/1/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "product": 1,
    "rating": 4,
    "title": "Good product",
    "comment": "Updated review text"
}
```

## Shopping Cart

### Get User's Cart
```http
GET /api/cart/me/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "iPhone 15 Pro",
            "product_price": "999.99",
            "quantity": 2,
            "subtotal": "1999.98",
            "added_at": "2024-01-15T10:30:00Z"
        }
    ],
    "total_price": "1999.98",
    "total_items": 2,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### Add Item to Cart
```http
POST /api/cart/add_item/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "product": 1,
    "quantity": 2
}
```

### Update Cart Item
```http
PUT /api/cart/update_item/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "product": 1,
    "quantity": 3
}
```

### Remove Item from Cart
```http
DELETE /api/cart/remove_item/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "product": 1
}
```

### Clear Cart
```http
DELETE /api/cart/clear/
Authorization: Bearer <access_token>
```

## Orders

### List User's Orders
```http
GET /api/orders/
Authorization: Bearer <access_token>
```

### Get Order Details
```http
GET /api/orders/<order_id>/
Authorization: Bearer <access_token>
```

### Create Order
```http
POST /api/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "status": "Pending",
    "items": [
        {
            "product": 1,
            "quantity": 2
        },
        {
            "product": 3,
            "quantity": 1
        }
    ],
    "shipping_address_line1": "123 Main Street",
    "shipping_address_line2": "Apt 4B",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_postal_code": "10001",
    "shipping_country": "USA"
}
```

**Response:**
```json
{
    "order_id": "8f1e83a6-8f36-442e-8c1c-09dd1ae20484",
    "user": 1,
    "status": "Pending",
    "tracking_number": null,
    "items": [
        {
            "product": 1,
            "product_name": "iPhone 15 Pro",
            "product_price": "999.99",
            "quantity": 2,
            "item_subtotal": "1999.98"
        }
    ],
    "total_price": "1999.98",
    "shipping_address_line1": "123 Main Street",
    "shipping_city": "New York",
    "created_at": "2024-01-15T10:00:00Z"
}
```

### Update Order Status (Admin Only)
```http
POST /api/orders/<order_id>/update_status/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
    "status": "Shipped"
}
```

Valid status transitions:
- Pending → Confirmed, Cancelled
- Confirmed → Processing, Cancelled
- Processing → Shipped, Cancelled
- Shipped → Delivered
- Delivered → (final state)
- Cancelled → (final state)

### Filter Orders
```http
GET /api/orders/?status=Pending&created_after=2024-01-01
Authorization: Bearer <access_token>
```

## User Profile

### Get Current User Profile
```http
GET /api/profiles/me/
Authorization: Bearer <access_token>
```

### Update User Profile
```http
PUT /api/profiles/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "phone_number": "+1234567890",
    "shipping_address_line1": "456 Oak Avenue",
    "shipping_address_line2": "",
    "shipping_city": "Los Angeles",
    "shipping_state": "CA",
    "shipping_postal_code": "90001",
    "shipping_country": "USA",
    "billing_address_line1": "456 Oak Avenue",
    "billing_city": "Los Angeles",
    "billing_state": "CA",
    "billing_postal_code": "90001",
    "billing_country": "USA"
}
```

### Partial Update
```http
PATCH /api/profiles/me/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "phone_number": "+0987654321"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "quantity": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
    "detail": "Request was throttled. Expected available in 60 seconds."
}
```

## Rate Limiting

The API implements the following rate limits:
- **Anonymous users**: 2 requests per minute
- **Authenticated users**: 
  - Burst: 10 requests per minute
  - Sustained: 15 requests per hour
- **Products endpoint**: 2 requests per minute
- **Orders endpoint**: 5 requests per minute

## Pagination

List endpoints support pagination:
```http
GET /api/products/?pagenum=2&size=20
```

Response includes:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/products/?pagenum=3&size=20",
    "previous": "http://localhost:8000/api/products/?pagenum=1&size=20",
    "results": [...]
}
```

## Testing with cURL

### Get Products
```bash
curl -X GET "http://localhost:8000/api/products/"
```

### Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test"}'
```

### Create Order (with token)
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "status": "Pending",
    "items": [{"product": 1, "quantity": 2}],
    "shipping_address_line1": "123 Main St",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_postal_code": "10001",
    "shipping_country": "USA"
  }'
```

## Postman Collection

You can import the `api.http` file into your REST client or use the Swagger UI at:
```
http://localhost:8000/api/schema/swagger-ui/
```

## Best Practices

1. **Always use HTTPS in production**
2. **Store JWT tokens securely** (e.g., httpOnly cookies)
3. **Refresh tokens before they expire**
4. **Handle rate limiting gracefully**
5. **Validate input on client-side before API calls**
6. **Use appropriate HTTP methods** (GET for reading, POST for creating, etc.)
7. **Check stock availability** before creating orders
8. **Implement proper error handling**
