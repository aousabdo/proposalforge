# ProposalForge API Request/Response Formats and Status Codes

## Introduction

This document outlines the standardized request and response formats for the ProposalForge API, as well as the HTTP status codes used across the API. Consistency in these formats is crucial for providing a predictable and developer-friendly API experience.

## Request Formats

### Common HTTP Methods

The ProposalForge API uses standard HTTP methods:

| Method | Usage |
|--------|-------|
| GET | Retrieve resources |
| POST | Create new resources |
| PATCH | Partially update resources |
| DELETE | Remove resources |
| OPTIONS | Get supported operations on resources |

### Content Types

All requests with bodies must use `application/json` as the content type:

```
Content-Type: application/json
```

### Request Headers

| Header | Description | Required | Example |
|--------|-------------|----------|---------|
| `Authorization` | Bearer token for authentication | Yes | `Bearer eyJhbGciOiJIUzI1NiIsInR5...` |
| `Content-Type` | Media type of the body | Yes (for POST/PATCH) | `application/json` |
| `Accept` | Media types acceptable for response | No | `application/json` |
| `Accept-Language` | Preferred language for responses | No | `en-US` |
| `X-Request-ID` | Client-generated request identifier | No | `550e8400-e29b-41d4-a716-446655440000` |

### Query Parameters

#### Pagination

```
GET /workspaces?limit=10&offset=20
```

| Parameter | Description | Default | Max |
|-----------|-------------|---------|-----|
| `limit` | Number of items to return | 10 | 100 |
| `offset` | Number of items to skip | 0 | N/A |

#### Filtering

```
GET /documents?type=rfp&category=government
```

#### Sorting

```
GET /proposals?sort=createdAt:desc
```

#### Search

```
GET /documents?search=security+requirements
```

### Request Body Structure

For POST and PATCH requests, the body structure follows these guidelines:

```json
{
  "property1": "value1",
  "property2": "value2",
  "nestedObject": {
    "nestedProperty": "nestedValue"
  }
}
```

- Property names use camelCase
- Boolean values use `true`/`false` (not strings)
- Dates use ISO 8601 format: `YYYY-MM-DDThh:mm:ss.sssZ`
- Null values are explicitly set to `null` (not empty strings)

## Response Formats

### Success Response Structure

All successful responses (2xx) follow this structure:

```json
{
  "data": {
    // Response data here
  },
  "meta": {
    // Metadata about the response (optional)
  },
  "links": {
    // Links related to the resource (optional)
  }
}
```

#### Single Resource Example

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "RFP Response Template",
    "description": "Standard template for government RFPs",
    "createdAt": "2023-01-15T14:30:15.123Z",
    "updatedAt": "2023-02-20T09:12:33.456Z"
  }
}
```

#### Collection Resource Example

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Government RFP Workspace",
      "description": "Workspace for DOD proposal",
      "createdAt": "2023-01-15T14:30:15.123Z"
    },
    {
      "id": "6d619cbc-7357-4401-9d1c-845661765101",
      "name": "Healthcare Proposal Workspace",
      "description": "Workspace for hospital system proposal",
      "createdAt": "2023-02-10T11:22:33.123Z"
    }
  ],
  "meta": {
    "totalCount": 157,
    "limit": 10,
    "offset": 0
  },
  "links": {
    "self": "/v1/workspaces?limit=10&offset=0",
    "next": "/v1/workspaces?limit=10&offset=10",
    "prev": null
  }
}
```

### Error Response Structure

All error responses (4xx, 5xx) follow this structure:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

