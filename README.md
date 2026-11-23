# VoiceAI - AI Voice Calling Automation Platform

A production-ready AI-powered voice calling automation platform that automatically calls customers, communicates naturally using AI, understands responses, stores recordings/transcripts, updates Google Sheets, and manages complete customer follow-up workflows.

## 🚀 Features

### Core Capabilities
- **AI Voice Agent**: Natural conversations in English, Hindi, and Hinglish using OpenAI Realtime API
- **FREE TTS Voice Synthesis**: Zero-cost text-to-speech using Piper, Coqui, eSpeak NG, or System TTS
- **Automated Call Queue**: Process customers sequentially with configurable concurrency, delays, and calling hours
- **Smart Campaign Management**: Multiple campaigns with custom AI instructions, scripts, and knowledge bases
- **Real-time Transcription**: Live speech-to-text with Whisper integration
- **Call Recording**: Automatic recording with secure storage and Google Drive sync
- **Google Sheets Integration**: Real-time bidirectional sync with configurable column mapping
- **Callback Automation**: Schedule and manage callbacks based on customer requests
- **Lead Scoring**: AI-powered interest classification (HOT/WARM/COLD/UNKNOWN)
- **Suppression Management**: Do-not-call lists with DND/opt-out compliance

### Dashboard & Analytics
- Real-time campaign monitoring
- Comprehensive analytics (daily/weekly/monthly)
- Call success rates, answer rates, conversion metrics
- Exportable reports (CSV/Excel)

### Compliance & Security
- TRAI/DND compliance for Indian market
- Consent tracking and management
- Encrypted credential storage
- Role-based access control (RBAC)
- Audit logging for all actions

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   API Gateway   │────▶│   PostgreSQL    │
│   (Next.js)     │     │   (FastAPI)     │     │   (Primary DB)  │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Redis   │ │  Celery  │ │  Twilio  │
              │ (Cache/  │ │ Workers  │ │ (Voice)  │
              │  Queue)  │ │          │ │          │
              └──────────┘ └──────────┘ └──────────┘
                    │            │            │
                    ▼            ▼            ▼
              ┌─────────────────────────────────────┐
              │     External Integrations           │
              │  OpenAI │ Google Sheets │ Google    │
              │  (AI Logic)│   & Drive    │  Drive  │
              │  Free TTS  │               │         │
              │  (Piper/   │               │         │
              │  Coqui/    │               │         │
              │  eSpeak)   │               │         │
              └─────────────────────────────────────┘
```

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic 2 |
| Database | PostgreSQL 16 (asyncpg), Redis 7 |
| Queue | Celery with Redis broker |
| Voice | Twilio Voice, **Free TTS (Piper/Coqui/eSpeak/System)** |
| AI | OpenAI GPT-4o (Logic only), **Free TTS Engines** |
| Integrations | Google Sheets API, Google Drive API, n8n |
| Deployment | Docker, Docker Compose, Nginx |

## 🎯 Free TTS Engines (Zero Cost!)

| Engine | Quality | Speed | Languages | Best For |
|--------|---------|-------|-----------|----------|
| **Piper TTS** ⭐ | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | 50+ | **Recommended** - Best balance |
| **Coqui TTS** | ⭐⭐⭐⭐⭐ | ⚡⚡ | 100+ | Voice cloning, multi-lingual |
| **eSpeak NG** | ⭐⭐⭐ | ⚡⚡⚡⚡ | 100+ | Lightweight, many languages |
| **System TTS** | ⭐⭐⭐ | ⚡⚡ | OS dependent | No install needed |

**Cost Comparison:**
- OpenAI TTS: ~$15/1M characters
- **Free TTS: $0** (runs locally)

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 22+ (for local frontend development)
- Python 3.12+ (for local backend development)
- Twilio Account (for voice calling)
- OpenAI API Key (for AI agent logic only)
- Google Cloud Project (for Sheets/Drive integration)

### 1. Clone and Configure
```bash
git clone https://github.com/Angrajkarn/voice-ai.git
cd voice-ai
cp .env.example .env
# Edit .env with your credentials
```

### 2. Choose Your Free TTS Engine

**Option A: Piper TTS (Recommended - Best Quality/Speed)**
```bash
# In .env
FREE_TTS_ENGINE=piper
# No additional install needed - auto-downloads models
```

**Option B: Coqui TTS (Voice Cloning, Multi-lingual)**
```bash
# In .env
FREE_TTS_ENGINE=coqui
# Install: pip install TTS torch torchaudio
```

**Option C: eSpeak NG (Lightweight, 100+ languages)**
```bash
# In .env
FREE_TTS_ENGINE=espeak
# Install: apt-get install espeak-ng (Linux) / brew install espeak-ng (macOS)
```

**Option D: System TTS (No install, uses OS built-in)**
```bash
# In .env
FREE_TTS_ENGINE=system
# macOS: say command | Windows: SAPI | Linux: festival/spd-say
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access Applications
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

