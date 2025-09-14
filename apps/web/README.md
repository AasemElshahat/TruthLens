# TruthLens Web Interface

Next.js web interface inherited from ClaimeAI and enhanced for TruthLens development. Currently functional with TypeScript, React, and integrated shadcn/ui components.

## 🏗️ Current Architecture (ClaimeAI Foundation)

**Frontend Stack (Currently Implemented):**
- **Next.js 15** with App Router and Turbopack
- **TypeScript** with strict mode for type safety
- **shadcn/ui** component library (already integrated)
- **Tailwind CSS** for styling and responsive design
- **Framer Motion** for animations and transitions
- **Clerk** for user authentication and management
- **tRPC** for type-safe API communication
- **Drizzle ORM** for database operations

**Current Features (Functional):**
- Basic fact-checking interface
- User authentication and session management
- Database integration with PostgreSQL
- Redis caching for performance
- Responsive design for desktop and mobile

**TruthLens Enhancements (Planned):**
- Real-time streaming updates during fact-checking
- Advanced sharing capabilities with privacy controls
- Enhanced UI/UX improvements
- Academic evaluation interfaces
- Performance analytics and monitoring

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- pnpm package manager
- PostgreSQL database (local or remote)
- Redis instance (local or Upstash)
- Environment variables configured

### Installation (Current Working Setup)

```bash
# From project root
cd apps/web

# Install dependencies
pnpm install

# Environment setup - Enhanced with PR #9 improvements
cp .env.example .env
# Edit .env with your configuration (see detailed guide below)

# Database setup - Now with local development fallback
pnpm db:push      # Apply schema to database (supports local development)
pnpm db:studio    # Optional: Open database studio

# Start development server
pnpm dev          # Runs on http://localhost:3000
```

Open [http://localhost:3000](http://localhost:3000) to access the TruthLens web interface.

## 🛠️ Development Scripts

```bash
# Development
pnpm dev              # Start development server with hot reload
pnpm build            # Build for production
pnpm start            # Start production server

# Code Quality
pnpm lint             # Run ESLint and code formatting
pnpm check-types      # TypeScript type checking
pnpm format           # Format code with Prettier

# Database
pnpm db:generate      # Generate new database migrations
pnpm db:push          # Push schema changes to database
pnpm db:studio        # Open Drizzle Studio for database management
```

## 📁 Project Structure

```
apps/web/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (dashboard)/     # Protected dashboard routes
│   │   ├── api/             # API routes and webhooks
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── ui/              # shadcn/ui components
│   │   └── ...              # Custom components
│   ├── lib/                 # Utilities and configurations
│   │   ├── db/              # Database schema and operations
│   │   ├── redis.ts         # Redis configuration
│   │   └── utils.ts         # Shared utilities
│   ├── server/              # Server-side logic
│   │   ├── routes/          # tRPC API routes
│   │   └── services/        # Business logic services
│   └── types/               # TypeScript type definitions
├── public/                  # Static assets
└── package.json            # Dependencies and scripts
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Database
DATABASE_URL="postgres://user:password@localhost:5432/truthlens"

# Redis (Upstash HTTP REST API)
UPSTASH_REDIS_REST_URL="http://localhost:8080"
UPSTASH_REDIS_REST_TOKEN="local_dev_token"

# Authentication (Clerk)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_..."
CLERK_SECRET_KEY="sk_test_..."
CLERK_WEBHOOK_SECRET="whsec_..."

# AI Services
OPENAI_API_KEY="sk-proj-..."
LANGGRAPH_API_URL="http://localhost:2024"

# App Configuration
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### Database Schema

The application uses Drizzle ORM with PostgreSQL. Key tables:
- `users` - User accounts and profiles
- `texts` - Submitted content for fact-checking
- `checks` - Fact-checking operations and results

### Real-time Architecture

TruthLens web interface implements real-time streaming for fact-checking results:

1. **User submits text** → Creates check record in database
2. **Background processing** → LangGraph agent processes claims
3. **Real-time updates** → Redis streams update results to frontend
4. **Live UI updates** → Users see progress and results in real-time

## 🎨 UI Components

Built with shadcn/ui component library for consistency:
- Form components with validation
- Loading states and skeletons
- Toast notifications
- Modal dialogs and sheets
- Responsive navigation
- Data visualization components

## 🚀 Deployment

### Production Build
```bash
pnpm build
pnpm start
```

### Vercel Deployment
This application is optimized for Vercel deployment:
- Automatic deployments from Git
- Edge function compatibility
- Built-in performance monitoring
- Global CDN distribution

## 📖 Related Documentation

- [Project Documentation](../../docs/README.md) - Complete project overview
- [Technical Approach](../../CLAUDE.md) - Development methodology
- [Product Vision](../../docs/strategy/project-vision.md) - Project vision and goals
- [Backend Agent](../agent/README.md) - Fact-checking backend documentation

## 🤝 Contributing

This web interface is part of the TruthLens thesis project. For development guidelines:
1. Follow TypeScript strict mode
2. Use shadcn/ui components where possible  
3. Implement proper error boundaries
4. Maintain responsive design
5. Write comprehensive tests

---

**Built with Next.js for TruthLens - Academic rigor, production scale** 🎓⚡️
