# FastAPI Backend Development Rules

## Project Context
This is a FastAPI backend service for automated invoice processing and delivery to Clearfacts accounting system. The service handles both scheduled and manual invoice processing with comprehensive error handling and monitoring.

## Architecture Overview
- **Framework**: FastAPI with async/await patterns
- **Authentication**: JWT tokens and API key authentication
- **Database**: PostgreSQL for job tracking and audit logs
- **External APIs**: Java backend (invoice source) and Clearfacts API (destination)
- **Monitoring**: Structured logging with error tracking
- **Deployment**: Kubernetes with GitHub Actions CI/CD

## Development Guidelines

### Code Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection and models
│   ├── auth.py                # Authentication and authorization
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── invoices.py    # Invoice processing endpoints
│   │   │   ├── jobs.py        # Job management endpoints
│   │   │   └── admin.py       # Admin endpoints
│   │   └── dependencies.py    # Common dependencies
│   ├── services/
│   │   ├── __init__.py
│   │   ├── invoice_service.py # Core invoice processing logic
│   │   ├── clearfacts_client.py # Clearfacts API client
│   │   ├── java_backend_client.py # Java backend client
│   │   └── notification_service.py # Slack notifications
│   ├── models/
│   │   ├── __init__.py
│   │   ├── invoice.py         # Invoice data models
│   │   ├── job.py             # Job tracking models
│   │   └── user.py            # User models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── invoice.py         # Pydantic schemas
│   │   ├── job.py             # Job schemas
│   │   └── responses.py       # API response schemas
│   └── utils/
│       ├── __init__.py
│       ├── logging.py         # Logging configuration
│       ├── exceptions.py      # Custom exceptions
│       └── validators.py      # Data validation utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   ├── test_api/             # API endpoint tests
│   ├── test_services/        # Service layer tests
│   └── test_utils/           # Utility function tests
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
└── README.md                # Service documentation
```

### Key Principles

#### 1. Async/Await Pattern
- Use async/await for all I/O operations
- Implement proper error handling with try/catch blocks
- Use asyncio.gather() for concurrent operations when appropriate

#### 2. Error Handling
- Implement custom exception classes for different error types
- Use HTTP status codes appropriately (400, 401, 403, 404, 500, etc.)
- Log all errors with structured logging (JSON format)
- Implement retry logic with exponential backoff for external API calls

#### 3. Authentication & Authorization
- JWT tokens for user authentication
- API keys for service-to-service communication
- Role-based access control (admin, user, service)
- Secure credential management using environment variables

#### 4. Data Validation
- Use Pydantic models for request/response validation
- Validate UBL format invoices before processing
- Implement duplicate detection logic
- Sanitize all input data

#### 5. Logging & Monitoring
- Structured logging with correlation IDs
- Log all API calls to external services
- Track job execution metrics (duration, success/failure rates)
- Implement health check endpoints

### API Design Patterns

#### 1. RESTful Endpoints
```python
# Invoice processing
POST /api/v1/invoices/process          # Manual trigger
GET  /api/v1/invoices/status/{job_id}  # Job status
GET  /api/v1/invoices/history          # Processing history

# Job management
GET  /api/v1/jobs/{job_id}             # Job details
GET  /api/v1/jobs                      # List jobs
POST /api/v1/jobs/{job_id}/retry       # Retry failed job

# Admin endpoints
GET  /api/v1/admin/health              # Health check
GET  /api/v1/admin/metrics             # Service metrics
POST /api/v1/admin/test-connection     # Test external APIs
```

#### 2. Response Format
```python
{
    "success": bool,
    "data": any,
    "message": str,
    "timestamp": str,
    "correlation_id": str
}
```

#### 3. Error Response Format
```python
{
    "success": false,
    "error": {
        "code": str,
        "message": str,
        "details": dict
    },
    "timestamp": str,
    "correlation_id": str
}
```

### Service Layer Patterns

#### 1. Invoice Service
- Handle invoice retrieval from Java backend
- Implement UBL format validation
- Manage duplicate detection
- Coordinate with Clearfacts client

#### 2. External API Clients
- Implement circuit breaker pattern for resilience
- Use connection pooling for HTTP clients
- Implement proper timeout handling
- Add request/response logging

#### 3. Notification Service
- Send Slack notifications for failures
- Implement notification throttling
- Support different notification channels
- Include relevant context in notifications

### Database Patterns

#### 1. Models
- Use SQLAlchemy ORM with async support
- Implement soft deletes for audit trails
- Add created_at/updated_at timestamps
- Use UUIDs for primary keys

#### 2. Migrations
- Use Alembic for database migrations
- Version all schema changes
- Include rollback scripts
- Test migrations in staging environment

### Testing Strategy

#### 1. Unit Tests
- Test all service methods with mocked dependencies
- Achieve >90% code coverage
- Use pytest with async support
- Mock external API calls

#### 2. Integration Tests
- Test API endpoints with test database
- Test external API integrations with test environments
- Use test containers for database testing
- Implement end-to-end workflow tests

#### 3. Performance Tests
- Load testing for concurrent invoice processing
- Stress testing for large invoice batches
- Monitor memory usage and response times
- Test retry mechanisms under failure conditions

### Security Considerations

#### 1. Input Validation
- Validate all incoming data
- Sanitize file uploads
- Prevent SQL injection with parameterized queries
- Implement rate limiting

#### 2. Authentication
- Secure JWT token handling
- Implement token refresh mechanism
- Use secure session management
- Validate API keys properly

#### 3. Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper CORS policies
- Log security events

### Deployment Considerations

#### 1. Container Configuration
- Use multi-stage Docker builds
- Implement health checks
- Configure proper resource limits
- Use non-root user in container

#### 2. Environment Configuration
- Use environment variables for configuration
- Implement configuration validation
- Support multiple environments (dev, test, prod)
- Use secrets management for sensitive data

#### 3. Monitoring
- Implement Prometheus metrics
- Use structured logging
- Set up alerting for critical failures
- Monitor external API response times

### Code Quality Standards

#### 1. Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Implement proper docstrings
- Use meaningful variable names

#### 2. Documentation
- Document all API endpoints
- Include usage examples
- Maintain changelog
- Document deployment procedures

#### 3. Code Review
- Require code reviews for all changes
- Test all new features
- Update documentation with changes
- Ensure backward compatibility

### Performance Optimization

#### 1. Caching
- Implement Redis caching for frequently accessed data
- Cache external API responses when appropriate
- Use connection pooling for database connections
- Implement request deduplication

#### 2. Async Operations
- Use async/await for I/O operations
- Implement concurrent processing for multiple invoices
- Use asyncio.gather() for parallel operations
- Avoid blocking operations in async functions

#### 3. Resource Management
- Implement proper connection pooling
- Use context managers for resource cleanup
- Monitor memory usage
- Implement garbage collection optimization

This FastAPI backend should be robust, scalable, and maintainable while providing reliable invoice processing capabilities for the Clearfacts integration.