### 5. Initialize Database
```bash
# Run migrations (first time)
docker-compose exec api alembic upgrade head

# Seed demo data
docker-compose exec api python -m prisma db seed
```

## 📁 Project Structure

```
voiceai/
├── apps/
│   ├── web/                 # Next.js Frontend
│   │   ├── src/
│   │   │   ├── app/         # App Router pages
│   │   │   ├── components/  # React components
│   │   │   ├── lib/         # Utilities & API client
│   │   │   └── hooks/       # Custom React hooks
│   │   └── package.json
│   │
│   └── api/                 # FastAPI Backend
│       ├── app/
│       │   ├── api/v1/      # API routes
│       │   ├── core/        # Config, security, Celery
│       │   ├── db/          # Database session
│       │   ├── models/      # SQLAlchemy models
│       │   ├── schemas/     # Pydantic schemas
│       │   ├── services/    # Business logic (14 services)
│       │   │   ├── free_tts_service.py  # FREE TTS!
│       │   │   ├── ai_agent_service.py  # Uses free TTS
│       │   │   └── ... 
│       │   └── tasks/       # Celery background tasks
│       ├── requirements.txt
│       └── Dockerfile
│
├── packages/
│   └── shared/              # Shared TypeScript/Python types
│
├── docker/
│   ├── nginx.conf           # Nginx reverse proxy config
│   └── init-db.sql          # Database initialization
│
├── docker-compose.yml       # Local development stack
├── .env.example             # Environment template
└── README.md
```

## ⚙️ Configuration

### Environment Variables
See `.env.example` for all configuration options. Key categories:

| Category | Variables |
|----------|-----------|
| **Database** | `DATABASE_URL` |
| **Redis** | `REDIS_URL`, `CELERY_BROKER_URL` |
| **Security** | `SECRET_KEY`, `ENCRYPTION_KEY`, `JWT` settings |
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` |
| **OpenAI** | `OPENAI_API_KEY` (AI logic only) |
| **Free TTS** | `FREE_TTS_ENGINE` (piper/coqui/espeak/system) |
| **Google** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, OAuth redirect URI |
| **Calling** | Window times, retry limits, concurrency |
| **Callbacks** | Reminder times, max days, scheduling |

### Campaign Configuration
Each campaign can be configured with:
- AI instructions and knowledge base
- Opening script with personalization variables
- Voice selection (mapped to free TTS voices)
- Calling schedule (hours, days, timezone)
- Retry policy and delays
- Google Sheets sync settings
- Callback rules

## 📖 API Documentation

### Authentication
All API endpoints require JWT Bearer token:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/campaigns
```

### Key Endpoints

#### Campaigns
```
GET    /api/v1/campaigns              # List campaigns
POST   /api/v1/campaigns              # Create campaign
GET    /api/v1/campaigns/{id}         # Get campaign
PATCH  /api/v1/campaigns/{id}         # Update campaign
POST   /api/v1/campaigns/{id}/start   # Start campaign
POST   /api/v1/campaigns/{id}/pause   # Pause campaign
POST   /api/v1/campaigns/{id}/stop    # Stop campaign
POST   /api/v1/campaigns/{id}/validate # Validate config
GET    /api/v1/campaigns/{id}/metrics # Get metrics
```

#### Customers
```
GET    /api/v1/customers              # List customers
POST   /api/v1/customers              # Create customer
POST   /api/v1/customers/import       # Bulk import (JSON)
POST   /api/v1/customers/import/csv   # Bulk import (CSV)
GET    /api/v1/customers/export       # Export customers
POST   /api/v1/customers/bulk         # Bulk actions
```