#### Validation Error Example

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request was invalid.",
    "details": {
      "fields": {
        "name": ["Name is required"],
        "estimatedValue": ["Must be a positive number"]
      }
    }
  }
}
```

#### Not Found Error Example

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "The requested workspace could not be found.",
    "details": {
      "resourceType": "workspace",
      "resourceId": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

### Pagination Metadata

For endpoints returning collections, pagination metadata is included:

```json
"meta": {
  "totalCount": 157,
  "limit": 10,
  "offset": 0,
  "hasMore": true
}
```

### HATEOAS Links

Where appropriate, responses include hypermedia links:

```json
"links": {
  "self": "/v1/workspaces/550e8400-e29b-41d4-a716-446655440000",
  "documents": "/v1/workspaces/550e8400-e29b-41d4-a716-446655440000/documents",
  "proposals": "/v1/workspaces/550e8400-e29b-41d4-a716-446655440000/proposals"
}
```

## HTTP Status Codes

The ProposalForge API uses standard HTTP status codes to indicate the success or failure of requests.

### Success Codes

| Code | Name | Description | Example |
|------|------|-------------|---------|
| 200 | OK | The request was successful | GET, PATCH operations |
| 201 | Created | A new resource was created | POST operations |
| 202 | Accepted | The request was accepted for processing | Asynchronous operations |
| 204 | No Content | The request was successful, no response body | DELETE operations |

### Client Error Codes

| Code | Name | Description | Example |
|------|------|-------------|---------|
| 400 | Bad Request | The request was malformed or invalid | Missing required field |
| 401 | Unauthorized | Authentication is required or failed | Invalid token |
| 403 | Forbidden | The client lacks permission | Insufficient privileges |
| 404 | Not Found | The requested resource doesn't exist | Invalid resource ID |
| 409 | Conflict | The request conflicts with the current state | Duplicate resource |
| 422 | Unprocessable Entity | The request was well-formed but invalid | Business rule violation |
| 429 | Too Many Requests | Rate limit exceeded | API throttling |

### Server Error Codes

| Code | Name | Description |
|------|------|-------------|
| 500 | Internal Server Error | An unexpected error occurred |
| 502 | Bad Gateway | Invalid response from an upstream server |
| 503 | Service Unavailable | The service is temporarily unavailable |
| 504 | Gateway Timeout | An upstream server timed out |

## Common Error Codes

The ProposalForge API uses consistent error codes across all endpoints.

### Authentication Errors

| Code | Message | Status Code |
|------|---------|-------------|
| `unauthorized` | Authentication is required to access this resource | 401 |
| `invalid_token` | The provided authentication token is invalid or expired | 401 |
| `forbidden` | You do not have permission to access this resource | 403 |

### Resource Errors

| Code | Message | Status Code |
|------|---------|-------------|
| `resource_not_found` | The requested {resource} could not be found | 404 |
| `resource_already_exists` | A {resource} with this {identifier} already exists | 409 |

### Validation Errors

| Code | Message | Status Code |
|------|---------|-------------|
| `validation_error` | The request was invalid | 400 |
| `missing_required_field` | Required field {field} is missing | 400 |
| `invalid_field_format` | Field {field} has an invalid format | 400 |
| `invalid_enum_value` | Field {field} must be one of: {values} | 400 |

### Business Logic Errors

| Code | Message | Status Code |
|------|---------|-------------|
| `business_rule_violation` | The operation violates a business rule | 422 |
| `dependency_conflict` | The operation conflicts with a dependent resource | 422 |
| `state_conflict` | The operation is not valid in the current state | 422 |

### System Errors

| Code | Message | Status Code |
|------|---------|-------------|
| `internal_error` | An unexpected error occurred | 500 |
| `service_unavailable` | The service is temporarily unavailable | 503 |

## Asynchronous Operations

Some operations in the ProposalForge API are handled asynchronously (e.g., generating outlines, processing large documents). These follow a specific pattern:

### Request

```http
POST /workspaces/550e8400-e29b-41d4-a716-446655440000/proposals/6d619cbc-7357-4401-9d1c-845661765101/outlines/generate
```

### Initial Response (202 Accepted)

```json
{
  "data": {
    "id": "7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "status": "pending",
    "type": "outline_generation",
    "createdAt": "2023-05-15T10:30:15.123Z"
  },
  "links": {
    "self": "/v1/operations/7b15e8c2-6a35-4127-8f98-b72d7bc5417b"
  }
}
```

### Polling Status

```http
GET /operations/7b15e8c2-6a35-4127-8f98-b72d7bc5417b
```

Response:

```json
{
  "data": {
    "id": "7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "status": "processing",
    "progress": 65,
    "type": "outline_generation",
    "createdAt": "2023-05-15T10:30:15.123Z",
    "updatedAt": "2023-05-15T10:31:12.456Z"
  },
  "links": {
    "self": "/v1/operations/7b15e8c2-6a35-4127-8f98-b72d7bc5417b"
  }
}
```

### Completion Response

```json
{
  "data": {
    "id": "7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "status": "completed",
    "progress": 100,
    "type": "outline_generation",
    "createdAt": "2023-05-15T10:30:15.123Z",
    "updatedAt": "2023-05-15T10:32:45.789Z",
    "result": {
      "outlineId": "8f01a5d9-8052-4b8b-b4e0-63e6dcea7441"
    }
  },
  "links": {
    "self": "/v1/operations/7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "result": "/v1/workspaces/550e8400-e29b-41d4-a716-446655440000/proposals/6d619cbc-7357-4401-9d1c-845661765101/outlines/8f01a5d9-8052-4b8b-b4e0-63e6dcea7441"
  }
}
```

### Error Response

```json
{
  "data": {
    "id": "7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "status": "failed",
    "type": "outline_generation",
    "createdAt": "2023-05-15T10:30:15.123Z",
    "updatedAt": "2023-05-15T10:33:22.111Z",
    "error": {
      "code": "processing_error",
      "message": "Failed to generate outline due to insufficient context"
    }
  },
  "links": {
    "self": "/v1/operations/7b15e8c2-6a35-4127-8f98-b72d7bc5417b"
  }
}
```

## Webhooks

For long-running operations, clients can register webhooks to receive notifications:

### Webhook Registration

```json
POST /webhooks

