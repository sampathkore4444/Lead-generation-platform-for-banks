# SPEC_kilocode.md – STBank Laos Lead Generation Platform

## 1. Project Overview

**Project Name:** STBank LeadGen Platform  
**Type:** Web-based Lead Capture & Management System  
**Goal:** Replace manual Google Forms/Sheets process with a secure, production-grade lead management system integrated with STBank's core banking infrastructure.  
**Target Users:** Bank customers (Lao residents), Sales Representatives, Branch Managers, Compliance Officers, IT Administrators  
**Success Metrics:** 500+ leads/month, <1 hour contact time, ≤5% duplicates, full audit compliance

---

## 2. User Personas & Access Levels

| Role | Access Level | Dashboard Features |
| :--- | :--- | :--- |
| **Customer** | Public form only | Submit lead, receive confirmation |
| **Sales Rep** | Assigned leads only | View queue, update status, add notes, make calls |
| **Branch Manager** | Branch-wide | Team performance, reports, lead allocation |
| **Compliance Officer** | Audit logs only | View all logs, export, anonymize data |
| **IT Admin** | System full | User management, monitoring, backups |

---

## 3. Functional Requirements

### 3.1 Customer Lead Form (Public)

**URL:** `https://lead.stbank.la` (or subfolder)

**Fields:**

| Field | Type | Validation | Required |
| :--- | :--- | :--- | :--- |
| Full Name | text | Min 2, max 100 characters | Yes |
| Phone Number | tel | Lao format: 20XXXXXXXX (9 digits) | Yes |
| Lao ID Number | text | 13-15 digits only | Yes |
| Product Interest | dropdown | Savings/Personal Loan/Home Loan/Credit Card | Yes |
| Loan Amount | number | 1M - 500M LAK (if loan selected) | Conditional |
| Preferred Contact Time | dropdown | Morning/Afternoon/Evening | Yes |
| Consent Checkbox | checkbox | Must be checked | Yes |

**Requirements:**
- Mobile-responsive ( Lao market is 80%+ mobile)
- Google reCAPTCHA v3 enabled
- Real-time inline validation
- Success message: *"Thank you. A STBank representative will contact you within 2 business hours."*
- Optional SMS confirmation

### 3.2 Sales Rep Dashboard (Internal)

**Authentication:** OAuth2/LDAP integration with STBank employee directory + MFA

**Kanban Board Columns:**

| Column | Description | Sorting |
| :--- | :--- | :--- |
| New | Uncontacted leads | Oldest first (SLA countdown) |
| Contacted | Attempted but not qualified | Most recent first |
| Qualified | Ready for product offer | Nearest follow-up first |
| Converted | Account opened/loan disbursed | Date closed |
| Lost | Not interested/no docs | Date closed |

**Per-Lead Actions:**
- View full details (modal or page)
- Update status (one-click buttons)
- Add notes (free text, timestamped)
- One-click phone dial (CTI/webphone)
- Re-assign to another rep (manager only)

**Export:** CSV (max 1000 records)

### 3.3 Branch Manager Dashboard

**Views:**
- All leads by branch (filterable by rep, date, product, status)
- Team performance metrics:
  - Average time to first contact
  - Conversion rate by product
  - SLA compliance (% contacted within 1 hour)

**Reports:** Weekly PDF/Excel download

### 3.4 Compliance & Audit

**Audit Log Events:**
- Lead created (system)
- Lead viewed (user + IP)
- Status changed (old→new, user + IP + timestamp)
- Lead exported (user + IP + record count)
- Lead deleted (user + IP + reason)

**Data Retention:**
- Active leads: Unlimited
- Converted/Lost: 90 days → auto-anonymize (PII removed, compliance officer only)
- Audit logs: 7 years (Lao banking regulation)

### 3.5 Duplicate Prevention

**Logic:**
- Check phone number against leads from last 30 days
- If duplicate found:
  - Do NOT create new lead
  - Increment `resubmit_count` on original
  - Log attempt
  - Show customer: *"You already submitted on [date]. A rep will contact you soon."*

---

## 4. Technical Architecture

### 4.1 Recommended Stack

| Layer | Technology | Notes |
| :--- | :--- | :--- |
| **Frontend** | Reactjs + Vite + Tailwind CSS | SEO-friendly, mobile-first |
| **Backend** | FastAPI | High throughput API |
| **Database** | PostgreSQL 15 | ACID, trigger-based audit |
| **Cache/Rate Limit** | Redis | Session + rate limiting |
| **Hosting** | Lao data center (LaoTel/Unitel) OR on-prem | Data residency required |
| **Web Server** | Nginx | TLS termination, static |
| **Monitoring** | Prometheus + Grafana | Uptime, latency metrics |

### 4.2 Database Schema

