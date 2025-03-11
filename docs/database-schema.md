# ProposalForge Database Schema Design

## Overview

This document outlines the database schema design for ProposalForge, detailing the data structures that will support both the MVP and Enterprise versions of the application. The schema is designed to accommodate single-user functionality initially while containing the structural foundations needed for multi-user collaboration in the Enterprise version.

## Database Technologies

ProposalForge utilizes multiple database technologies, each optimized for specific data types and access patterns:

1. **PostgreSQL (Primary Relational Database)**
   - Stores structured application data
   - Handles relationships between entities
   - Maintains transaction integrity

2. **Qdrant (Vector Database)**
   - Stores document embeddings
   - Enables semantic search
   - Supports retrieval augmented generation (RAG)

3. **Amazon S3 (Object Storage)**
   - Stores original documents
   - Maintains exported files
   - Houses large binary assets

4. **Redis (Cache)**
   - Caches frequent queries
   - Stores session data
   - Manages real-time collaboration state

This document focuses primarily on the PostgreSQL schema design, with references to how it interfaces with the other data stores.

## PostgreSQL Schema Design

### Schema Overview

```
┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
│      Users         │       │    Workspaces      │       │    Documents       │
├────────────────────┤       ├────────────────────┤       ├────────────────────┤
│ id                 │       │ id                 │       │ id                 │
│ external_id        │◄──┐   │ name               │       │ workspace_id       │
│ email              │   │   │ description        │       │ name               │
│ name               │   │   │ created_at         │       │ type               │
│ role               │   │   │ updated_at         │   ┌───│ category           │
│ created_at         │   │   │ owner_id           │───┘   │ s3_key             │
│ updated_at         │   │   │ is_archived        │       │ created_at         │
└────────────────────┘   │   └────────────────────┘       │ updated_at         │
                         │             │                  │ created_by         │
                         │             │                  │ status             │
                         │             ▼                  └────────────────────┘
┌────────────────────┐   │   ┌────────────────────┐                 │
│   UserWorkspaces   │   │   │   Proposals        │                 │
├────────────────────┤   │   ├────────────────────┤                 │
│ user_id            │───┘   │ id                 │                 │
│ workspace_id       │───────│ workspace_id       │                 │
│ role               │       │ name               │                 │
│ joined_at          │       │ description        │                 │
└────────────────────┘       │ status             │                 │
                             │ created_at         │                 │
                             │ updated_at         │                 │
                             │ created_by         │                 │
                             └────────────────────┘                 │
                                       │                            │
               ┌─────────────────────┬─┴──────────────────┐         │
               │                     │                    │         │
               ▼                     ▼                    ▼         │
┌────────────────────┐   ┌────────────────────┐   ┌────────────────-┴──┐
│     Outlines       │   │     Sections       │   │  DocumentChunks    │
├────────────────────┤   ├────────────────────┤   ├────────────────────┤
│ id                 │   │ id                 │   │ id                 │
│ proposal_id        │   │ proposal_id        │   │ document_id        │
│ name               │   │ outline_id         │◄──│ content            │
│ description        │   │ parent_id          │   │ metadata           │
│ version            │   │ order              │   │ embedding_id       │
│ created_at         │   │ title              │   │ created_at         │
│ updated_at         │   │ content            │   └────────────────────┘
│ created_by         │   │ status             │
└────────────────────┘   │ assigned_to        │
        │                │ created_at         │
        │                │ updated_at         │
        │                │ created_by         │
        │                │ last_updated_by    │
        ▼                └────────────────────┘
┌────────────────────┐             │
│   OutlineItems     │             │
├────────────────────┤             │
│ id                 │             │
│ outline_id         │             │
│ parent_id          │             │
│ title              │             │
│ order              │             │
│ section_id         │◄────────────┘
│ created_at         │
│ updated_at         │
└────────────────────┘
                                         
┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
│     WinThemes      │   │    Comments        │   │   FeatureFlags     │
├────────────────────┤   ├────────────────────┤   ├────────────────────┤
│ id                 │   │ id                 │   │ id                 │
│ proposal_id        │   │ section_id         │   │ name               │
│ name               │   │ user_id            │   │ description        │
│ description        │   │ content            │   │ enabled            │
│ created_at         │   │ created_at         │   │ created_at         │
│ updated_at         │   │ updated_at         │   │ updated_at         │
│ created_by         │   │ resolved           │   └────────────────────┘
└────────────────────┘   │ resolved_by        │
                         │ resolved_at        │
                         └────────────────────┘

┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
│   KnowledgeItems   │   │  SectionVersions   │   │    Feedback        │
├────────────────────┤   ├────────────────────┤   ├────────────────────┤
│ id                 │   │ id                 │   │ id                 │
│ name               │   │ section_id         │   │ user_id            │
│ description        │   │ content            │   │ content            │
│ s3_key             │   │ created_at         │   │ type               │
│ type               │   │ created_by         │   │ context            │
│ category           │   │ version_number     │   │ rating             │
│ is_global          │   └────────────────────┘   │ created_at         │
│ created_at         │                            └────────────────────┘
│ updated_at         │
│ created_by         │
└────────────────────┘
```