{
  "url": "https://example.com/webhook-handler",
  "events": ["operation.completed", "document.processed"],
  "description": "Notification endpoint for async operations"
}
```

### Webhook Payload Format

```json
{
  "event": "operation.completed",
  "timestamp": "2023-05-15T10:32:45.789Z",
  "data": {
    "operationId": "7b15e8c2-6a35-4127-8f98-b72d7bc5417b",
    "status": "completed",
    "type": "outline_generation",
    "result": {
      "outlineId": "8f01a5d9-8052-4b8b-b4e0-63e6dcea7441"
    }
  }
}
```

## Rate Limiting

The ProposalForge API implements rate limiting to ensure fair usage:

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1589458403
```

### Rate Limit Exceeded Response (429 Too Many Requests)

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please slow down your requests.",
    "details": {
      "limit": 100,
      "reset": 1589458403,
      "resetIn": 60
    }
  }
}
```

## File Uploads

The ProposalForge API uses a two-step process for file uploads:

### 1. Request Upload URL

```http
POST /workspaces/550e8400-e29b-41d4-a716-446655440000/documents
Content-Type: application/json

{
  "name": "RFP Document.pdf",
  "type": "rfp",
  "mimeType": "application/pdf",
  "fileSize": 1024000
}
```

Response:

```json
{
  "data": {
    "id": "8f01a5d9-8052-4b8b-b4e0-63e6dcea7441",
    "name": "RFP Document.pdf",
    "type": "rfp",
    "status": "pending",
    "uploadUrl": "https://proposalforge-uploads.s3.amazonaws.com/documents/8f01a5d9-8052-4b8b-b4e0-63e6dcea7441?X-Amz-Algorithm=..."
  }
}
```

### 2. Upload File

```http
PUT https://proposalforge-uploads.s3.amazonaws.com/documents/8f01a5d9-8052-4b8b-b4e0-63e6dcea7441?X-Amz-Algorithm=...
Content-Type: application/pdf

[Binary file data]
```

## Conclusion

This document outlines the standardized request and response formats, as well as HTTP status codes used across the ProposalForge API. By maintaining consistency in these formats, we provide a predictable and developer-friendly API experience.

Developers should refer to this document as the authoritative reference for how to format requests and interpret responses when integrating with the ProposalForge API.