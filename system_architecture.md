# System Architecture & Schema Documentation

## Overview
This document provides a comprehensive overview of the Clearfacts invoice integration system architecture, including system diagrams, data flow schemas, and component interactions.

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Frontend Admin Interface]
    end
    
    subgraph "API Gateway Layer"
        IG[Istio Ingress Gateway]
        LB[Load Balancer]
    end
    
    subgraph "Application Layer"
        subgraph "FastAPI Backend"
            API[FastAPI Service]
            AUTH[Authentication Service]
            LOG[Logging Service]
        end
        
        subgraph "Dagster Orchestration"
            DAG[Dagster Daemon]
            SCHED[Scheduler]
            MON[Monitoring]
        end
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL Database)]
        REDIS[(Redis Cache)]
        PVC[Persistent Volumes]
    end
    
    subgraph "External Systems"
        JAVA[Java Backend<br/>Invoice Source]
        CF[Clearfacts API<br/>Invoice Destination]
        SLACK[Slack API<br/>Notifications]
    end
    
    subgraph "Infrastructure Layer"
        K8S[Kubernetes Cluster]
        PROM[Prometheus<br/>Monitoring]
        GRAF[Grafana<br/>Dashboards]
        JAEGER[Jaeger<br/>Tracing]
    end
    
    %% Frontend to API Gateway
    FE --> IG
    IG --> LB
    LB --> API
    
    %% API Gateway to Services
    LB --> DAG
    
    %% FastAPI Internal
    API --> AUTH
    API --> LOG
    API --> DB
    API --> REDIS
    
    %% Dagster Internal
    DAG --> SCHED
    DAG --> MON
    DAG --> PVC
    
    %% External API Calls
    API --> JAVA
    API --> CF
    API --> SLACK
    
    %% Dagster External Calls
    DAG --> API
    
    %% Infrastructure Monitoring
    PROM --> API
    PROM --> DAG
    GRAF --> PROM
    JAEGER --> API
    JAEGER --> DAG
    
    %% Data Storage
    API --> DB
    DAG --> DB
    API --> REDIS
```

## Data Flow Architecture

### 1. Scheduled Invoice Processing Flow

```mermaid
sequenceDiagram
    participant S as Dagster Scheduler
    participant D as Dagster Daemon
    participant F as FastAPI Backend
    participant J as Java Backend
    participant C as Clearfacts API
    participant S as Slack API
    participant DB as Database
    
    Note over S: Every 24h at 2 AM CET
    
    S->>D: Trigger scheduled job
    D->>F: Call invoice processing endpoint
    F->>J: GET /invoices (retrieve UBL invoices)
    J-->>F: Return invoice list
    
    F->>DB: Check for duplicates
    DB-->>F: Return duplicate status
    
    F->>C: POST /invoices (send UBL invoices)
    C-->>F: Return processing result
    
    F->>DB: Log job execution
    F-->>D: Return job result
    
    alt Job Success
        D->>S: Send success notification
    else Job Failure
        D->>S: Send failure notification
        S-->>D: Alert sent to Slack
    end
```

### 2. Manual Invoice Processing Flow

```mermaid
sequenceDiagram
    participant U as User (Frontend)
    participant F as FastAPI Backend
    participant J as Java Backend
    participant C as Clearfacts API
    participant DB as Database
    
    U->>F: POST /api/v1/invoices/process
    F->>F: Validate authentication
    F->>J: GET /invoices (retrieve UBL invoices)
    J-->>F: Return invoice list
    
    F->>DB: Check for duplicates
    DB-->>F: Return duplicate status
    
    F->>C: POST /invoices (send UBL invoices)
    C-->>F: Return processing result
    
    F->>DB: Log job execution
    F-->>U: Return job status and result
```

## Component Architecture

### 1. FastAPI Backend Components

```mermaid
graph LR
    subgraph "FastAPI Backend"
        subgraph "API Layer"
            API1[Invoice Endpoints]
            API2[Job Management]
            API3[Admin Endpoints]
        end
        
        subgraph "Service Layer"
            SVC1[Invoice Service]
            SVC2[Clearfacts Client]
            SVC3[Java Backend Client]
            SVC4[Notification Service]
        end
        
        subgraph "Data Layer"
            MOD1[Invoice Models]
            MOD2[Job Models]
            MOD3[User Models]
        end
        
        subgraph "Utility Layer"
            UTIL1[Logging]
            UTIL2[Validation]
            UTIL3[Exceptions]
        end
    end
    
    API1 --> SVC1
    API2 --> SVC1
    API3 --> SVC1
    
    SVC1 --> SVC2
    SVC1 --> SVC3
    SVC1 --> SVC4
    
    SVC1 --> MOD1
    SVC1 --> MOD2
    
    SVC1 --> UTIL1
    SVC1 --> UTIL2
    SVC1 --> UTIL3
