# ProposalForge API Documentation

This directory contains comprehensive documentation for the ProposalForge API, which supports both the MVP and Enterprise versions of the application.

## Documentation Files

- **[openapi-specification.yaml](./openapi-specification.yaml)** - Complete OpenAPI/Swagger specification detailing all endpoints, request/response schemas, and parameters
- **[authentication-flow.md](./authentication-flow.md)** - Documentation of authentication processes, token lifecycle, and security considerations
- **[api-versioning-strategy.md](./api-versioning-strategy.md)** - Guidelines for API versioning, evolution, and deprecation
- **[request-response-formats.md](./request-response-formats.md)** - Standardized formats for requests, responses, and error handling

## API Principles

The ProposalForge API is built on the following core principles:

1. **REST-Based Design** - Resource-oriented architecture with standard HTTP methods
2. **Consistent Patterns** - Uniform request/response formats across all endpoints
3. **Version Stability** - Backward compatibility within major versions
4. **Secure by Default** - Authentication required for all endpoints
5. **Developer-Friendly** - Clear error messages, pagination, and comprehensive documentation
6. **Feature Flag Controls** - Enterprise features isolated behind feature flags

## Authentication

The API uses JWT-based authentication via the Clerk service. Tokens are required for all endpoints except authentication operations.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

For details, see the [authentication flow documentation](./authentication-flow.md).

## Versioning

API versions are specified in the URL path:

```
https://api.proposalforge.com/v1/workspaces
```

The current stable version is `v1`. For details on the versioning strategy, see the [API versioning documentation](./api-versioning-strategy.md).

## Running the OpenAPI Documentation

The OpenAPI specification can be viewed using Swagger UI:

1. Install Swagger UI dependencies:
   ```
   npm install -g swagger-ui-cli
   ```

2. Start the Swagger UI server:
   ```
   swagger-ui-cli serve ./openapi-specification.yaml
   ```

3. Open a browser to `http://localhost:3000`

## API Client Libraries

### JavaScript/TypeScript Client

```javascript
import { ProposalForgeClient } from '@proposalforge/api-client';

const client = new ProposalForgeClient({
  baseUrl: 'https://api.proposalforge.com',
  version: 'v1',
  apiKey: 'your-api-key'
});

// Example: List workspaces
const workspaces = await client.workspaces.list();
```

### Node.js Client

```javascript
const { ProposalForgeClient } = require('@proposalforge/api-client');

const client = new ProposalForgeClient({
  baseUrl: 'https://api.proposalforge.com',
  version: 'v1',
  apiKey: 'your-api-key'
});

// Example: Create a new workspace
client.workspaces.create({
  name: 'New Workspace',
  description: 'Workspace for project X'
})
.then(workspace => console.log(workspace))
.catch(error => console.error(error));
```

## Rate Limits

The API implements rate limiting to ensure fair usage:

- **Standard Rate Limit**: 100 requests per minute per API key
- **Burst Rate Limit**: 20 requests per second per API key

Rate limit information is returned in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1589458403
```

## Support

For questions about the API, please contact:

- **Email**: api-support@proposalforge.com
- **Developer Portal**: https://developers.proposalforge.com

## Future Documentation

Additional API documentation will be added as the ProposalForge platform evolves, including:

- Detailed integration guides
- Code samples for common operations
- Webhook implementation examples
- Best practices for API usage

## Contributing

To suggest improvements to the API documentation:

1. Create a new branch
2. Make your changes
3. Submit a pull request with a clear description of your updates

All documentation is reviewed for accuracy and completeness before merging.