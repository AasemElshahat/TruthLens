# TruthLens

**AI-Powered Fact-Checking Chrome Extension with Full Transparency**

TruthLens is a Chrome extension that instantly fact-checks selected text on any webpage, showing not just what's true or false, but exactly how and why. Built as a bachelor's thesis project at Berliner Hochschule für Technik.

## Quick Start

```bash
# Install dependencies
pnpm setup:dev

# Start development
pnpm dev

# Start with extension development
pnpm dev:ext
```

## What It Does

1. **Select text** on any webpage
2. **Right-click** → "Fact-check with TruthLens"  
3. **Get instant verification** with full evidence trail
4. **See the reasoning** - sources, queries, and AI logic

## Tech Stack

- **Backend**: Python, LangGraph, FastAPI
- **Frontend**: Next.js, TypeScript, shadcn/ui
- **Extension**: Extension.js framework
- **Database**: PostgreSQL + Redis
- **AI**: OpenAI GPT-4 + Google Gemini (thesis requirement)

## Thesis Requirements

**Academic Deliverables (Due January 2026)**:
- [x] ClaimeAI foundation ✅
- [ ] Gemini API integration for comparison
- [ ] Chrome extension with context menu
- [ ] User study with 5-10 participants
- [ ] Comparative evaluation (Gemini vs OpenAI)
- [ ] 40-60 page thesis document

## Project Structure

```
TruthLens/
├── apps/
│   ├── agent/        # Python fact-checking backend
│   ├── extension/    # Chrome extension
│   └── web/          # Next.js web interface
├── docs/            # Project documentation
└── .claude/         # Claude Code commands
```

## Development Commands

```bash
# Backend only
pnpm backend:dev

# Frontend only
pnpm frontend:dev

# Database operations
pnpm db:generate    # Generate migrations
pnpm db:push        # Apply schema changes
pnpm db:studio      # Database GUI

# Testing
cd apps/agent && python -m pytest    # Backend tests
cd apps/extension && pnpm test       # Extension tests
```

## Environment Setup

Copy `.env.example` files and add your API keys:

**Required APIs**:
- OpenAI API key
- Google Gemini API key (thesis requirement)
- Brave Search API key

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide and current sprint
- **[docs/THESIS_REQUIREMENTS.md](docs/THESIS_REQUIREMENTS.md)** - Academic requirements
- **[docs/CURRENT_SPRINT.md](docs/CURRENT_SPRINT.md)** - This week's tasks

## License

MIT License - See LICENSE file for details.

---

*Building transparent, trustworthy fact-checking for the AI age* 🎯