### Detailed Table Definitions

#### 1. Users Table

Stores user account information. Designed to support both individual users in MVP and organizational users in Enterprise.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(255) NOT NULL UNIQUE,  -- ID from Clerk
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',  -- 'user', 'admin', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb,  -- User preferences
    last_login_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_external_id ON users(external_id);
```

#### 2. Workspaces Table

Central organizational unit for proposals. In MVP, there's typically one workspace per proposal, but Enterprise will support collaborative workspaces.

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    owner_id UUID NOT NULL REFERENCES users(id),
    is_archived BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}'::jsonb,  -- Workspace configuration
    organization_id UUID NULL,  -- For Enterprise: links to organization
    
    -- For MVP, these are not used but included for future Enterprise capability
    is_collaborative BOOLEAN DEFAULT FALSE,
    collaboration_settings JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_organization ON workspaces(organization_id);
```

#### 3. UserWorkspaces Table

Junction table for users and workspaces. Primarily for Enterprise, but included in MVP to support future expansion.

```sql
CREATE TABLE user_workspaces (
    user_id UUID NOT NULL REFERENCES users(id),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    role VARCHAR(50) NOT NULL DEFAULT 'member',  -- 'member', 'admin', etc.
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (user_id, workspace_id)
);

-- Indexes
CREATE INDEX idx_user_workspaces_user ON user_workspaces(user_id);
CREATE INDEX idx_user_workspaces_workspace ON user_workspaces(workspace_id);
```

#### 4. Documents Table

Stores metadata about uploaded documents. Actual document content stored in S3.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'rfp', 'sow', 'support'
    category VARCHAR(100),
    s3_key VARCHAR(255) NOT NULL,  -- Key for S3 object
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'processing',  -- 'processing', 'ready', 'error'
    file_size BIGINT,
    mime_type VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,  -- Additional document metadata
    is_global BOOLEAN DEFAULT FALSE  -- For universal knowledge base
);

-- Indexes
CREATE INDEX idx_documents_workspace ON documents(workspace_id);
CREATE INDEX idx_documents_created_by ON documents(created_by);
CREATE INDEX idx_documents_type_category ON documents(type, category);
CREATE INDEX idx_documents_is_global ON documents(is_global);
```

#### 5. DocumentChunks Table

Stores textual chunks of documents for RAG. Links to embeddings in Qdrant.

```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,  -- Position, page, etc.
    embedding_id VARCHAR(255),  -- ID in Qdrant
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_document_chunks_embedding ON document_chunks(embedding_id);
```

#### 6. Proposals Table

Represents a proposal response to an RFP. Central entity for proposal management.

```sql
CREATE TABLE proposals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'in-progress', 'complete'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    settings JSONB DEFAULT '{}'::jsonb,  -- Proposal-specific settings
    
    -- Additional metadata
    due_date TIMESTAMP WITH TIME ZONE,
    customer VARCHAR(255),
    estimated_value DECIMAL(15,2),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_proposals_workspace ON proposals(workspace_id);
CREATE INDEX idx_proposals_created_by ON proposals(created_by);
CREATE INDEX idx_proposals_status ON proposals(status);
```

#### 7. Outlines Table

Stores proposal outlines generated by the LLM or created manually.

```sql
CREATE TABLE outlines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proposal_id UUID NOT NULL REFERENCES proposals(id),
    name VARCHAR(255) NOT NULL DEFAULT 'Default Outline',
    description TEXT,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_outlines_proposal ON outlines(proposal_id);
