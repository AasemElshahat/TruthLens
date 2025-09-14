# Technical Architecture Decisions

## Core Architectural Choices

### 1. Monolithic Backend (For Now)
**Decision**: Keep backend as single Python application during thesis
**Rationale**: 
- Simpler development and debugging
- Faster iteration on features
- Less operational complexity
- Can refactor to microservices post-thesis when needed

**Trade-offs**:
- ✅ Easier development and testing
- ✅ Single deployment unit
- ❌ Harder to scale individual components
- ❌ Technology coupling

### 2. LLM Abstraction Layer
**Decision**: Create provider-agnostic interface for OpenAI/Gemini
**Rationale**:
- Core thesis requirement (comparative analysis)
- Future-proofs against provider changes
- Enables A/B testing different models
- Professional software architecture practice

**Implementation**:
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        pass

class OpenAIProvider(LLMProvider):
    # Implementation

class GeminiProvider(LLMProvider): 
    # Implementation
```

### 3. PostgreSQL + Redis Stack
**Decision**: PostgreSQL for data, Redis for caching
**Rationale**:
- PostgreSQL: Robust, ACID compliance, great for structured data
- Redis: Fast caching, session storage, pub/sub capabilities
- Both scale well and are production-proven
- Heroku/Fly.io support both

**Schema Design**:
- User accounts (post-thesis)
- Fact-check results and caching
- Usage analytics
- System configuration

### 4. Chrome Extension with WXT Framework
**Decision**: Use WXT framework with shadcn/ui and Tailwind CSS for Chrome extension
**Rationale**:
- Modern developer experience with excellent TypeScript support
- Hot module reloading and fast development iteration
- Built-in support for modern web standards and frameworks
- Superior tooling compared to Extension.js for thesis development
- shadcn/ui provides consistent, accessible UI components
- Tailwind CSS enables rapid, maintainable styling

**Architecture**:
- Background script for API communication
- Content script for webpage interaction
- Popup for results display with shadcn/ui components
- Context menu integration
- Tailwind CSS for responsive, professional styling

### 5. Context Menu Approach
**Decision**: Right-click fact-checking vs. automatic detection
**Rationale**:
- User control and consent
- Avoids false positives
- Better privacy (user chooses what to check)
- Simpler implementation than NLP text extraction

**User Flow**:
1. User highlights text
2. Right-clicks → "Fact-check with TruthLens"
3. Extension processes selected text
4. Results displayed in popup/sidebar

## API Design Decisions

### 1. RESTful API Architecture
**Endpoints**:
```
POST /api/v1/fact-check
GET /api/v1/fact-check/{id}
GET /api/v1/health
POST /api/v1/feedback (post-thesis)
```

### 2. Request/Response Format
**Request**:
```json
{
  "text": "Selected text to fact-check",
  "provider": "openai|gemini",
  "options": {
    "include_evidence": true,
    "max_claims": 5
  }
}
```

**Response**:
```json
{
  "id": "uuid",
  "claims": [
    {
      "text": "Extracted claim",
      "status": "supported|refuted|insufficient",
      "confidence": 0.85,
      "evidence": [
        {
          "source": "URL",
          "snippet": "Supporting text",
          "relevance": 0.9
        }
      ]
    }
  ],
  "processing_time": 4.2,
  "provider": "openai"
}
```

## Performance Optimization Decisions

### 1. Caching Strategy
**Decision**: Multi-level caching
- **L1**: Browser localStorage (24 hours)
- **L2**: Redis cache (7 days)
- **L3**: Database persistence (permanent)

**Cache Keys**: Hash of (text + provider + options)

### 2. Rate Limiting
**Thesis Period**: No rate limiting (development focus)
**Post-Thesis**: Redis-based rate limiting by IP/user

### 3. Background Processing
**Decision**: Synchronous processing during thesis
**Future**: Async with WebSocket updates for real-time feedback

## Security Decisions

### 1. API Key Management
**Current**: Environment variables
**Future**: Encrypted database storage, key rotation

### 2. Input Validation
**Decision**: Strict validation on all inputs
- Text length limits (1000 chars for thesis)
- HTML sanitization
- Rate limiting by IP
- Request size limits

### 3. Data Privacy
**Thesis**: Minimal logging, no user data storage
**Future**: GDPR-compliant data handling

## Development Workflow Decisions

### 1. Version Control Strategy
**Decision**: Git with conventional commits
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code improvements

### 2. Testing Strategy
**Current Focus**: E2E testing with Playwright MCP
**Post-Thesis**: Unit tests for core logic

### 3. Deployment Strategy
**Thesis**: Manual deployments to Fly.io
**Future**: CI/CD with GitHub Actions

## Technology Choices Rationale

### Python/LangGraph Backend
**Why**: 
- Already implemented in ClaimeAI
- Excellent AI/ML ecosystem
- LangGraph perfect for fact-checking workflows
- Fast development iteration

### TypeScript Frontend
**Why**:
- Type safety prevents runtime errors
- Better IDE support and refactoring
- Professional development standard
- Chrome extension best practices

### Fly.io Deployment
**Why**:
- Simple deployment from code
- Good free tier for development
- Scales easily
- PostgreSQL and Redis add-ons

## Future Architecture Evolution

### When to Split to Microservices
**Triggers**:
- >10,000 active users
- Team size >5 developers
- Need different scaling for components
- Complex deployment requirements

**Services to Extract First**:
1. User Management Service
2. Fact-checking Engine
3. Analytics Service
4. Notification Service

### Scaling Roadmap
**1,000 users**: Single server with caching
**10,000 users**: Load balancer + read replicas
**100,000 users**: Microservices + auto-scaling
**1M users**: Global CDN + edge computing

## Decision Log Template

For future decisions, document:
1. **Context**: What problem are we solving?
2. **Options**: What alternatives did we consider?
3. **Decision**: What did we choose and why?
4. **Consequences**: What are the trade-offs?
5. **Review Date**: When should we revisit this?

---

*Living document tracking all major technical decisions and their rationale*  
*Updated: 2025-09-14*