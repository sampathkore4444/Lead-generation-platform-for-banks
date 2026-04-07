# STBank Laos Lead Generation Platform - End-to-End Flow Documentation

## Table of Contents
1. [Platform Overview](#platform-overview)
2. [System Architecture](#system-architecture)
3. [Frontend-Backend Communication](#frontend-backend-communication)
4. [Feature Phases](#feature-phases)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Database Schema](#database-schema)
7. [Security & Authentication](#security--authentication)
8. [AI & ML Features](#ai--ml-features)
9. [Deployment Guide](#deployment-guide)

---

## Platform Overview

The STBank Laos Lead Generation Platform is a production-ready system designed to replace manual lead capture (Google Forms + Sheets) with a secure, automated lead management system. The platform supports multiple user roles:

| Role | Description | Access Level |
|------|-------------|---------------|
| **Customer** | Lao resident (18-60) submitting lead forms | Public form only |
| **Sales Rep** | Bank officer viewing/managing leads | Assigned leads only |
| **Branch Manager** | Supervises team performance | Branch-level analytics |
| **Compliance Officer** | Audits data access & exports | Full audit logs |
| **IT Admin** | System maintenance & configuration | Full system access |

---

## System Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│  - React 18 + TypeScript                                       │
│  - Vite (build tool)                                           │
│  - Tailwind CSS (styling)                                      │
│  - React Router (navigation)                                   │
│  - Axios (HTTP client)                                          │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI Python)                   │
│  - FastAPI (REST API framework)                                 │
│  - SQLAlchemy (ORM)                                            │
│  - Pydantic (data validation)                                  │
│  - JWT (authentication)                                         │
│  - PostgreSQL (database)                                        │
│  - Redis (caching/sessions)                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE (PostgreSQL)                      │
│  - Users, Leads, Audit Logs                                     │
│  - Branches, Products                                          │
│  - Anonymization data                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI/ML SERVICES (Ollama)                       │
│  - Llama3.2 (LLM for NLP tasks)                                │
│  - ML Models (sklearn)                                         │
│  - Smart Engines                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
Lead Generation Platform Banks - Laos/
├── backend/
│   ├── src/
│   │   ├── config/           # Settings, database config
│   │   │   ├── settings.py   # Environment variables
│   │   │   └── database.py   # SQLAlchemy setup
│   │   ├── core/             # FastAPI app setup
│   │   │   └── fastapi.py    # Main app configuration
│   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── user.py       # User model
│   │   │   ├── lead.py       # Lead model
│   │   │   └── audit.py      # Audit log model
│   │   ├── schemas/          # Pydantic validation schemas
│   │   │   ├── user.py       # User schemas
│   │   │   └── lead.py       # Lead schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ai_service.py         # Ollama AI integration
│   │   │   ├── lead_service.py       # Lead operations
│   │   │   ├── mfa_service.py         # TOTP MFA
│   │   │   ├── ldap_service.py        # LDAP/AD integration
│   │   │   ├── report_service.py      # PDF/Excel reports
│   │   │   ├── anonymization_service.py # Data anonymization
│   │   │   ├── smart_engines_service.py # Smart features
│   │   │   └── ml_engine_service.py    # ML models
│   │   ├── routes/           # API endpoints
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── leads.py      # Lead CRUD
│   │   │   ├── ai.py         # AI features
│   │   │   ├── mfa.py        # MFA endpoints
│   │   │   ├── integrations.py # Voice/WhatsApp
│   │   │   ├── smart_engines.py # Smart engines
│   │   │   ├── ml_engine.py  # ML endpoints
│   │   │   ├── reports.py    # Report generation
│   │   │   └── admin.py      # Admin functions
│   │   ├── middleware/       # JWT auth middleware
│   │   │   └── auth.py        # Token validation
│   │   └── common/          # Utilities
│   │       └── migrate.py   # DB migrations
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx         # Entry point
│   │   ├── App.tsx          # Main routing
│   │   ├── components/     # Reusable components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── LeadForm.tsx # Customer lead form
│   │   │   ├── Chatbot.tsx # AI chatbot
│   │   │   └── CaptchaWidget.tsx
│   │   ├── pages/          # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx     # Sales rep Kanban
│   │   │   ├── LeadDetail.tsx    # Lead details
│   │   │   ├── BranchManager.tsx # Team analytics
│   │   │   └── ComplianceAudit.tsx # Audit logs
│   │   ├── services/       # API client
│   │   │   └── api.ts       # Axios setup
│   │   ├── types/          # TypeScript types
│   │   └── styles/         # Tailwind CSS
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
│
├── docker-compose.yml
└── README.md
```

---

## Frontend-Backend Communication

### Communication Flow

```
┌──────────────┐      HTTP Requests       ┌──────────────┐
│              │ ──────────────────────▶  │              │
│   Frontend   │     (Axios Client)       │   Backend    │
│   (React)    │                          │  (FastAPI)   │
│              │ ◀──────────────────────   │              │
└──────────────┘    JSON Responses       └──────────────┘
```

### API Base URL

The frontend communicates with the backend via REST API:

```typescript
// frontend/src/services/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});
```

### Authentication Flow

1. **Login Request:**
   ```typescript
   // Frontend sends credentials
   const response = await api.post('/auth/token', formData);
   // Returns: { access_token, refresh_token, token_type, expires_in }
   ```

2. **Token Storage:**
   ```typescript
   // Tokens stored in localStorage
   localStorage.setItem('access_token', response.data.access_token);
   localStorage.setItem('refresh_token', response.data.refresh_token);
   ```

3. **Subsequent Requests:**
   ```typescript
   // Interceptor adds token to each request
   api.interceptors.request.use((config) => {
     const token = localStorage.getItem('access_token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

4. **Token Refresh:**
   ```typescript
   // On 401, refresh token automatically
   api.interceptors.response.use(async (error) => {
     if (error.response?.status === 401) {
       // Refresh token logic
     }
   });
   ```

### API Endpoints Structure

| Category | Prefix | Examples |
|----------|--------|----------|
| Authentication | `/api/v1/auth` | login, refresh, logout, register |
| Leads | `/api/v1/leads` | create, list, update, delete, export |
| AI | `/api/v1/ai` | score-lead, chatbot, predict-conversion |
| MFA | `/api/v1/mfa` | setup, enable, verify, disable |
| Integrations | `/api/v1/integrations` | call, whatsapp, sentiment, fraud |
| Smart Engines | `/api/v1/smart` | credit-score, recommendations, churn |
| ML Engine | `/api/v1/ml` | credit-score, churn-prediction, train |
| Reports | `/api/v1/reports` | leads-pdf, leads-excel, audit |
| Admin | `/api/v1/admin` | anonymization, jobs, ldap, system |

---

## Feature Phases

### Phase 1: Core Lead Management

#### 1.1 Customer Lead Form (Public)
- **Endpoint:** `POST /api/v1/leads`
- **Flow:**
  1. Customer fills form (name, phone, Lao ID, product, amount)
  2. Frontend validates input
  3. CAPTCHA verification (self-hosted)
  4. Duplicate check (phone within 30 days)
  5. Lead saved to database
  6. Confirmation displayed to customer

```typescript
// Frontend: LeadForm.tsx
const handleSubmit = async (data: LeadFormData) => {
  try {
    const captchaToken = await captchaRef.current.getToken();
    const response = await leadApi.createLead({ ...data, captchaToken });
    setSuccess(true);
  } catch (error) {
    setError(error.message);
  }
};
```

#### 1.2 Sales Rep Dashboard (Kanban View)
- **Endpoints:**
  - `GET /api/v1/leads` - List leads
  - `GET /api/v1/leads/stats` - Get statistics
  - `PATCH /api/v1/leads/{id}/status` - Update status

- **Kanban Columns:**
  | Status | Color | Description |
  |--------|-------|-------------|
  | New | Yellow | Uncontacted leads |
  | Contacted | Blue | Initial contact made |
  | Qualified | Purple | Verified interest |
  | Converted | Green | Account opened/loan disbursed |
  | Lost | Red | Not interested |

```typescript
// Frontend: Dashboard.tsx
const columns = [
  { id: 'new', title: 'New', color: 'yellow' },
  { id: 'contacted', title: 'Contacted', color: 'blue' },
  { id: 'qualified', title: 'Qualified', color: 'purple' },
  { id: 'converted', title: 'Converted', color: 'green' },
  { id: 'lost', title: 'Lost', color: 'red' },
];
```

#### 1.3 Lead Detail View
- **Endpoint:** `GET /api/v1/leads/{id}`
- **Features:**
  - Full lead information
  - Status update buttons
  - Notes section
  - AI scoring display
  - Call/contact actions

---

### Phase 2: Authentication & Security

#### 2.1 JWT Authentication
- **Endpoints:**
  - `POST /api/v1/auth/login` - User login
  - `POST /api/v1/auth/refresh` - Refresh token
  - `POST /api/v1/auth/logout` - Logout
  - `GET /api/v1/auth/me` - Get current user

- **Token Configuration:**
  - Access token: 30 minutes expiry
  - Refresh token: 7 days expiry
  - Password: bcrypt hashed (cost 12)

#### 2.2 Multi-Factor Authentication (TOTP)
- **Endpoints:**
  - `POST /api/v1/mfa/setup` - Initialize MFA for user
  - `POST /api/v1/mfa/enable` - Enable MFA
  - `POST /api/v1/mfa/verify` - Verify TOTP code
  - `POST /api/v1/mfa/disable` - Disable MFA
  - `POST /api/v1/mfa/regenerate-backup-codes` - New backup codes

- **Flow:**
  1. User enables MFA in profile
  2. System generates secret key + QR code
  3. User scans with authenticator app
  4. On login, user enters TOTP code
  5. System validates and grants access

#### 2.3 LDAP/AD Integration
- **Endpoints:**
  - `GET /api/v1/admin/ldap/config` - Get LDAP config
  - `POST /api/v1/admin/ldap/test` - Test connection
  - `POST /api/v1/auth/ldap/login` - LDAP login

- **Features:**
  - Sync users from Active Directory
  - Group-based role assignment
  - Single Sign-On (SSO) support

#### 2.4 Self-hosted CAPTCHA
- **Endpoints:**
  - `GET /api/v1/mfa/captcha` - Get CAPTCHA challenge
  - `POST /api/v1/mfa/captcha/verify` - Verify answer
  - `GET /api/v1/mfa/captcha/honey` - Honey pot token

- **Implementation:**
  - Math problems (addition/subtraction)
  - Honey pot field detection
  - Rate limiting per IP

---

### Phase 3: AI & Intelligence Features

#### 3.1 Ollama AI Integration
- **Base URL:** `http://localhost:11434` (configurable)
- **Model:** llama3.2

- **Endpoints:**
  - `POST /api/v1/ai/score-lead` - AI lead scoring
  - `POST /api/v1/ai/lead-insight` - Lead insights
  - `POST /api/v1/ai/predict-conversion` - Conversion prediction
  - `POST /api/v1/ai/chatbot` - Customer support chatbot
  - `POST /api/v1/ai/generate-report` - AI report generation

```python
# Backend: ai_service.py
async def score_lead_with_ai(lead_data: dict) -> dict:
    prompt = f"""
    Analyze this lead and provide a score (0-100):
    - Name: {lead_data['full_name']}
    - Product: {lead_data['product']}
    - Amount: {lead_data.get('amount', 0)}
    
    Consider: income potential, product fit, and engagement likelihood.
    """
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'user', 'content': prompt}
    ])
    return parse_ai_response(response)
```

#### 3.2 Smart Engines

| Engine | Endpoint | Function |
|--------|----------|----------|
| Credit Scoring | `POST /api/v1/smart/credit-score` | Calculate credit score |
| Product Recommendations | `POST /api/v1/smart/recommendations` | Jaccard similarity matching |
| Churn Prediction | `POST /api/v1/smart/churn-prediction` | Random Forest model |
| Optimal Contact Time | `POST /api/v1/smart/optimal-contact-time` | Decision Tree analysis |
| Voice Analytics | `POST /api/v1/smart/voice-analytics` | Sentiment & duration analysis |
| Conversation Intelligence | `POST /api/v1/smart/conversation-intelligence` | Call transcript analysis |
| Risk Assessment | `POST /api/v1/smart/risk-assessment` | Ensemble model |
| Auto-Scheduler | `POST /api/v1/smart/auto-schedule` | Optimal meeting scheduling |

#### 3.3 ML Engine (Machine Learning Models)

| Model | Endpoint | Algorithm |
|-------|----------|-----------|
| Credit Scoring | `POST /api/v1/ml/credit-score` | Logistic Regression |
| Churn Prediction | `POST /api/v1/ml/churn-prediction` | Random Forest |
| Lead Scoring | `POST /api/v1/ml/lead-score` | Gradient Boosting |
| Risk Assessment | `POST /api/v1/ml/risk-assessment` | Ensemble |
| Optimal Contact | `POST /api/v1/ml/optimal-contact-time` | Decision Tree |
| Voice Analytics | `POST /api/v1/ml/voice-analytics` | Naive Bayes |

- **Training Endpoints:**
  - `POST /api/v1/ml/train/credit-model`
  - `POST /api/v1/ml/train/churn-model`

---

### Phase 4: Communication Integrations

#### 4.1 Voice/Call Integration
- **Endpoints:**
  - `POST /api/v1/integrations/call/initiate` - Start call
  - `GET /api/v1/integrations/call/{id}` - Get call status

- **Features:**
  - WebRTC call initiation
  - Call recording
  - Duration tracking

#### 4.2 WhatsApp/Line Integration
- **Endpoints:**
  - `POST /api/v1/integrations/whatsapp/send` - Send WhatsApp
  - `POST /api/v1/integrations/line/send` - Send Line message

- **Message Types:**
  - Text messages
  - Product information
  - Appointment reminders

#### 4.3 Sentiment Analysis
- **Endpoint:** `POST /api/v1/integrations/sentiment`
- **Analysis:**
  - Text sentiment (positive/negative/neutral)
  - Emotion detection
  - Urgency identification

#### 4.4 Fraud Detection
- **Endpoints:**
  - `POST /api/v1/integrations/fraud/check` - Check fraud risk
  - `GET /api/v1/integrations/fraud/risk-levels` - Get risk levels

- **Checks:**
  - Phone number validation
  - Lao ID format validation
  - Duplicate detection
  - Suspicious pattern recognition

---

### Phase 5: Reporting & Compliance

#### 5.1 PDF/Excel Reports
- **Endpoints:**
  - `GET /api/v1/reports/leads/pdf` - Lead list PDF
  - `GET /api/v1/reports/leads/excel` - Lead list Excel
  - `GET /api/v1/reports/performance/pdf` - Performance PDF
  - `GET /api/v1/reports/audit/excel` - Audit log Excel

- **Libraries:**
  - PDF: ReportLab
  - Excel: OpenPyXL

#### 5.2 Audit Logging
- **Tracked Actions:**
  - Lead view
  - Lead create/update/delete
  - Status changes
  - Data export
  - Login/logout
  - Configuration changes

- **Log Fields:**
  ```python
  {
    "id": 1,
    "lead_id": 123,
    "user_id": 1,
    "user_name": "Somchai",
    "action": "view",
    "old_status": None,
    "new_status": None,
    "details": "Viewed lead details",
    "ip_address": "192.168.1.100",
    "created_at": "2024-01-15T10:30:00Z"
  }
  ```

#### 5.3 Data Anonymization
- **Endpoint:** `POST /api/v1/admin/anonymization/run`
- **Features:**
  - Automatic 90-day anonymization
  - Manual anonymization trigger
  - Restore anonymized data
  - Retention policy enforcement

- **Anonymized Fields:**
  - Phone: `***XXX1234`
  - Lao ID: `*************`
  - Notes: `[REDACTED]`

---

## API Endpoints Reference

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /auth/token | Login with credentials | No |
| POST | /auth/refresh | Refresh access token | No |
| POST | /auth/logout | Logout user | Yes |
| GET | /auth/me | Get current user | Yes |
| POST | /auth/register | Register new user | Yes (Admin) |

### Leads (`/api/v1/leads`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /leads | Create new lead | No (CAPTCHA) |
| GET | /leads | List leads | Yes |
| GET | /leads/stats | Get lead statistics | Yes |
| GET | /leads/{id} | Get lead detail | Yes |
| PATCH | /leads/{id}/status | Update status | Yes |
| PATCH | /leads/{id}/assign | Assign to rep | Yes |
| GET | /leads/export/csv | Export CSV | Yes |
| GET | /leads/duplicate-check | Check duplicate | No |

### AI (`/api/v1/ai`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /ai/score-lead | AI lead scoring | Yes |
| POST | /ai/lead-insight | Get lead insights | Yes |
| POST | /ai/predict-conversion | Predict conversion | Yes |
| POST | /ai/chatbot | Chat with AI | No |
| POST | /ai/generate-report | AI report | Yes |

### MFA (`/api/v1/mfa`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /mfa/setup | Setup MFA | Yes |
| POST | /mfa/enable | Enable MFA | Yes |
| POST | /mfa/verify | Verify TOTP | Yes |
| POST | /mfa/disable | Disable MFA | Yes |
| GET | /mfa/captcha | Get CAPTCHA | No |

### Integrations (`/api/v1/integrations`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /integrations/call/initiate | Start call | Yes |
| POST | /integrations/whatsapp/send | Send WhatsApp | Yes |
| POST | /integrations/line/send | Send Line | Yes |
| POST | /integrations/sentiment | Analyze sentiment | Yes |
| POST | /integrations/fraud/check | Check fraud | Yes |

### Smart Engines (`/api/v1/smart`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /smart/credit-score | Credit scoring | Yes |
| POST | /smart/recommendations | Product recommendations | Yes |
| POST | /smart/churn-prediction | Churn prediction | Yes |
| POST | /smart/optimal-contact-time | Contact time | Yes |
| POST | /smart/voice-analytics | Voice analysis | Yes |

### ML Engine (`/api/v1/ml`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /ml/credit-score | ML credit score | Yes |
| POST | /ml/churn-prediction | ML churn prediction | Yes |
| POST | /ml/lead-score | ML lead score | Yes |
| POST | /ml/train/credit-model | Train credit model | Yes |
| POST | /ml/train/churn-model | Train churn model | Yes |

### Reports (`/api/v1/reports`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /reports/leads/pdf | PDF report | Yes |
| GET | /reports/leads/excel | Excel report | Yes |
| GET | /reports/performance/pdf | Performance PDF | Yes |

### Admin (`/api/v1/admin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /admin/anonymization/stats | Anonymization stats | Yes |
| POST | /admin/anonymization/run | Run anonymization | Yes |
| GET | /admin/jobs/schedule | Job schedule | Yes |
| POST | /admin/jobs/run | Run jobs | Yes |
| GET | /admin/ldap/config | LDAP config | Yes |
| POST | /admin/ldap/test | Test LDAP | Yes |
| GET | /admin/system/info | System info | Yes |

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL,  -- sales_rep, branch_manager, compliance_officer, it_admin
    branch_id INTEGER REFERENCES branches(id),
    is_active BOOLEAN DEFAULT TRUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    ldap_id VARCHAR(255),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Leads Table
```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    lao_id VARCHAR(20),
    product VARCHAR(50) NOT NULL,  -- savings_account, personal_loan, home_loan, credit_card
    amount DECIMAL(15, 2),
    preferred_time VARCHAR(20),
    consent_given BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'new',  -- new, contacted, qualified, converted, lost
    branch_id INTEGER REFERENCES branches(id),
    assigned_to INTEGER REFERENCES users(id),
    notes TEXT,
    resubmit_count INTEGER DEFAULT 0,
    first_contact_at TIMESTAMP,
    converted_at TIMESTAMP,
    ai_score INTEGER,
    ai_insights TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Lead Audit Log Table
```sql
CREATE TABLE lead_audit_log (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- view, create, update, delete, status_change, export
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Branches Table
```sql
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security & Authentication

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Customer** | Submit lead form only |
| **Sales Rep** | View assigned leads, update status, add notes |
| **Branch Manager** | View branch leads, view analytics, assign leads |
| **Compliance Officer** | View all leads, export reports, view audit logs |
| **IT Admin** | Full access, user management, system config |

### Security Features

1. **Password Security:**
   - Bcrypt hashing (cost factor 12)
   - Password complexity requirements
   - Failed login lockout (5 attempts)

2. **Session Management:**
   - 30-minute idle timeout
   - Secure HTTP-only cookies option
   - Token refresh mechanism

3. **API Security:**
   - Rate limiting (100 req/min per IP)
   - CORS configuration
   - Input validation (Pydantic)

4. **Data Protection:**
   - TLS 1.3 encryption
   - Data anonymization after 90 days
   - Audit logging for all actions

---

## Deployment Guide

### Option 1: With Docker (Recommended)

#### Prerequisites
- Docker Desktop installed
- Docker Compose installed

#### Steps

1. **Clone the repository:**
   ```bash
   cd "Lead Generation Platform Banks - Laos"
   ```

2. **Create environment file:**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit with your settings
   
   # Frontend
   cp frontend/.env.example frontend/.env
   # Edit with your settings
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

5. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

#### Stop Services
```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

#### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

---

### Option 2: Without Docker (Local Development)

#### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis (optional)

#### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start PostgreSQL:**
   ```bash
   # Windows - Using pg_ctl or pgAdmin
   # Linux
   sudo systemctl start postgresql
   
   # Create database
   createdb stbank_leadgen
   ```

5. **Run database migrations:**
   ```bash
   python -m src.common.migrate
   # Or use Alembic if configured
   ```

6. **Start the backend server:**
   ```bash
   # Development mode (auto-reload)
   uvicorn src.core.fastapi:app --reload --host 0.0.0.0 --port 8000
   
   # Or
   python -m uvicorn src.core.fastapi:app --reload
   ```

7. **Access API documentation:**
   - Open http://localhost:8000/docs in browser

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Set VITE_API_URL=http://localhost:8000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Open http://localhost:5173 in browser

#### Stop Servers

**Backend:**
```bash
# Press Ctrl+C in the terminal running uvicorn
# Or kill the process
```

**Frontend:**
```bash
# Press Ctrl+C in the terminal running npm run dev
# Or
npm run build  # For production build
```

---

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/stbank_leadgen

# JWT
SECRET_KEY=your-secret-key-min-32-chars-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=stbank_leadgen

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Ollama (AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# LDAP (Optional)
LDAP_SERVER=ldap://localhost
LDAP_PORT=389
LDAP_BASE_DN=dc=stbank,dc=la

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=STBank LeadGen Platform
```

---

### Production Deployment Checklist

1. **Security:**
   - [ ] Change all default passwords
   - [ ] Configure TLS/SSL certificate
   - [ ] Set up firewall rules
   - [ ] Enable MFA for all users
   - [ ] Configure rate limiting

2. **Database:**
   - [ ] Set up automated backups
   - [ ] Configure connection pooling
   - [ ] Enable SSL connections

3. **Monitoring:**
   - [ ] Set up health checks
   - [ ] Configure logging
   - [ ] Set up alerts

4. **Compliance:**
   - [ ] Verify data residency
   - [ ] Configure audit logging
   - [ ] Set up anonymization job

---

## Quick Reference Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose build --no-cache

# Restart specific service
docker-compose restart backend
```

### Backend Commands
```bash
# Activate virtual environment
cd backend && venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.core.fastapi:app --reload

# Run tests
pytest
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Development
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

---

## Support & Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check PostgreSQL is running
   - Verify .env configuration
   - Check port 8000 is available

2. **Frontend can't connect to backend:**
   - Verify CORS settings
   - Check API URL in frontend .env
   - Ensure backend is running

3. **AI features not working:**
   - Verify Ollama is running: `curl http://localhost:11434`
   - Check model is installed: `ollama list`

4. **Database connection errors:**
   - Verify PostgreSQL credentials
   - Check database exists
   - Ensure network connectivity

---

*Document Version: 1.0*  
*Last Updated: 2026-04-07*  
*For: STBank Laos Lead Generation Platform*