CREATE INDEX idx_outlines_created_by ON outlines(created_by);
```

#### 8. OutlineItems Table

Hierarchical structure of outline elements. Represents the structure of the proposal.

```sql
CREATE TABLE outline_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    outline_id UUID NOT NULL REFERENCES outlines(id),
    parent_id UUID REFERENCES outline_items(id),
    title VARCHAR(255) NOT NULL,
    order INT NOT NULL,
    section_id UUID REFERENCES sections(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional attributes
    description TEXT,
    estimated_length VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending'  -- 'pending', 'in-progress', 'complete'
);

-- Indexes
CREATE INDEX idx_outline_items_outline ON outline_items(outline_id);
CREATE INDEX idx_outline_items_parent ON outline_items(parent_id);
CREATE INDEX idx_outline_items_section ON outline_items(section_id);
```

#### 9. Sections Table

Content sections of the proposal, linked to outline items.

```sql
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proposal_id UUID NOT NULL REFERENCES proposals(id),
    outline_id UUID REFERENCES outlines(id),
    parent_id UUID REFERENCES sections(id),  -- For nested sections
    order INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'in-review', 'approved'
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    last_updated_by UUID REFERENCES users(id),
    
    -- Additional attributes
    word_count INT,
    metadata JSONB DEFAULT '{}'::jsonb,
    review_status VARCHAR(50) DEFAULT 'pending'  -- 'pending', 'reviewed', 'changes-requested'
);

-- Indexes
CREATE INDEX idx_sections_proposal ON sections(proposal_id);
CREATE INDEX idx_sections_outline ON sections(outline_id);
CREATE INDEX idx_sections_parent ON sections(parent_id);
CREATE INDEX idx_sections_assigned_to ON sections(assigned_to);
CREATE INDEX idx_sections_created_by ON sections(created_by);
```

#### 10. SectionVersions Table

Version history of section content. Enables tracking changes over time.

```sql
CREATE TABLE section_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    version_number INT NOT NULL,
    
    -- Additional metadata
    change_description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_section_versions_section ON section_versions(section_id);
CREATE INDEX idx_section_versions_created_by ON section_versions(created_by);
```

#### 11. WinThemes Table

Stores win themes for proposals. These influence content generation by the LLM.

```sql
CREATE TABLE win_themes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proposal_id UUID NOT NULL REFERENCES proposals(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Additional attributes
    priority INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_win_themes_proposal ON win_themes(proposal_id);
CREATE INDEX idx_win_themes_created_by ON win_themes(created_by);
```

#### 12. Comments Table

Stores comments on proposal sections. Primarily for Enterprise but included for future expansion.

```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id),
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional attributes
    parent_id UUID REFERENCES comments(id),  -- For threaded comments
    position JSONB  -- Position in document for inline comments
);

