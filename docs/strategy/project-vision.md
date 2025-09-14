# TruthLens - Project Vision Document

**Version:** 3.0  
**Date:** September 14, 2025  
**Status:** Active Development  
**Author:** Aasem Elshahat

---

## Executive Summary

### Product Name: TruthLens

### One-Line Vision:
*"Making truth verification as simple as spell-check, and as transparent as glass."*

### Mission Statement:
We're building the world's most transparent and trustworthy fact-checking tool that empowers users to instantly verify claims in any online content, showing not just what's true or false, but exactly WHY and HOW we know it.

---

## Problem Statement

### The Problem We're Solving:
- **60-80% of adults** regularly encounter false information online (Multiple studies, 2024-2025)
- Current fact-checking is slow, opaque, and disconnected from browsing
- Users must leave their reading flow to verify claims manually
- Existing tools provide verdicts without transparent reasoning
- No tool adequately explains HOW it reached its conclusions

### Why Now:
- AI advancement makes real-time checking feasible
- Browser extension adoption at all-time high
- Growing distrust requires transparent solutions
- Academic research (Claimify + SAFE) provides proven methodology

---

## Target Users & Personas

### Primary Persona: "Informed Isabella"
- **Role:** Journalist/Researcher/Student
- **Age:** 25-45
- **Needs:** Verify sources quickly, cite credible information
- **Pain Points:** Time-consuming manual fact-checking
- **Value Prop:** Save 2+ hours daily on verification

### Secondary Persona: "Cautious Carlos"
- **Role:** Everyday internet user
- **Age:** 30-60
- **Needs:** Know if shared content is reliable
- **Pain Points:** Embarrassment from sharing false info
- **Value Prop:** Confidence in what they read and share

### Tertiary Persona: "Enterprise Emma"
- **Role:** Corporate communications/PR
- **Needs:** Verify claims before publishing
- **Pain Points:** Reputational risk from false claims
- **Value Prop:** Protect brand credibility

---

## Core Value Propositions

### Our Unique Value: The 3 T's
1. **🎯 Truth** - Research-backed methodology (Claimify + SAFE)
2. **🔍 Transparency** - Show sources, queries, and reasoning
3. **⚡ Time** - Instant verification without leaving the page

### Key Differentiators:

| Feature | Us | Competitors |
|---------|----|-----------| 
| Shows reasoning | ✅ Full transparency | ❌ Black box |
| Research-based | ✅ Academic methods | ❌ Proprietary |
| Browser integration | ✅ Native experience | ⚠️ Separate sites |
| Multi-LLM support | ✅ Provider choice | ❌ Single model |
| Real-time checking | ✅ Instant | ⚠️ Delayed |

---

## Product Principles

These principles guide every product decision:

1. **Transparency First** - Never hide our reasoning
2. **User Empowerment** - Give users control and choice
3. **Academic Rigor** - Build on proven research
4. **Speed Without Sacrifice** - Fast but thorough
5. **Accessible Complexity** - Powerful yet simple
6. **Privacy Respected** - Minimal data collection
7. **Quality Over Speed** - No technical compromises
8. **Sustainable Architecture** - Built for multi-million user scale

---

## Success Metrics (KPIs)

### Thesis Phase Goals (Oct 2025 - Jan 2026):
- **Functionality:** Working Chrome extension with core features
- **Evaluation:** Comparative analysis (Gemini vs OpenAI)
- **User Testing:** 5-10 participant study completed
- **Academic:** Thesis defense passed with distinction

### Year 1 Goals (2026):
- **Users:** 10,000 active users
- **Checks:** 1M+ facts checked
- **Accuracy:** 90%+ verification accuracy
- **Revenue:** $50K ARR
- **Net Promoter Score (NPS):** 50+

### North Star Metric:
**"Verified Claims per Active User per Week"** - Target: 20+

### Supporting Metrics:
- Average verification time: <3 seconds
- User trust score: 8+/10
- Monthly retention: 40%+
- Paid conversion: 2-3%

---

## Technical Architecture Philosophy

### Non-Negotiable Technical Standards:
- **Microservices from start**: Fact-checker, user management, billing separate
- **Database design**: Proper indexing, migrations, backup strategies
- **API design**: RESTful, versioned, rate-limited, documented
- **Code quality**: TypeScript strict mode, comprehensive tests, CI/CD
- **Security first**: Authentication, authorization, input validation
- **Monitoring**: Logging, metrics, error tracking from day one

### Scalability Planning:
- Queue systems for processing (Redis/BullMQ)
- Caching layers (Redis)
- CDN for static assets
- Load balancer ready
- Database sharding strategy
- Horizontal scaling architecture

### Development Approach:
- **Claude Code Direct Partnership**: Direct development with Claude Code as technical co-founder
- **Academic Rigor**: University-validated methodology and evaluation
- **Production Quality**: Professional architecture designed for future scaling
- **Transparent Process**: Every technical decision documented and justified

---

## MVP Definition & Constraints

### Thesis MVP Scope (Oct 2025 - Jan 2026)

