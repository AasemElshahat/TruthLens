# TruthLens

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AI-Powered Fact-Checking System with Full Transparency**

TruthLens is a comprehensive fact-checking system that breaks down text into verifiable claims, cross-references them with web evidence, and generates detailed accuracy reports with complete transparency. Built as a bachelor's thesis project at Berliner Hochschule für Technik, it's designed to be production-ready Chrome extension serving millions of users.

**Academic Foundation**: Technical implementation for bachelor's thesis research  
**Business Vision**: Bootstrap sustainable fact-checking service with multi-million dollar potential

## 🏗️ Architecture Overview

### Current Implementation (Inherited from ClaimeAI)
TruthLens builds upon the existing ClaimeAI foundation with these components:

**Core Components:**
- **`apps/agent/`** - Python/LangGraph fact-checking backend (fully functional)
  - **[Claim Extractor](./apps/agent/claim_extractor/README.md)** - Extracts factual claims using Claimify methodology
  - **[Claim Verifier](./apps/agent/claim_verifier/README.md)** - Verifies claims against web evidence via Tavily Search  
  - **[Fact Checker](./apps/agent/fact_checker/README.md)** - Orchestrates workflow and generates reports
- **`apps/web/`** - Next.js web interface with existing shadcn/ui components
- **`apps/extension/`** - Basic Chrome extension using Extension.js framework

**Current Technology Stack:**
- **Backend**: Python, LangGraph, FastAPI
- **Frontend**: TypeScript, Next.js, React, shadcn/ui (already integrated)
- **Extension**: Extension.js framework
- **Database**: PostgreSQL with Drizzle ORM
- **Caching**: Redis with Upstash HTTP REST API
- **Authentication**: Clerk
- **Hosting**: Fly.io (backend), Vercel (web), Chrome Web Store (extension)

### Planned TruthLens Development (Our Contributions)
**Current Status**: Infrastructure preparation and team setup phase (Week 2 of 4-week plan)

**Planned Enhancements:**
- **Extension Migration**: Extension.js → **WXT framework** for modern Chrome extension development
- **Enhanced Features**: Real-time streaming, improved UI/UX, advanced sharing capabilities
- **Academic Integration**: Comparative analysis framework (OpenAI vs Gemini implementations)
- **Production Scaling**: Architecture designed for multi-million user scale
- **Chrome Extension**: Complete rebuild with WXT for better development experience
- **Advanced Analytics**: User behavior tracking and performance metrics

## 🎯 Why TruthLens?

In an era where misinformation spreads faster than truth, we need transparent, real-time fact-checking that shows not just what's true or false, but **exactly HOW we know it**.

## 🔄 How It Works

1. **Text Input** - Submit any text through web interface or Chrome extension
2. **Claim Extraction** - AI breaks down text into specific, testable factual claims
3. **Evidence Gathering** - Each claim is verified against real-world web evidence
4. **Transparent Reporting** - Get detailed results showing not just true/false, but the reasoning and sources behind each determination

## 🚀 Quick Start (Current ClaimeAI Infrastructure)

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+ with Poetry  
- PostgreSQL database
- Redis instance
- OpenAI API key
- Clerk authentication setup

### Development Setup

```bash
# Clone repository
git clone https://github.com/AasemElshahat/TruthLens.git
cd TruthLens

# Install dependencies
pnpm install
cd apps/agent && poetry install

# Environment setup - Use our enhanced templates
cp apps/web/.env.example apps/web/.env
cp apps/agent/.env.example apps/agent/.env
# Edit .env files with your API keys (see detailed docs below)

# Database setup - Now with improved error handling (PR #9)
cd apps/web
pnpm db:push      # Works with local development fallback
pnpm db:studio    # Optional: view database

# Start development servers
pnpm dev          # Web interface (http://localhost:3000)
cd apps/agent && poetry run python main.py  # Backend agent

# Extension development (Extension.js - current framework)
cd apps/extension
pnpm dev          # Chrome extension development
```

**Note**: This runs the current working ClaimeAI infrastructure. Our TruthLens enhancements will be built on top of this foundation during the development phase.

## 📖 Documentation

- **[Project Documentation](./docs/README.md)** - Complete documentation index
- **[Project Vision](./docs/strategy/project-vision.md)** - Product vision and user personas
- **[Product Roadmap](./docs/strategy/product-roadmap.md)** - Bootstrap strategy and development timeline
- **[Technical Approach](./CLAUDE.md)** - Development methodology and team coordination
- **Component READMEs**: [Agent](./apps/agent/README.md) | [Web](./apps/web/README.md) | [Extension](./apps/extension/README.md)

## 🎓 Academic Foundation

**Thesis Context**: Bachelor's thesis at Berliner Hochschule für Technik  
**Research Focus**: Comparative analysis of LLM providers (OpenAI vs Gemini) for fact-checking  
**Methodology**: Based on proven academic research (Claimify + SAFE methodologies)  
**Timeline**: October 2025 - January 2026

### Research Components:
- Quantitative evaluation on curated test datasets
- User study with 5-10 participants  
- Performance benchmarking and optimization analysis
- Comparative LLM provider analysis

Each component offers extensive configuration options in their respective `config/` directories:

- **LLM Settings**: Temperature, model selection, retry attempts
- **Search Configuration**: Number of results, result filtering, source weighting
- **Performance Tuning**: Caching strategies, rate limiting, timeout handling
- **UI Customization**: Real-time streaming, result display, sharing options

See individual component READMEs for detailed configuration guides.

## 📚 Research Foundation

**Claimify Methodology**: Claim extraction based on Metropolitansky & Larson's 2025 research  
**SAFE Integration**: Evidence retrieval inspired by Wei et al.'s Search-Augmented Factuality Evaluator  
**Academic Rigor**: All implementations follow peer-reviewed methodologies with proper citations

## 🤝 Contributing

This is a thesis project with specific academic requirements, but feedback and suggestions are welcome:

1. **Issues**: Report bugs or suggest features via GitHub Issues
2. **Documentation**: Help improve documentation clarity
3. **Testing**: Contribute test cases or performance benchmarks

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with academic rigor, designed for production scale** 🎓⚡️
