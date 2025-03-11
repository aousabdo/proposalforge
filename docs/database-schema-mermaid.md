# ProposalForge Database Schema with Mermaid Diagrams

## Database Schema Overview

```mermaid
erDiagram
    Users {
        UUID id PK
        VARCHAR external_id
        VARCHAR email
        VARCHAR name
        VARCHAR role
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    Workspaces {
        UUID id PK
        VARCHAR name
        TEXT description
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID owner_id FK
        BOOLEAN is_archived
    }
    
    UserWorkspaces {
        UUID user_id PK,FK
        UUID workspace_id PK,FK
        VARCHAR role
        TIMESTAMP joined_at
    }
    
    Documents {
        UUID id PK
        UUID workspace_id FK
        VARCHAR name
        VARCHAR type
        VARCHAR category
        VARCHAR s3_key
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
        VARCHAR status
    }
    
    DocumentChunks {
        UUID id PK
        UUID document_id FK
        TEXT content
        JSONB metadata
        VARCHAR embedding_id
        TIMESTAMP created_at
    }
    
    Proposals {
        UUID id PK
        UUID workspace_id FK
        VARCHAR name
        TEXT description
        VARCHAR status
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
    }
    
    Outlines {
        UUID id PK
        UUID proposal_id FK
        VARCHAR name
        TEXT description
        INTEGER version
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
    }
    
    OutlineItems {
        UUID id PK
        UUID outline_id FK
        UUID parent_id FK
        VARCHAR title
        INTEGER order
        UUID section_id FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    Sections {
        UUID id PK
        UUID proposal_id FK
        UUID outline_id FK
        UUID parent_id FK
        INTEGER order
        VARCHAR title
        TEXT content
        VARCHAR status
        UUID assigned_to FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
        UUID last_updated_by FK
    }
    
    WinThemes {
        UUID id PK
        UUID proposal_id FK
        VARCHAR name
        TEXT description
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
    }
    
    Comments {
        UUID id PK
        UUID section_id FK
        UUID user_id FK
        TEXT content
        TIMESTAMP created_at
        TIMESTAMP updated_at
        BOOLEAN resolved
        UUID resolved_by FK
        TIMESTAMP resolved_at
    }
    
    FeatureFlags {
        UUID id PK
        VARCHAR name
        TEXT description
        BOOLEAN enabled
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }
    
    KnowledgeItems {
        UUID id PK
        VARCHAR name
        TEXT description
        VARCHAR s3_key
        VARCHAR type
        VARCHAR category
        BOOLEAN is_global
        TIMESTAMP created_at
        TIMESTAMP updated_at
        UUID created_by FK
    }
    
    SectionVersions {
        UUID id PK
        UUID section_id FK
        TEXT content
        TIMESTAMP created_at
        UUID created_by FK
        INTEGER version_number
    }
    
    Feedback {
        UUID id PK
        UUID user_id FK
        TEXT content
        VARCHAR type
        TEXT context
        INTEGER rating
        TIMESTAMP created_at
    }
    
    Users ||--o{ UserWorkspaces : has
    Workspaces ||--o{ UserWorkspaces : has
    
    Users ||--o{ Workspaces : owns
    Workspaces ||--o{ Documents : contains
    Workspaces ||--o{ Proposals : contains
    
    Documents ||--o{ DocumentChunks : chunked_into
    
    Proposals ||--o{ Outlines : has
    Proposals ||--o{ Sections : contains
    Proposals ||--o{ WinThemes : has
    
    Outlines ||--o{ OutlineItems : contains
    OutlineItems ||--o{ OutlineItems : has_children
    
    Sections ||--o{ Comments : has
    Sections ||--o{ SectionVersions : has_versions
    
    OutlineItems ||--|| Sections : links_to
    
    Users ||--o{ Comments : makes
    Users ||--o{ Feedback : submits
} 