#### Calls
```
GET    /api/v1/calls                  # List calls
GET    /api/v1/calls/{id}             # Get call details
GET    /api/v1/calls/{id}/transcript  # Get transcript
GET    /api/v1/calls/{id}/recording   # Get recording
GET    /api/v1/calls/campaign/{id}/live # Live calls
```

#### Callbacks
```
GET    /api/v1/callbacks              # List callbacks
POST   /api/v1/callbacks              # Schedule callback
GET    /api/v1/callbacks/campaign/{id}/due # Due callbacks
POST   /api/v1/callbacks/{id}/complete # Complete callback
```

#### Analytics
```
GET    /api/v1/analytics/dashboard    # Dashboard metrics
GET    /api/v1/analytics/campaigns/{id} # Campaign analytics
GET    /api/v1/analytics/organization # Organization analytics
GET    /api/v1/analytics/export/{type} # Export reports
```

#### Webhooks (Twilio)
```
POST   /api/v1/webhooks/twilio/voice      # Voice webhook
POST   /api/v1/webhooks/twilio/status     # Status callback
POST   /api/v1/webhooks/twilio/recording  # Recording callback
POST   /api/v1/webhooks/twilio/transcription # Transcription
```

## 🔧 Development

### Local Development Setup

#### Backend
```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env
alembic upgrade head
python -m prisma db seed
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd apps/web
npm install
cp ../.env.example .env.local
# Edit .env.local
npm run dev
```

#### Celery Workers
```bash
cd apps/api
# Terminal 1: Call worker
celery -A app.core.celery_app worker -Q calls -c 4 --loglevel=info

# Terminal 2: Callback worker
celery -A app.core.celery_app worker -Q callbacks -c 2 --loglevel=info

# Terminal 3: Sync worker
celery -A app.core.celery_app worker -Q sync -c 2 --loglevel=info

# Terminal 4: Beat scheduler
celery -A app.core.celery_app beat --loglevel=info
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests
```bash
# Backend tests
cd apps/api
pytest

# Frontend tests
cd apps/web
npm run test
```

## 🚀 Deployment

### Production Deployment with Docker

1. **Prepare environment**
```bash
cp .env.example .env.production
# Fill in production values
```

2. **Build and deploy**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

3. **Configure SSL**
```bash
# Add certificates to docker/ssl/
# cert.pem, key.pem
```

4. **Set up monitoring**
- Prometheus metrics at `:9090/metrics`
- Health checks at `/health`
- Log aggregation via structured JSON logs

### Scaling Considerations

| Component | Scaling Strategy |
|-----------|-----------------|
| API | Horizontal (add replicas behind load balancer) |
| Celery Workers | Scale per queue based on workload |
| Database | Read replicas, connection pooling |
| Redis | Cluster mode for high availability |
| WebSocket | Sticky sessions or Redis adapter |

## 📋 Compliance Checklist

### Indian Telecom Regulations (TRAI)
- [ ] DND registry integration
- [ ] Calling hours compliance (9 AM - 6 PM)
- [ ] Consent recording and storage
- [ ] Opt-out mechanism (immediate)
- [ ] Call recording announcement
- [ ] Data localization (if required)

### Data Privacy
- [ ] Encryption at rest (AES-256)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Credential encryption in database
- [ ] Audit logging for all data access
- [ ] Data retention policies
- [ ] Right to deletion implementation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for Realtime API and GPT-4o
- [Rhasspy](https://github.com/rhasspy/piper) for **Piper TTS (Free!)**
- [Coqui](https://coqui.ai/) for **Coqui TTS (Free!)**
- [eSpeak NG](http://espeak.sourceforge.net/) for **eSpeak NG (Free!)**
- [Twilio](https://www.twilio.com/) for voice infrastructure
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [Prisma](https://www.prisma.io/) for database tooling
- [Celery](https://docs.celeryq.dev/) for distributed task queue

## 📞 Support

- **Repository**: [github.com/Angrajkarn/voice-ai](https://github.com/Angrajkarn/voice-ai)
- **Issues**: [GitHub Issues](https://github.com/Angrajkarn/voice-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Angrajkarn/voice-ai/discussions)

---

Built with ❤️ for sales teams and customer engagement automation.
**Now with 100% FREE voice synthesis!** 🎉