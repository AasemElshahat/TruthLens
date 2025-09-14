# TruthLens - Thesis + Future Product Development

## Mission
Build a polished AI fact-checking Chrome extension for my bachelor's thesis, with production-ready architecture for future commercialization.

## Current Sprint: Gemini Integration Research (Week 1)
**Focus**: Understand Gemini API requirements and plan LLM abstraction layer

### This Week's Goals
- [ ] Research Gemini API capabilities and limitations
- [ ] Design LLM abstraction layer architecture
- [ ] Test Gemini API integration with existing prompts
- [ ] Document comparison framework (Gemini vs OpenAI)

## Thesis Requirements (Due Jan 2026)
**Core Deliverables**:
- [x] ClaimeAI backend foundation ✅
- [ ] Gemini API integration alongside OpenAI
- [ ] Chrome extension with context menu functionality
- [ ] Professional UI/UX for fact-checking results
- [ ] Comparative evaluation (Gemini vs OpenAI)
- [ ] User study with 5-10 participants
- [ ] 40-60 page thesis document

**Academic Success Metrics**:
- Extension works on 90% of tested websites
- Average response time <10 seconds
- Clear evidence transparency features
- Documented methodology and evaluation

## Tech Stack
**Current**:
- Backend: Python/LangGraph (from ClaimeAI)
- Search: Brave Search, Tavily, Exa APIs
- Database: PostgreSQL + Redis
- LLM: OpenAI GPT-4

**Adding for Thesis**:
- Gemini API integration
- Chrome extension (TypeScript/WXT framework, shadcn/ui, Tailwind CSS)
- Comparative evaluation framework

**Future Commercial Features** (Post-Thesis):
- Stripe payment integration
- User authentication with Clerk
- Usage tracking and analytics
- Team accounts and billing

## Architecture (Built for Scale)
- Modular backend with clean API boundaries
- LLM abstraction layer (easy provider switching)
- PostgreSQL with proper indexes
- Environment-based configuration
- Professional TypeScript frontend

## Quick Commands
```bash
# Development
pnpm dev              # Start full dev environment  
pnpm backend:dev      # Backend only
pnpm frontend:dev     # Web interface only
pnpm dev:ext          # Include extension development

# Database
pnpm db:generate      # Generate migrations
pnpm db:push          # Apply schema changes
pnpm db:studio        # Database GUI

# Testing
cd apps/agent && python -m pytest    # Backend tests
cd apps/extension && pnpm test       # Extension tests
```

## Current Development Status
**Infrastructure**: ✅ Production-ready foundation established
- Database operations with error handling
- Redis HTTP REST API configuration  
- Authentication system ready
- Local development environment functional

**Next Priorities**:
1. Gemini API integration and testing
2. LLM abstraction layer implementation
3. Chrome extension context menu development
4. Results display UI/UX design

## Key Architectural Decisions
- **Monolithic backend** (can split later, but keep simple for thesis)
- **Multi-LLM support** (core thesis requirement)
- **Context menu approach** (better UX than URL input)
- **Transparency-first** (show all evidence and reasoning)
- **Academic documentation** (every decision justified)

## Weekly Focus Areas
**Week 1 (Current)**: Gemini integration research and planning  
**Week 2**: LLM abstraction layer implementation  
**Week 3**: Chrome extension context menu functionality  
**Week 4**: Results display and evidence transparency  

## Environment Setup
Copy environment examples and add your API keys:
- `apps/agent/.env` - Backend configuration
- `apps/web/.env.local` - Frontend configuration

Required API keys:
- OpenAI API key (existing)
- Google Gemini API key (to add)
- Brave Search API key (existing)
- Tavily API key (optional, backup search)

## How We Build Features

### Our Development Philosophy
- **YAGNI** (You Aren't Gonna Need It) - Build only what the thesis requires
- **Ship Fast, Refactor Later** - Working code > perfect code
- **Integration Tests Only** - Test user workflows, not implementation details
- **Document Decisions** - Every "why" in TECHNICAL_DECISIONS.md

### Feature Workflow
1. **Define user story**: "As a user, I want to..."
2. **Create integration test** with Playwright MCP
3. **Build minimum viable implementation**
4. **Test manually in browser**
5. **Ship when it works**

### Testing Strategy (Thesis-Focused)
**Use Integration Tests**:
- Right-click → fact-check → results workflow
- Gemini vs OpenAI API responses
- Error handling (network failures, invalid text)

**Use Playwright MCP for browser testing**:
```bash
mcp__playwright__browser_navigate "test-site.com"  
mcp__playwright__browser_click "text selection"
mcp__playwright__browser_take_screenshot
```

**Skip for thesis phase**:
- Unit tests (change too often during exploration)
- Performance tests (not relevant for prototype)
- Complex edge cases (focus on 90% scenarios)

## Documentation Imports
- @docs/DEVELOPMENT_WORKFLOW.md - Complete development process
- @docs/THESIS_REQUIREMENTS.md - Detailed academic requirements
- @docs/CURRENT_SPRINT.md - Weekly task breakdown
- @docs/POST_THESIS_FEATURES.md - Commercial features for later
- @docs/TECHNICAL_DECISIONS.md - Architecture rationale

---

*Last updated: 2025-09-14*  
*Current milestone: Gemini integration research phase*  
*Development approach: Simple, focused, ship-when-it-works*