```

### 2. Dagster Orchestration Components

```mermaid
graph LR
    subgraph "Dagster Orchestration"
        subgraph "Asset Layer"
            AST1[Raw Invoices]
            AST2[Validated Invoices]
            AST3[Processed Invoices]
            AST4[Job Metrics]
        end
        
        subgraph "Operation Layer"
            OP1[Retrieve Invoices]
            OP2[Validate Invoices]
            OP3[Send to Clearfacts]
            OP4[Send Notifications]
        end
        
        subgraph "Job Layer"
            JOB1[Daily Processing]
            JOB2[Health Monitoring]
            JOB3[Manual Trigger]
        end
        
        subgraph "Resource Layer"
            RES1[FastAPI Client]
            RES2[Slack Client]
            RES3[Configuration]
        end
    end
    
    AST1 --> OP1
    AST2 --> OP2
    AST3 --> OP3
    AST4 --> OP4
    
    OP1 --> AST1
    OP2 --> AST2
    OP3 --> AST3
    OP4 --> AST4
    
    JOB1 --> OP1
    JOB1 --> OP2
    JOB1 --> OP3
    JOB1 --> OP4
    
    OP1 --> RES1
    OP3 --> RES1
    OP4 --> RES2
```

## Database Schema

### 1. Core Tables

```sql
-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table for tracking invoice processing jobs
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL, -- 'scheduled', 'manual'
    status VARCHAR(50) NOT NULL, -- 'pending', 'running', 'completed', 'failed'
    triggered_by UUID REFERENCES users(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table for tracking processed invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    invoice_id VARCHAR(255) NOT NULL,
    ubl_data TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'pending', 'sent', 'failed', 'duplicate'
    clearfacts_response JSONB,
    error_message TEXT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table for tracking all operations
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configuration table for system settings
CREATE TABLE configuration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Indexes for Performance

```sql
-- Performance indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);

CREATE INDEX idx_invoices_job_id ON invoices(job_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_invoice_id ON invoices(invoice_id);
CREATE INDEX idx_invoices_processed_at ON invoices(processed_at);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

CREATE INDEX idx_configuration_key ON configuration(key);
```

## API Schema Definitions

### 1. Invoice Processing Request/Response

```json
{
  "request": {
    "endpoint": "POST /api/v1/invoices/process",
    "headers": {
      "Authorization": "Bearer <jwt_token>",
      "Content-Type": "application/json"
    },
    "body": {
      "force_processing": false,
      "invoice_ids": ["optional", "specific", "invoice", "ids"]
    }
  },
  "response": {
    "success": true,
    "data": {
      "job_id": "uuid",
      "status": "pending",
      "estimated_completion": "2024-01-15T10:30:00Z",
      "message": "Invoice processing job started"
    },
    "timestamp": "2024-01-15T10:00:00Z",
    "correlation_id": "uuid"
  }
}
```

### 2. Job Status Response

```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "completed",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": "2024-01-15T10:05:00Z",
    "duration_seconds": 300,
    "results": {
      "total_invoices": 25,
      "processed": 23,
      "failed": 1,
      "duplicates": 1
    },
    "errors": [
      {
        "invoice_id": "INV-001",
        "error": "Invalid UBL format",
        "timestamp": "2024-01-15T10:02:00Z"
      }
    ]
  },
  "timestamp": "2024-01-15T10:05:00Z",
  "correlation_id": "uuid"
}
```

### 3. Error Response Schema

```json
{
  "success": false,
  "error": {
    "code": "EXTERNAL_API_ERROR",
    "message": "Failed to connect to Clearfacts API",
    "details": {
      "api_endpoint": "https://api.clearfacts.com/invoices",
      "status_code": 503,
      "retry_count": 3,
      "next_retry_at": "2024-01-15T10:05:00Z"
    }
  },
  "timestamp": "2024-01-15T10:00:00Z",
  "correlation_id": "uuid"
}
```

## UBL Invoice Schema

### 1. UBL Invoice Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    
    <!-- Invoice Identification -->
    <cbc:ID>INV-2024-001</cbc:ID>
    <cbc:IssueDate>2024-01-15</cbc:IssueDate>
    <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
    
    <!-- Supplier Information -->
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>SUPPLIER-001</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>Supplier Company</cbc:Name>
            </cac:PartyName>
        </cac:Party>
    </cac:AccountingSupplierParty>
    
    <!-- Customer Information -->
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID>CUSTOMER-001</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>Customer Company</cbc:Name>
            </cac:PartyName>
        </cac:Party>
    </cac:AccountingCustomerParty>
    
    <!-- Invoice Lines -->
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="EA">10</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="EUR">100.00</cbc:LineExtensionAmount>
        <cac:Item>
            <cbc:Description>Product Description</cbc:Description>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="EUR">10.00</cbc:PriceAmount>
        </cac:Price>
    </cac:InvoiceLine>
    
    <!-- Totals -->
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="EUR">100.00</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="EUR">100.00</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="EUR">121.00</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="EUR">121.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    
</Invoice>
```

## Security Architecture

### 1. Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as FastAPI
    participant A as Auth Service
    participant DB as Database
    
    U->>F: POST /auth/login
    F->>A: Validate credentials
    A->>DB: Check user credentials
    DB-->>A: Return user data
    A-->>F: Generate JWT token
    F-->>U: Return JWT token
    
    Note over U,F: Subsequent requests include JWT token
    
    U->>F: POST /api/v1/invoices/process<br/>Authorization: Bearer <token>
    F->>A: Validate JWT token
    A-->>F: Token valid, user authorized
    F->>F: Process request
    F-->>U: Return response
```

### 2. Network Security

```mermaid
graph TB
    subgraph "External Network"
        INTERNET[Internet]
    end
    
    subgraph "DMZ"
        LB[Load Balancer]
        WAF[Web Application Firewall]
    end
    
    subgraph "Internal Network"
        subgraph "Kubernetes Cluster"
            IG[Istio Ingress Gateway]
            API[FastAPI Backend]
            DAG[Dagster Daemon]
            DB[(Database)]
        end
    end
    
    INTERNET --> LB
    LB --> WAF
    WAF --> IG
    IG --> API
    IG --> DAG
    API --> DB
    DAG --> DB
    
    %% Security layers
    LB -.->|SSL/TLS| WAF
    WAF -.->|Rate Limiting| IG
    IG -.->|mTLS| API
    IG -.->|mTLS| DAG
```

## Monitoring Architecture

### 1. Observability Stack

```mermaid
graph LR
    subgraph "Application Layer"
        API[FastAPI Backend]
        DAG[Dagster Daemon]
    end
    
    subgraph "Monitoring Stack"
        PROM[Prometheus<br/>Metrics Collection]
        GRAF[Grafana<br/>Visualization]
        JAEGER[Jaeger<br/>Distributed Tracing]
        ELK[ELK Stack<br/>Log Aggregation]
    end
    
    subgraph "Alerting"
        ALERT[AlertManager]
        SLACK[Slack Notifications]
        EMAIL[Email Notifications]
    end
    
    API --> PROM
    DAG --> PROM
    API --> JAEGER
    DAG --> JAEGER
    API --> ELK
    DAG --> ELK
    
    PROM --> GRAF
    PROM --> ALERT
    ALERT --> SLACK
    ALERT --> EMAIL
```

### 2. Key Metrics

```yaml
# Prometheus metrics configuration
metrics:
  fastapi_backend:
    - http_requests_total
    - http_request_duration_seconds
    - invoice_processing_total
    - invoice_processing_duration_seconds
    - external_api_calls_total
    - external_api_call_duration_seconds
  
  dagster:
    - dagster_job_runs_total
    - dagster_job_duration_seconds
    - dagster_asset_materializations_total
    - dagster_operation_executions_total
  
  system:
    - cpu_usage_percent
    - memory_usage_bytes
    - disk_usage_percent
    - network_io_bytes
```

## Deployment Architecture

### 1. Kubernetes Namespace Structure

```yaml
# Namespace organization
namespaces:
  clearfacts-system:
    - fastapi-backend
    - dagster-daemon
    - monitoring-stack
  
  clearfacts-data:
    - postgresql
    - redis
    - persistent-volumes
  
  clearfacts-networking:
    - istio-system
    - ingress-controllers
    - network-policies
```

### 2. Environment Configuration

```yaml
# Environment-specific configurations
environments:
  development:
    replicas: 1
    resources:
      cpu: "250m"
      memory: "512Mi"
    database:
      size: "5Gi"
  
  staging:
    replicas: 2
    resources:
      cpu: "500m"
      memory: "1Gi"
    database:
      size: "20Gi"
  
  production:
    replicas: 3
    resources:
      cpu: "1000m"
      memory: "2Gi"
    database:
      size: "100Gi"
```

This comprehensive architecture documentation provides the foundation for implementing the Clearfacts invoice integration system with proper scalability, security, and maintainability.
