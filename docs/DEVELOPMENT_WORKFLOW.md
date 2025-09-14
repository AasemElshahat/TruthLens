# Development Workflow

## Our Development Philosophy

### YAGNI (You Aren't Gonna Need It)
- Build only what the thesis requires
- Skip features that "might be useful later"
- Focus on working prototype, not perfect architecture

### Ship Fast, Refactor Later
- Working code > perfect code
- Get user feedback quickly
- Optimize when you have real performance issues

### Document Decisions
- Every "why" goes in `TECHNICAL_DECISIONS.md`
- Future you will thank present you
- Academic thesis requires clear rationale

## Feature Development Process

### 1. Write User Story
```
As a [user type], I want to [goal] so that [reason]

Example:
As a journalism student, I want to right-click and fact-check selected text 
so that I can verify claims while reading articles.
```

### 2. Create Integration Test
Use Playwright MCP to test the full user workflow:
```bash
mcp__playwright__browser_navigate "https://example-news-site.com"
mcp__playwright__browser_click "Select text"
mcp__playwright__browser_click "Right-click context menu"
mcp__playwright__browser_take_screenshot
```

### 3. Implement Feature
- Start with simplest possible implementation
- Make it work, then make it clean
- Use existing patterns from ClaimeAI codebase

### 4. Test Manually
- Test in real browser with real websites
- Use different text selections and website types
- Capture screenshots of success/failure cases

### 5. Ship When It Works
- Don't wait for perfection
- Ship working prototype
- Gather feedback and iterate

## Testing Strategy (Thesis-Focused)

### What We Test ✅
- **User Workflows**: Right-click → fact-check → results display
- **API Integration**: Gemini vs OpenAI responses  
- **Error Handling**: Network failures, invalid inputs
- **Browser Compatibility**: Chrome extension works correctly

### What We Skip (For Now) ❌
- **Unit Tests**: Change too often during exploration
- **Performance Tests**: Not relevant for thesis prototype
- **Edge Cases**: Focus on 90% of user scenarios

### Testing Tools

#### Playwright MCP (Primary)
```bash
# Navigate and interact
mcp__playwright__browser_navigate "URL"
mcp__playwright__browser_click "element"
mcp__playwright__browser_type "text input"

# Capture evidence
mcp__playwright__browser_take_screenshot
mcp__playwright__browser_snapshot
```

#### Context7 MCP (API Documentation)
```bash
# Verify API documentation is current
mcp__context7__resolve-library-id "openai"
mcp__context7__get-library-docs "/google/generative-ai-python"
```

#### Manual Testing Checklist
- [ ] Extension loads in Chrome
- [ ] Context menu appears on text selection
- [ ] Both OpenAI and Gemini providers work
- [ ] Results display with evidence sources
- [ ] Error messages are user-friendly
- [ ] Works on at least 5 different websites

## Code Standards

### Python Backend
```python
# Type hints required
def fact_check_claim(text: str, provider: str) -> FactCheckResult:
    """Check factual claim using specified LLM provider.
    
    Args:
        text: The claim text to verify
        provider: Either 'openai' or 'gemini'
    
    Returns:
        FactCheckResult with status and evidence
    """
    pass

# Use existing ClaimeAI patterns
from utils.llm import get_llm_provider
from schemas import FactCheckResult
```

### TypeScript Frontend/Extension (WXT Framework)
```typescript
// Built with WXT framework + shadcn/ui + Tailwind CSS
// Strict mode enabled in tsconfig.json
interface FactCheckRequest {
  text: string;
  provider: 'openai' | 'gemini';
}

// Use shadcn/ui components for consistent UI
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

// Tailwind classes for styling
const popupClass = "w-96 max-h-96 bg-background border shadow-lg";
```

### Git Commits
- `feat: add Gemini API integration`
- `fix: handle network timeout errors`  
- `docs: update thesis requirements`
- `refactor: simplify LLM abstraction`

## Development Environment

### Daily Startup
```bash
# Start development environment
pnpm dev

# Or with extension development
pnpm dev:ext

# Check everything works
curl http://localhost:8000/api/health
```

### Environment Variables
Keep these updated in your `.env` files:
- `OPENAI_API_KEY` - Required for baseline
- `GOOGLE_API_KEY` - Required for thesis comparison
- `BRAVE_API_KEY` - Required for evidence search

### Database Operations
```bash
# Generate migrations after schema changes
pnpm db:generate

# Apply to development database
pnpm db:push

# Open database GUI for debugging
pnpm db:studio
```

## Debugging Workflow

### Backend Issues
1. Check logs: `fly logs` or local console
2. Test API directly: `curl -X POST http://localhost:8000/api/v1/fact-check`
3. Check environment variables loaded
4. Verify API keys work

### Extension Issues
1. Open Chrome DevTools → Extensions
2. Check console for errors
3. Verify content script injection
4. Test context menu registration

### Database Issues
1. Check connection: `pnpm db:studio`
2. Verify migrations applied: `pnpm db:push`
3. Check data exists: Query directly in studio

## When to Refactor

### Refactor When:
- Same code copy-pasted 3+ times
- Function longer than 30 lines
- Adding new feature is painful
- Tests are hard to write

### Don't Refactor When:
- Code works and thesis deadline approaches
- Uncertain about requirements
- Only used in one place
- Performance is adequate

## Thesis-Specific Considerations

### Documentation Requirements
- Every major technical decision needs rationale
- Keep screenshots of working features
- Document comparison methodology (Gemini vs OpenAI)
- Track user study feedback

### Academic Integrity
- Credit ClaimeAI foundation properly
- Document your original contributions clearly
- Keep development process transparent
- Save evidence of working system

---

*Simple, practical development workflow focused on thesis success* 🎯