# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TruthLens is an AI-powered fact-checking Chrome extension with full transparency. It's built as a bachelor's thesis project for evaluating the effectiveness of different AI models in fact-checking tasks.

## Architecture

### Tech Stack
- **Backend**: Python with LangGraph framework for agent orchestration, FastAPI for API layer
- **Frontend**: Next.js 15 with TypeScript, shadcn/ui components, TailwindCSS 
- **Extension**: Extension.js framework for Chrome extension development
- **Database**: PostgreSQL (via Drizzle ORM) + Redis (via Upstash HTTP)
- **AI Models**: OpenAI GPT-4 and Google Gemini (thesis requirement for comparison)

### Core Components

1. **Agent System** (`apps/agent/`)
   - Three LangGraph agents working in pipeline:
     - `claim_extractor`: Breaks down text into verifiable claims
     - `claim_verifier`: Searches and verifies individual claims
     - `fact_checker`: Main orchestrator combining extraction and verification
   - Search abstraction layer supporting multiple providers (Brave, Tavily)
   - Redis caching for API responses

2. **Web Application** (`apps/web/`)
   - Next.js application with Hono API routes
   - Real-time streaming from LangGraph agents
   - Clerk authentication integration
   - Database operations via Drizzle ORM

3. **Chrome Extension** (`apps/extension/`)
   - Context menu integration for fact-checking selected text
   - Communication with backend via API

## Development Commands

### Setup
```bash
# Install all dependencies (pnpm + poetry)
pnpm setup:dev
```

### Development
```bash
# Full stack development (backend + frontend)
pnpm dev

# With extension development
pnpm dev:ext

# Backend only (LangGraph)
pnpm backend:dev

# Frontend only (Next.js)
pnpm frontend:dev
```

### Database
```bash
pnpm db:generate  # Generate Drizzle migrations
pnpm db:push      # Apply schema to database
pnpm db:studio    # Open Drizzle Studio GUI
```

### Code Quality
```bash
# Frontend
cd apps/web
pnpm lint         # Run ultracite linter
pnpm tc          # TypeScript type checking

# Backend
cd apps/agent
poetry run python -m pytest  # Run tests
```

### Extension
```bash
cd apps/extension
pnpm dev         # Development mode
pnpm build       # Build for production
```

## Environment Setup

Required environment variables:

### Backend (`apps/agent/.env`)
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `GOOGLE_API_KEY`: Google Gemini API key (thesis requirement)
- `BRAVE_API_KEY`: Brave Search API key
- `TAVILY_API_KEY`: Tavily Search API key (optional)
- `REDIS_URL`: Redis connection string

### Frontend (`apps/web/.env`)
- `LANGGRAPH_API_URL`: LangGraph server URL (default: http://localhost:2024)
- `DATABASE_URL`: PostgreSQL connection string
- `UPSTASH_REDIS_REST_URL`: Upstash Redis HTTP endpoint
- `UPSTASH_REDIS_REST_TOKEN`: Upstash Redis auth token
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Clerk public key
- `CLERK_SECRET_KEY`: Clerk secret key
- `OPENAI_API_KEY`: OpenAI API key for streaming

## Key Workflows

### Fact-Checking Pipeline
1. User selects text on webpage → triggers Chrome extension
2. Extension sends request to web API
3. Web API streams request to LangGraph agents
4. `fact_checker` agent orchestrates:
   - Claims extraction via `claim_extractor`
   - Parallel verification via `claim_verifier`
   - Report generation with evidence trails
5. Results streamed back to user in real-time

### Agent Communication
- LangGraph agents communicate via state management
- Each agent has defined nodes, prompts, and schemas
- Verification includes search query generation, evidence retrieval, and evaluation
- Full transparency with reasoning traces

## Important Files

- `apps/agent/langgraph.json`: LangGraph configuration defining available graphs
- `apps/agent/fact_checker/agent.py`: Main fact-checking orchestrator
- `apps/web/src/server/routes/agent.ts`: API endpoints for agent communication
- `apps/web/src/lib/langgraph.ts`: LangGraph client configuration
- `apps/extension/src/background.ts`: Extension background service worker

## Testing Approach

### Backend Testing
- Unit tests for individual agent nodes
- Integration tests for full pipelines
- Mock external API calls during tests

### Frontend Testing  
- Component testing with React Testing Library
- API route testing with Hono test client
- E2E testing considerations for extension

## Common Issues & Solutions

1. **LangGraph not starting**: Ensure Poetry environment is activated and dependencies installed
2. **Database connection issues**: Check PostgreSQL is running and DATABASE_URL is correct
3. **Redis connection**: For local dev, ensure Redis server is running or use Upstash HTTP proxy
4. **Extension not loading**: Run `pnpm build` in extension directory before loading unpacked

## Thesis Requirements Tracking

Key academic deliverables:
- Gemini API integration for model comparison
- Chrome extension with context menu integration  
- User study with 5-10 participants
- Comparative evaluation metrics (accuracy, speed, reasoning quality)
- 40-60 page thesis document

Current focus should maintain academic rigor while building production-ready system.