```sql
-- Core tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL, -- sales_rep, branch_manager, compliance, it_admin
    branch_id INTEGER,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    lao_id VARCHAR(15) NOT NULL,
    product VARCHAR(50) NOT NULL,
    amount DECIMAL(15,0),
    preferred_time VARCHAR(20),
    status VARCHAR(20) DEFAULT 'new', -- new/contacted/qualified/converted/lost
    assigned_to INTEGER REFERENCES users(id),
    resubmit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    converted_at TIMESTAMP,
    anonymized_at TIMESTAMP
);

CREATE TABLE lead_audit_log (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- view, status_change, export, delete
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leads_phone ON leads(phone) WHERE created_at > NOW() - INTERVAL '30 days';
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_assigned ON leads(assigned_to);
```

### 4.3 API Endpoints

```
Public:
POST   /api/v1/leads           - Submit new lead
GET    /api/v1/leads/:id       - Get lead (with token)

Authenticated:
GET    /api/v1/dashboard      - Get rep's leads
PATCH  /api/v1/leads/:id      - Update status/notes
POST   /api/v1/leads/:id/split - Re-assign lead
GET    /api/v1/export         - Export CSV

Compliance:
GET    /api/v1/audit          - Search audit logs
POST   /api/v1/anonymize     - Trigger anonymization job
```

### 4.4 Security Requirements

| Requirement | Implementation |
| :--- | :--- |
| TLS | TLS 1.3 (no HTTP) |
| Password hashing | bcrypt cost 12 |
| Authentication | OAuth2 + MFA (mandatory) |
| Session timeout | 30 minutes idle |
| Rate limiting | 100 req/min per IP |
| API auth | API keys for integrations |
| RBAC | Role-based middleware |

---

## 5. UI/UX Guidelines

### 5.1 Visual Design (STBank Branding)

**Colors:**
- Primary: `#0066CC` (STBank Blue)
- Secondary: `#FFCC00` (Accent Yellow)
- Success: `#28A745`
- Warning: `#FFC107`
- Error: `#DC3545`
- Background: `#F5F7FA`

**Typography:**
- Headings: Noto Sans Lao (Lao script support required)
- Body: Noto Sans Lao, 16px base
- Monospace: For IDs/phones

**Layout:**
- Mobile-first (375px minimum)
- Single column form on mobile
- Max form width: 480px centered
- Touch-friendly: 44px minimum tap targets

### 5.2 Customer Form Layout

```
┌─────────────────────────┐
│    🏦 STBank Logo       │
│                         │
│    ໂຄນເຕື້ອມ 2 ໂມງ     │
│    (Call back in 2h)    │
│                         │
│  Full Name:             │
│  [_______________]      │
│                         │
│  Phone:                 │
│  [_______________]      │
│                         │
│  Lao ID:                 │
│  [_______________]      │
│                         │
│  Product:               │
│  [▼ Select...]          │
│                         │
│  □ I consent...         │
│                         │
│  [SUBMIT]               │
└─────────────────────────┘
```

### 5.3 Sales Rep Dashboard Layout

```
┌────────────────────────────────────────────────────────────┐
│  Logged in: Somchai (Vientiane Branch)    [Logout]         │
├────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 🔴 New   │ │ 🟡 Contacted│ │ 🟢 Qualified│ │ ❌ Lost │       │
│  │  12     │ │  8      │ │  5      │ │  3      │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├────────────────────────────────────────────────────────────┤
│  Search: [___________] Filter: [All Products ▼] [Apply]     │
├────────────────────────────────────────────────────────────┤
│  Name      │ Phone      │ Product    │ Received │ Age │Act   │
│  ──────────────────────────────────────────────────────     │
│  Mr. X    │ 2022123456 │ Personal   │ 10:32 AM │ 12m │[Call]│
│  Ms. Y    │ 2055567890 │ Savings    │ 10:15 AM │ 29m │[Call]│
│  Mr. Z    │ 2055123456 │ Home Loan  │ 09:45 AM │ 1h  │[Call]│
└────────────────────────────────────────────────────────────┘
```

---

## 6. Non-Functional Requirements

### 6.1 Performance Targets

| Metric | Target |
| :--- | :--- |
| Form load (3G) | <2 seconds |
| Form submit | <3 seconds |
| Dashboard load (10k leads) | <2 seconds |
| Concurrent users | 50 reps + 500 form submits/hour |
| Uptime | 99.5% (8:00-20:00, Mon-Sat) |

### 6.2 Compliance (Lao Requirements)

- [ ] All data stored in Laos (server location verified)
- [ ] Consent checkbox legally reviewed
- [ ] Right to deletion (72-hour SLA)
- [ ] 7-year audit log retention
- [ ] 90-day auto-anonymization implemented

---

## 7. Development Phases

| Phase | Duration | Deliverables |
| :--- | :--- | :--- |
| **Phase 1** | 6 weeks | Lead form, authentication, basic dashboard |
| **Phase 2** | 4 weeks | Core banking integration, LDAP auth |
| **Phase 3** | 2 weeks | Audit logs, compliance features |
| **Phase 4** | 3 weeks | Security testing (pen test, load test), UAT |
| **Phase 5** | 2 weeks | Deployment, training |
| **Total** | **17 weeks** | Production launch |

---

## 8. Risks & Mitigation

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Core banking API unavailable | High | Phase 1 launch without, manual check |
| Low rep adoption | Medium | Mandatory training, performance dashboards |
| Data breach | Critical | Pen test before launch, full audit logging |
| Regulatory change | Medium | Legal review on updates |

