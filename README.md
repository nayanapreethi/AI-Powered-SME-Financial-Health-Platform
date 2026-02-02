# SME-Pulse AI - AI-Powered Financial Health Platform

<div align="center">

![SME-Pulse AI](https://img.shields.io/badge/SME--Pulse-AI-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)

**Empowering SMEs with institutional-grade financial analysis, credit readiness, and automated compliance using AI-driven narrative insights.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Documentation](#-api-documentation) • [Deployment](#-deployment)

</div>

---

## 🎯 Overview

SME-Pulse AI is a comprehensive financial health platform designed for Small and Medium Enterprises. It provides:

- 📊 **Multi-Source Data Ingestion** - Upload bank statements (PDF/CSV/XLSX), Tally/Zoho exports
- 🤖 **AI-Powered Health Assessment** - Proprietary SME-Health Score with Claude/GPT narratives
- 📈 **Financial Ratios** - DSCR, Current Ratio, Leverage, Profitability metrics
- 🚨 **Anomaly Detection** - Flag irregular transactions and financial irregularities
- 💡 **Automated Advisory** - AI-generated cost optimization and growth recommendations
- 🏦 **Product Matching** - Recommend financial products from banks/NBFCs

## ✨ Features

### A. Data Ingestion & Integration
- ✅ Multi-source upload (PDF/CSV/XLSX)
- ✅ Bank statement parsing (ICICI, HDFC, SBI)
- ✅ Tally/Zoho export support
- ✅ GST integration (GSTR-1, GSTR-3B)

### B. AI-Powered Health Assessment
- ✅ Cash Flow Narrative generation
- ✅ Creditworthiness Scoring (SME-Health Score)
- ✅ DSCR (Debt Service Coverage Ratio) calculation
- ✅ Current Ratio and liquidity analysis
- ✅ Anomaly detection for irregular transactions

### C. Automated Advisory & Marketplace
- ✅ Product Matching (Working Capital Loans, Bill Discounting)
- ✅ Cost Optimization recommendations
- ✅ 90-day cash flow forecasting
- ✅ Investor-Ready Report generation

### D. Security & Compliance
- ✅ DPDP Act compliance with granular consent
- ✅ AES-256 encryption at rest
- ✅ TLS 1.3 in transit
- ✅ Tamper-proof audit trails

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- 4GB RAM minimum

### Installation

1. **Clone the repository**
   ```bash
   cd /home/nayana/Documents/AI-Powered\ SME\ Financial\ Health\ Platform
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the services**

   **Using Docker (recommended):**
   ```bash
   docker-compose up -d
   ```

   **Manual startup:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Demo Credentials
- Email: `demo@sme-pulse.ai`
- Password: Any password (min 6 characters)

## 📁 Project Structure

```
sme-pulse-ai/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── routes/        # Route handlers
│   │   │   └── deps.py        # Dependencies
│   │   ├── core/              # Core configuration
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── main.py            # Application entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React.js frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API integration
│   │   └── assets/            # Static assets
│   ├── package.json
│   └── Dockerfile
├── database/                   # Database scripts
│   ├── init.sql               # Schema initialization
│   └── migrations/            # Alembic migrations
├── docker-compose.yml         # Docker orchestration
├── .env.example               # Environment template
├── setup.sh                   # Setup script
└── README.md                  # This file
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React.js)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │Dashboard│  │Documents│  │Analysis │  │Health Score │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘    │
└───────┼────────────┼────────────┼─────────────┼────────────┘
        │            │            │             │
        └────────────┴─────┬──────┴─────────────┘
                           │
                    ┌──────┴──────┐
                    │   REST API  │
                    │  (FastAPI)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────┴────┐       ┌─────┴─────┐      ┌────┴────┐
   │  File   │       │ Financial │      │   AI    │
   │Processing│      │ Analysis  │      │Narrative│
   └────┬────┘       └─────┬─────┘      └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────┴──────┐
                    │ PostgreSQL  │
                    │  Database   │
                    └─────────────┘
```

## 📡 API Documentation

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user

### Documents
- `POST /api/v1/documents/upload` - Upload financial document
- `GET /api/v1/documents` - List user documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document

### Analysis
- `POST /api/v1/analysis/health-score/{company_id}` - Calculate health score
- `GET /api/v1/analysis/health-score/{company_id}` - Get health score
- `GET /api/v1/analysis/financial-metrics/{company_id}` - Get financial metrics
- `GET /api/v1/analysis/anomalies/{company_id}` - Get detected anomalies
- `POST /api/v1/analysis/cash-flow-narrative` - Generate cash flow narrative
- `POST /api/v1/analysis/financial-advisory` - Get AI recommendations
- `GET /api/v1/analysis/dashboard/{company_id}` - Get dashboard summary
- `POST /api/v1/analysis/products/recommendations` - Get product recommendations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `SECRET_KEY` | JWT secret key | Required |
| `ENCRYPTION_KEY` | AES-256 encryption key | Required |
| `AI_API_KEY` | Claude/GPT API key (optional) | Mock responses if not set |
| `GST_API_KEY` | GST API key (optional) | Mock data if not set |
| `BANK_API_KEY` | Banking API key (optional) | Mock data if not set |
| `ENVIRONMENT` | Environment mode | `development` |
| `DEBUG` | Enable debug mode | `true` |

## 🛡️ Security

### DPDP Act Compliance
- Granular consent management for data fetching
- Data retention policies
- User data deletion capabilities
- Audit logging for all data access

### Encryption
- AES-256 encryption for sensitive data at rest
- TLS 1.3 for data in transit
- Secure password hashing (bcrypt)
- JWT token authentication

## 📊 Success Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Accuracy | 95%+ | Automated categorization accuracy |
| Time to Clarity | < 5 minutes | Manual vs automated analysis time |
| Loan Approval | +15% | Improvement in loan approval rates |

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Production with Docker

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Build frontend: `cd frontend && npm run build`
2. Configure web server (nginx/Apache)
3. Set up reverse proxy to backend
4. Configure SSL certificates
5. Set up monitoring and logging

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Support

For support, please contact:
- Email: support@sme-pulse.ai
- Documentation: https://docs.sme-pulse.ai

---

<div align="center">
Built with ❤️ for SMEs
</div>