-- Indexes
CREATE INDEX idx_comments_section ON comments(section_id);
CREATE INDEX idx_comments_user ON comments(user_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
```

#### 13. KnowledgeItems Table

Stores knowledge base items accessible across proposals. Both global and workspace-specific items.

```sql
CREATE TABLE knowledge_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    s3_key VARCHAR(255) NOT NULL,  -- Key for S3 object
    type VARCHAR(50) NOT NULL,  -- 'proposal', 'capability', 'template'
    category VARCHAR(100),
    is_global BOOLEAN DEFAULT FALSE,  -- Is it part of universal knowledge base?
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    
    -- Additional attributes
    workspace_id UUID REFERENCES workspaces(id),  -- Only for workspace-specific items
    tags TEXT[],
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_knowledge_items_type_category ON knowledge_items(type, category);
CREATE INDEX idx_knowledge_items_is_global ON knowledge_items(is_global);
CREATE INDEX idx_knowledge_items_workspace ON knowledge_items(workspace_id);
CREATE INDEX idx_knowledge_items_created_by ON knowledge_items(created_by);
CREATE INDEX idx_knowledge_items_tags ON knowledge_items USING GIN(tags);
```

#### 14. Feedback Table

Stores user feedback on LLM-generated content for improvement.

```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'outline', 'section', 'general'
    context JSONB NOT NULL,  -- References to relevant entities
    rating INT,  -- 1-5 rating
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_feedback_user ON feedback(user_id);
CREATE INDEX idx_feedback_type ON feedback(type);
```

#### 15. FeatureFlags Table

Manages feature flags for gradually enabling Enterprise features.

```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional attributes
    conditions JSONB DEFAULT '{}'::jsonb,  -- Complex enabling conditions
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_feature_flags_name ON feature_flags(name);
CREATE INDEX idx_feature_flags_enabled ON feature_flags(enabled);
```

### Additional Tables for Enterprise Version

These tables will be included in the MVP schema design but only activated for the Enterprise version:

#### 16. Organizations Table

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb,
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(50) DEFAULT 'active'
);
```

#### 17. OrganizationUsers Table

```sql
CREATE TABLE organization_users (
    organization_id UUID NOT NULL REFERENCES organizations(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (organization_id, user_id)
);
```

#### 18. Teams Table

```sql
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 19. TeamMembers Table

```sql
CREATE TABLE team_members (
    team_id UUID NOT NULL REFERENCES teams(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (team_id, user_id)
);
```

## Vector Database Schema (Qdrant)

Qdrant stores document embeddings for semantic search. The structure includes:

### Collections

1. **document_chunks**
   - Vector dimension: 1536 (OpenAI embedding size)
   - Metric: Cosine similarity
   - Payload schema:
     - document_id: UUID
     - chunk_id: UUID
     - content: String
     - metadata: Object
       - page: Integer
       - position: Integer
       - is_global: Boolean
       - workspace_id: UUID
       - document_type: String
       - category: String

2. **win_themes**
   - Vector dimension: 1536
   - Metric: Cosine similarity
   - Payload schema:
     - theme_id: UUID
     - proposal_id: UUID
     - name: String
     - description: String

## Implementation and Migration Strategy

### Schema Evolution

The database schema will evolve in phases:

1. **MVP Phase (Months 1-2)**
   - Implement core tables: Users, Workspaces, Documents, DocumentChunks, Proposals, Outlines, OutlineItems, Sections, WinThemes
   - Establish Qdrant collections for document chunks
   - Set up S3 bucket structure

2. **MVP Enhancement (Months 3-4)**
   - Add SectionVersions for version history
   - Implement Feedback table
   - Add FeatureFlags table

3. **Enterprise Groundwork (Months 5-7)**
   - Activate UserWorkspaces relationship
   - Implement Comments table
   - Set up Organizations, Teams structures (disabled via feature flags)

4. **Enterprise Release (Months 8-10)**
   - Fully activate all tables
   - Enhance schema with additional indices for performance
   - Implement partition strategies for larger datasets

### Migration Strategy

All schema changes will follow these principles:

1. **Non-destructive changes only**
   - New tables and columns are added without removing existing ones
   - Deprecated fields are marked but not removed immediately

2. **Version-controlled migrations**
   - All migrations are tracked in version control
   - Each migration has up and down scripts
   - Migrations are applied automatically during deployment

3. **Data integrity**
   - Foreign key constraints ensure data consistency
   - Transactions protect against partial updates
   - Backup before migration

4. **Feature flag compatibility**
   - Schema supports both feature-on and feature-off states
   - Default values ensure backward compatibility

## Performance Considerations

### Indexing Strategy

The schema includes carefully designed indexes to optimize common query patterns:

1. **Primary access paths**
   - All foreign keys are indexed
   - Common filter columns have dedicated indexes

2. **Composite indexes**
   - Multi-column indexes for frequently combined filters
   - Type + category indexes for document filtering

3. **Full-text search**
   - GIN indexes for array and JSONB data
   - Text search capabilities via PostgreSQL text search

### Query Optimization

1. **Pagination**
   - All list endpoints support keyset pagination
   - Avoid OFFSET for large datasets

2. **Selective retrieval**
   - Use column selection to minimize data transfer
   - JSON path queries for targeted JSONB access

3. **Denormalization**
   - Strategic duplication for read performance
   - Materialized views for complex aggregations (Enterprise)

## Security Considerations

### Data Protection

1. **Column-level encryption**
   - Sensitive fields encrypted at the application level
   - Encryption keys managed via AWS KMS

2. **Row-level security**
   - PostgreSQL RLS policies for multi-tenant isolation
   - Automatic filtering based on user context

3. **Audit trails**
   - Creation and modification timestamps on all tables
   - User attribution for all changes

## Conclusion

The ProposalForge database schema is designed with both immediate MVP needs and future Enterprise capabilities in mind. The schema supports:

1. **Single-user MVP functionality**
   - Document management and embeddings
   - Proposal outline generation and editing
   - Section-based content creation with LLM assistance
   - Win theme integration

2. **Future Enterprise expansion**
   - Multi-user collaboration
   - Organizational hierarchy
   - Team-based workflows
   - Advanced analytics

This schema design ensures a smooth transition between phases without requiring data migration or schema redesign, fulfilling the core architectural principle of building for growth from day one.