---

## 9. Acceptance Criteria (Launch)

- [ ] Customer submits lead → receives confirmation
- [ ] Sales rep logs in → views assigned leads
- [ ] Rep updates status → audit log records change
- [ ] Duplicate phone detected → submission blocked
- [ ] Export CSV → audit log records export
- [ ] Pen test → no critical vulnerabilities
- [ ] 5 reps complete training → can use system independently
- [ ] 95% contacted within 2 hours (tested with 50 leads)

---

## 10. Budget Estimate

| Item | Cost (USD) |
| :--- | :--- |
| Development (17 weeks) | $12,000 - $18,000 |
| Server hosting (Year 1) | $1,200 - $2,400 |
| SSL certificate | $100 - $300 |
| Penetration test | $500 - $1,500 |
| Training & docs | $500 - $1,000 |
| **Total** | **$14,300 - $23,200** |

---

## 11. Next Steps

1. **Internal approval:** Present to STBank IT, Compliance, Retail Banking heads
2. **Vendor selection:** RFP to 2-3 local Lao development teams
3. **Integration commitment:**Written core banking API access agreement
4. **Legal review:** Consent checkbox + data retention policy
5. **Budget sign-off:** $15,000 - $25,000 for Phase 1

---

**Document:** SPEC_kilocode.md  
**Version:** 1.1  
**Date:** 2026-04-07  
**Prepared for:** STBank Laos, Retail Banking Division

---

## 12. Smart Engines (AI/ML)

### 12.1 Credit Scoring Engine
- Calculate credit score (300-850)
- Categorize: Excellent, Good, Fair, Poor
- Factors analysis
- Max loan amount recommendation
- Suggested interest rate

### 12.2 Product Recommendation Engine
- Multi-product scoring
- Primary recommendation
- Confidence level
- Personalized reasoning

### 12.3 Churn Prediction Engine
- Probability scoring (0-1)
- Risk level categorization
- Contributing factors
- Retention suggestions

### 12.4 Optimal Contact Time Engine
- Best day prediction
- Best time prediction
- Confidence scoring
- Reasoning

### 12.5 Speech/Voice Analytics
- Sentiment analysis
- Keyword extraction
- Topic detection
- Talk ratio analysis
- Emotion detection
- Compliance monitoring

### 12.6 Conversation Intelligence
- Call summarization
- Action items extraction
- Lead qualification status
- Objection identification
- Closing signal detection
- Next action recommendation

### 12.7 Risk Assessment Engine
- Overall risk score (0-100)
- Multi-factor risk analysis
- Fraud indicator detection
- Mitigation suggestions
- Credit considerations

### 12.8 Auto-Scheduler
- Automated scheduling
- Channel selection (call/WhatsApp)
- Duration prediction
- Priority assignment
- Smart follow-up timing

---

## 13. Smart Engines API Endpoints

```
Smart Engines:
POST /api/v1/smart-engines/credit-score         - Credit scoring
POST /api/v1/smart-engines/recommendations       - Product recommendations
POST /api/v1/smart-engines/churn-prediction      - Churn prediction
POST /api/v1/smart-engines/optimal-contact-time  - Contact time
POST /api/v1/smart-engines/voice-analytics       - Voice analysis
POST /api/v1/smart-engines/conversation-intelligence - Conversation AI
POST /api/v1/smart-engines/risk-assessment       - Risk assessment
POST /api/v1/smart-engines/auto-schedule         - Auto-scheduler
POST /api/v1/smart-engines/comprehensive-analysis - All engines
```

---

## 14. On-Premise Security Features

### 14.1 MFA (TOTP)
- Google Authenticator compatible
- Backup codes
- QR code setup
- Enable/disable endpoints

### 14.2 LDAP/AD Integration
- Active Directory authentication
- Group-based role mapping
- Hybrid auth (LDAP + local)

### 14.3 Self-hosted CAPTCHA
- Math-based challenges
- Token verification
- Honeypot detection

### 14.4 Data Compliance
- 90-day anonymization
- 7-year audit retention
- Data residency (Laos)

---

**Document:** SPEC_kilocode.md  
**Version:** 1.1  
**Date:** 2026-04-07  
**Prepared for:** STBank Laos, Retail Banking Division




backend/
├── requirements.txt
├── .env.example
└── src/
    ├── config/           # Settings, database config
    ├── core/            # FastAPI app setup
    ├── models/          # SQLAlchemy models
    ├── schemas/         # Pydantic schemas
    ├── services/       # Business logic
    ├── routes/         # API endpoints
    ├── middleware/     # JWT auth
    ├── common/        # Utilities
    └── main.py         # Entry point


frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── src/
    ├── main.tsx         # Entry point
    ├── App.tsx         # Main app
    ├── components/     # Reusable components (Button, Input, LeadForm)
    ├── pages/         # Page components
    ├── services/      # API service
    ├── hooks/        # Custom hooks
    ├── utils/         # Utilities
    ├── types/         # TypeScript types
    └── styles/        # Global CSS