#### MUST Have Features (Required for Thesis):
✅ **Core Functionality**
- Claimify-based claim extraction pipeline
- SAFE-inspired evidence retrieval
- Multi-LLM support (OpenAI + Gemini)
- Web search integration (Tavily/Exa)

✅ **Chrome Extension**
- Right-click context menu integration
- URL input capability
- Extension popup UI (400x600px)
- Real-time processing feedback
- Results display with verification status

✅ **Transparency Features**
- "Show Evidence" expandable section
- Display source URLs
- Show search queries used
- Explain reasoning process

✅ **Academic Requirements**
- Quantitative evaluation capability
- Performance metrics logging
- Comparative analysis (Gemini vs OpenAI)
- User study infrastructure

#### Technical Success Criteria:
- [ ] Successfully extracts claims from text (>80% accuracy)
- [ ] Retrieves relevant evidence via web search
- [ ] Provides verification verdict with reasoning
- [ ] Shows transparent evidence trail
- [ ] Works on any webpage via Chrome extension
- [ ] Average response time <10 seconds
- [ ] Extension size <10MB
- [ ] Works on 90% of websites tested
- [ ] Handles text selections up to 500 words

#### Academic Success Criteria:
- [ ] Comparative analysis completed (Gemini vs OpenAI)
- [ ] User study with 5-10 participants
- [ ] Quantitative evaluation on test dataset
- [ ] Documentation of methodology
- [ ] Thesis paper 40-60 pages

---

## Core User Journey & Functionality

### Primary User Flow: Text Selection
1. User reads any article/webpage
   ↓
2. Highlights suspicious text/claim
   ↓
3. Right-clicks → Selects "Fact-check with TruthLens"
   ↓
4. Extension panel opens with analysis in progress
   ↓
5. Results show IN the extension UI:
   - Verification status (Supported/Refuted/Unverified)
   - Confidence score
   - "Show Evidence" expandable section
   ↓
6. User clicks "Show Evidence" to see:
   - Exact sources used
   - Search queries performed
   - AI reasoning process
   ↓
7. User can save, share, or dismiss results

### Key UX Principles:
- **No redirects** - Everything happens in the extension
- **Non-intrusive** - Overlay/sidebar, never blocking content
- **Context-aware** - Highlights checked text on the page
- **Persistent** - Results stay accessible during session
- **Shareable** - Generate link to verification results

---

## Competitive Positioning

**We are the "Grammarly of fact-checking"**

- **Like Grammarly:** Seamless, in-context, trusted
- **Unlike Snopes:** Real-time, transparent, integrated
- **Unlike ChatGPT:** Specialized, sourced, verifiable
- **Unlike Google:** Focused, academic, explanatory

### Our Competitive Moats:
1. **Research Foundation** - Built on published academic methods (Claimify + SAFE)
2. **Radical Transparency** - No other tool shows full reasoning chain
3. **Browser Integration** - Seamless workflow vs separate sites
4. **Multi-LLM Support** - User choice, no vendor lock-in
5. **Speed + Accuracy** - Real-time checking with academic rigor
6. **Technical Excellence** - No compromises architecture from day one
7. **Academic Credibility** - University thesis validation

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **API costs exceed revenue** | High | Implement caching, rate limits, free tiers |
| **Google blocks extension** | Critical | Follow all Chrome policies strictly |
| **Users don't trust AI** | High | Radical transparency, academic backing |
| **Technical debt accumulates** | Critical | No compromises policy, continuous refactoring |
| **Scaling challenges** | Medium | Architecture designed for scale from start |

---

## Definition of Success

### Short Term (Thesis Completion - Jan 2026):
- ✅ Successful thesis defense
- ✅ Working Chrome extension with all core features
- ✅ Academic validation of methodology
- ✅ User study results showing positive reception

### Medium Term (6 months - July 2026):
- ✅ 1,000+ active users
- ✅ Featured in Chrome Web Store
- ✅ First paying customers
- ✅ Technical architecture proven at scale

### Long Term (2-3 years - By 2028):
- 🚀 $1M+ ARR
- 🌍 100K+ active users
- 💼 Acquisition offers
- 🎯 Industry standard for fact-checking

---

## Guiding Questions

Before any major decision, ask:

1. Does this increase transparency?
2. Does this make fact-checking easier?
3. Does this build user trust?
4. Can we deliver this with excellence?
5. Does this align with our academic foundation?
6. Will this scale to millions of users?
7. Does this maintain our technical standards?

If the answer to any is "no," reconsider.

---

## Academic Foundation

**Built on proven research:**
- **Claimify Methodology** (Metropolitansky & Larson, 2025)
- **SAFE Framework** (Wei et al., 2024)

**Our contribution:**
- Multi-LLM comparative analysis
- Real-time browser integration
- Transparent reasoning display
- User experience optimization

---

*"In a world drowning in information, we're building the life raft of truth."*

**Document maintained by:** Aasem Elshahat  
**Last updated:** September 14, 2025  
**Current Development Status:** Thesis-focused development with production-ready foundation  
**Next review:** October 2025