# API Design Template

This template provides guidelines and standardized formats for designing and documenting APIs.

## API Overview

**API Name**: [Name]
**Version**: [Version number]
**Base URL**: [Base URL]

## API Design Principles

- Follow RESTful resource naming conventions
- Use appropriate HTTP methods
- Implement consistent error handling
- Design for backward compatibility
- Include proper authentication and authorization
- Apply rate limiting and throttling
- Document all endpoints thoroughly

## Authentication

**Type**: [Bearer Token / API Key / OAuth 2.0 / etc.]

**Implementation**:
```
[Example implementation details]
```

## Endpoints

### [Resource Name]

#### List [Resources]

```
GET /api/v1/[resources]
```

**Query Parameters**:
- `page`: Page number for pagination (default: 1)
- `limit`: Number of items per page (default: 20, max: 100)
- `sort`: Field to sort by (default: id)
- `order`: Sort order (asc/desc, default: asc)
- `[filter]`: [Filter description]

**Request Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Response**:
```json
{
  "data": [
    {
      "id": "[id]",
      "[field1]": "[value1]",
      "[field2]": "[value2]"
    },
    {...}
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "pages": 5
  }
}
```

#### Get [Resource]

```
GET /api/v1/[resources]/{id}
```

**Path Parameters**:
- `id`: Unique identifier of the resource

**Request Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Response**:
```json
{
  "data": {
    "id": "[id]",
    "[field1]": "[value1]",
    "[field2]": "[value2]",
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z"
  }
}
```

#### Create [Resource]

```
POST /api/v1/[resources]
```

**Request Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Request Body**:
```json
{
  "[field1]": "[value1]",
  "[field2]": "[value2]"
}
```

**Response**:
```json
{
  "data": {
    "id": "[id]",
    "[field1]": "[value1]",
    "[field2]": "[value2]",
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z"
  }
}
```

#### Update [Resource]

```
PUT /api/v1/[resources]/{id}
```

**Path Parameters**:
- `id`: Unique identifier of the resource

**Request Headers**:
```
Authorization: Bearer [token]
Content-Type: application/json
```

**Request Body**:
```json
{
  "[field1]": "[updated value1]",
  "[field2]": "[updated value2]"
}
```

**Response**:
```json
{
  "data": {
    "id": "[id]",
    "[field1]": "[updated value1]",
    "[field2]": "[updated value2]",
    "createdAt": "2023-01-01T00:00:00Z",
    "updatedAt": "2023-01-01T00:00:00Z"
  }
}
```

#### Delete [Resource]

```
DELETE /api/v1/[resources]/{id}
```

**Path Parameters**:
- `id`: Unique identifier of the resource

**Request Headers**:
```
Authorization: Bearer [token]
```

**Response**:
```json
{
  "success": true,
  "message": "[Resource] deleted successfully"
}
```

## Error Handling

### Error Codes

- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authentication successful but insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Request conflicts with current state
- `422 Unprocessable Entity`: Validation errors
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Unexpected server error

### Error Response Format

```json
{
  "error": {
    "code": "[error_code]",
    "message": "[error_message]",
    "details": [
      {
        "field": "[field_name]",
        "message": "[field_error_message]"
      }
    ],
    "requestId": "[request_id]"
  }
}
```

## Versioning Strategy

**Version in URL Path**: `/api/v1/[resources]`

**Guidelines**:
1. Maintain backward compatibility within major versions
2. Properly document breaking changes when moving to a new major version
3. Support previous major versions for [timeframe] after a new version is released
4. Encourage clients to include version in Accept header for future compatibility

## Rate Limiting

**Default Rate Limit**: [number] requests per [timeframe]

**Response Headers**:
```
X-RateLimit-Limit: [requests_per_timeframe]
X-RateLimit-Remaining: [remaining_requests]
X-RateLimit-Reset: [reset_timestamp]
```

**Rate Limit Exceeded Response**:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "retryAfter": 60
    },
    "requestId": "[request_id]"
  }
}
```

## Pagination

**Approach**: Page-based pagination with page number and limit

**Parameters**:
- `page`: Page number (1-based indexing)
- `limit`: Number of items per page

**Response Format**:
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "pages": 5
  },
  "links": {
    "self": "/api/v1/[resources]?page=1&limit=20",
    "first": "/api/v1/[resources]?page=1&limit=20",
    "last": "/api/v1/[resources]?page=5&limit=20",
    "prev": null,
    "next": "/api/v1/[resources]?page=2&limit=20"
  }
}
```

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: [API Name]
  description: [API Description]
  version: '1.0'
servers:
  - url: 'https://api.example.com/v1'
    description: Production server
  - url: 'https://staging-api.example.com/v1'
    description: Staging server

security:
  - bearerAuth: []

paths:
  /[resources]:
    get:
      summary: List [Resources]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        '200':
          description: A list of [resources]
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/[Resource]List'
    post:
      summary: Create a new [Resource]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/[Resource]Input'
      responses:
        '201':
          description: [Resource] created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/[Resource]'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  
  schemas:
    [Resource]:
      type: object
      properties:
        id:
          type: string
        [field1]:
          type: string
        [field2]:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
          
    [Resource]Input:
      type: object
      required:
        - [field1]
      properties:
        [field1]:
          type: string
        [field2]:
          type: string
          
    [Resource]List:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/[Resource]'
        meta:
          type: object
          properties:
            total:
              type: integer
            page:
              type: integer
            limit:
              type: integer
            pages:
              type: integer
```

## Implementation Guidelines

### Security Best Practices

1. **Use HTTPS**: Ensure all API endpoints use HTTPS
2. **Token-Based Authentication**: Implement JWT or similar token mechanism
3. **Input Validation**: Validate all user input server-side
4. **Parameter Sanitization**: Sanitize all query and path parameters
5. **Sensitive Data**: Never expose sensitive data in responses
6. **Authorization**: Implement proper role-based access control

### Performance Optimization

1. **Response Size**: Limit response size and use pagination for large data sets
2. **Caching**: Implement appropriate HTTP caching headers
3. **Database Queries**: Optimize database queries for performance
4. **Compression**: Enable GZIP/Brotli compression for responses
5. **Monitoring**: Implement performance monitoring for all endpoints