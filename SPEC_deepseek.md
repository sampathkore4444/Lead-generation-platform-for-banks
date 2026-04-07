Below is a comprehensive **`SPEC.md`** (Specification Document) for a production-ready lead generation platform tailored for **STBank Laos**. This document is written to be handed directly to a development team (internal or external) and covers all technical, functional, security, and compliance requirements.

---

# SPEC.md – STBank Laos Lead Generation Platform

## 1. Executive Summary

**Project Name:** STBank LeadGen Platform  
**Version:** 1.0  
**Goal:** Replace the manual pilot (Google Forms + Sheets) with a secure, production-grade lead capture and management system integrated with STBank’s existing core banking infrastructure.  
**Target Launch:** 4 months from approval.  
**Success Metrics:**  
- Process 500+ leads/month with 99.5% uptime during business hours.  
- Lead to contact within 1 hour (automated SLA tracking).  
- ≤5% duplicate submissions.  
- Full audit trail for compliance.

---

## 2. System Overview

### 2.1 User Personas

| Role | Description | Primary Actions |
| :--- | :--- | :--- |
| **Customer** | Lao resident (18–60) with basic digital literacy | Submits lead form, receives confirmation |
| **Sales Rep** | Bank officer (branch or call center) | Views leads, updates status, logs contact |
| **Branch Manager** | Supervises reps | Views team performance, lead conversion |
| **Compliance Officer** | Audits data access | Reviews audit logs, exports reports |
| **IT Admin** | Maintains system | Manages users, monitors uptime, backups |

### 2.2 Core Workflow

```
Customer visits landing page → Fills form (4-6 fields) → 
System validates input → Stores lead in database → 
Triggers instant notification to assigned sales rep → 
Rep views dashboard → Calls customer → Updates status (contacted / qualified / converted / lost) → 
Audit log records every action
```

---

## 3. Functional Requirements

### 3.1 Customer-Facing Lead Form

**FR-1:** Mobile-responsive, branded form at `lead.stbank.la` (or subfolder).  
**FR-2:** Fields (all required unless noted):

| Field | Type | Validation |
| :--- | :--- | :--- |
| Full Name | Text | Min 2 chars, max 100 |
| Phone Number | Tel | Lao format: 20XXXXXXXX (9 digits after 20) |
| Lao ID Number | Text | 13–15 digits (basic format check) |
| Product Interest | Dropdown | Savings Account, Personal Loan, Home Loan, Credit Card |
| Loan Amount (if loan) | Number | Optional, min 1M LAK, max 500M LAK |
| Preferred Contact Time | Dropdown | Morning (8-12), Afternoon (13-17), Evening (17-20) |

**FR-3:** CAPTCHA (Google reCAPTCHA v3) to prevent bots.  
**FR-4:** Real-time inline validation with clear error messages.  
**FR-5:** After submission, show: *"Thank you. A STBank representative will contact you within 2 business hours."*  
**FR-6:** Send auto-confirmation SMS (optional, budget-dependent) or email.

### 3.2 Sales Rep Dashboard

**FR-7:** Role-based login (OAuth2 or LDAP integration with STBank’s existing employee directory).  
**FR-8:** Dashboard displays leads assigned to that rep only.  
**FR-9:** Lead queue columns:

| Column | Description |
| :--- | :--- |
| New (uncontacted) | Highlighted in yellow, sort by oldest first |
| Contacted | Awaiting qualification |
| Qualified | Ready for product offer |
| Converted | Account opened or loan disbursed |
| Lost | Reason required (e.g., not interested, no documents) |

**FR-10:** Each lead row shows: Name, Phone, Product, Timestamp, Age (minutes since submission).  
**FR-11:** Click lead → open detail view with full data and status update buttons.  
**FR-12:** One-click phone dial (web-based or CTI integration).  
**FR-13:** Notes field (free text) for each lead.  
**FR-14:** Bulk export to CSV (limited to 1000 leads).

### 3.3 Branch Manager Dashboard

**FR-15:** View leads by rep, by branch, by date range.  
**FR-16:** Real-time SLA metrics:  
- % contacted within 1 hour  
- Average time to first contact  
- Conversion rate by product  
**FR-17:** Download weekly performance report (PDF/Excel).

### 3.4 Compliance & Audit

**FR-18:** Every access to lead data (view, edit, export) logged with: timestamp, user ID, action, IP address.  
**FR-19:** Audit log searchable by date, user, lead ID.  
**FR-20:** Logs retained for 7 years (per Lao banking regulations).  
**FR-21:** Leads automatically anonymized after 90 days of final status (converted or lost) – only accessible by compliance officers.

### 3.5 Duplicate Prevention

**FR-22:** System checks for duplicate phone number within last 30 days.  
**FR-23:** If duplicate found:  
- Do not create new lead.  
- Increment `resubmit_count` on original lead.  
- Log attempt.  
- Show customer: *"You already submitted a request on [date]. A representative will contact you soon."*

---

## 4. Non-Functional Requirements

### 4.1 Security

| NFR | Requirement |
| :--- | :--- |
| **Encryption** | TLS 1.3 for all traffic. Passwords hashed with bcrypt (cost 12). |
| **Authentication** | Multi-factor authentication (MFA) for all bank employee accounts. |
| **Authorization** | Role-based access control (RBAC). No direct database access from frontend. |
| **Session** | 30-minute idle timeout. |
| **Penetration Test** | Required before production launch (third-party). |
| **API Security** | Rate limiting (100 requests per minute per IP). API keys for integrations. |

### 4.2 Performance & Scalability

| NFR | Target |
| :--- | :--- |
| Form load time | <2 seconds on 3G network |
| Form submission | <3 seconds |
| Dashboard load | <2 seconds for 10,000 leads |
| Concurrent users | 50 sales reps + 500 form submissions/hour |
| Uptime | 99.5% during banking hours (8:00–20:00, Mon–Sat) |

### 4.3 Availability & Backup

- **Database backups:** Daily full backup, hourly incremental. Retain 30 days.  
- **Failover:** Manual failover to read-only replica acceptable (no real-time HA required initially).  
- **Disaster recovery:** Restore from backup within 24 hours.

### 4.4 Compliance (Lao Specific)

- **Data localization:** All lead data must reside on servers physically in Laos (or approved cloud region – check with Bank of Laos).  
- **Consent:** Form must include checkbox: *"I consent to STBank contacting me regarding financial products."*  
- **Right to deletion:** Customer can request deletion via hotline; compliance officer must be able to delete lead record within 72 hours (audit log preserved separately).

---

## 5. Technical Architecture

### 5.1 Recommended Stack (Local Developer Friendly)

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React js + Vite + Tailwind CSS | SEO-friendly, mobile-first, Lao language support |
| **Backend API** | FastAPI Python | High throughput, easy integration |
| **Database** | PostgreSQL 15 | Reliable, audit logging via triggers |
| **Cache** | Redis (optional) | Session store, rate limiting |
| **Hosting** | Local Lao data center (e.g., LaoTel, Unitel cloud) OR on-prem VM | Data residency compliance |
| **Reverse Proxy** | Nginx | TLS termination, static assets |
| **Monitoring** | Prometheus + Grafana | Uptime, request latency, error rates |

### 5.2 Database Schema (Simplified)

```sql
-- Core tables
users (id, email, role, branch_id, last_login, mfa_enabled)
leads (id, full_name, phone, lao_id, product, amount, preferred_time, status, created_at, assigned_to, converted_at)
lead_audit_log (id, lead_id, user_id, action, old_status, new_status, ip_address, created_at)
duplicate_log (id, phone, original_lead_id, attempted_at)
```

### 5.3 Integration Points

| Integration | Purpose | Method | Owner |
| :--- | :--- | :--- | :--- |
| **Core Banking System** | Check if existing customer | REST API (read-only) | STBank IT |
| **Employee Directory** | Authentication & roles | LDAP or OAuth2 | STBank IT |
| **SMS Gateway** | Send confirmation SMS | HTTP API (e.g., Lao Telecom) | Optional |
| **Internal Notification** | Alert rep of new lead | Webhook to Telegram/Teams or email | Internal |

**Note:** Integration with core banking is the highest risk. If API is unavailable, Phase 1 can launch without it (manual check by rep). Phase 2 adds integration.

---

## 6. Development Phases & Timeline

| Phase | Duration | Deliverables | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Phase 0: Setup** | 1 week | Dev environment, database, CI/CD pipeline | Code runs locally |
| **Phase 1: Core Form + Dashboard** | 6 weeks | Public form, admin login, basic lead queue | Rep can view and update leads |
| **Phase 2: Integration** | 4 weeks | Core banking API (read customer status), LDAP auth | API calls succeed with test data |
| **Phase 3: Compliance & Audit** | 2 weeks | Audit logs, anonymization job, export reports | Compliance officer approves |
| **Phase 4: Security & Testing** | 3 weeks | Pen test, load test, UAT | No critical vulnerabilities |
| **Phase 5: Deployment & Training** | 2 weeks | Production server, user manual, 2-hour training session | 5 reps can use system independently |
| **Total** | **18 weeks** | Production platform | Go-live |

---

## 7. Security & Compliance Checklist (Pre-Launch)

- [ ] TLS certificate installed (no self-signed in production).  
- [ ] All default passwords changed.  
- [ ] Penetration test report with no high-risk findings.  
- [ ] Data retention policy implemented (90-day anonymization).  
- [ ] Consent checkbox legally reviewed by STBank legal.  
- [ ] Backup and restore procedure tested.  
- [ ] MFA enforced for all employee accounts.  
- [ ] Audit logging verified (every access recorded).  
- [ ] Server located in Laos (or approved cloud region).  
- [ ] Signed Data Processing Agreement (if using any third-party service).

---

## 8. Sample User Interface Mockups (Text Description)

### Customer Form (Mobile)
```
[STBank Logo]
Get a call back in 2 hours

Full name: [________________]
Phone:     [________________]
Lao ID:    [________________]
Product:   [Savings Account v]
Amount (kip): [____________] (optional)

[ ] I consent to be contacted

[ SUBMIT ]
```

### Sales Rep Dashboard (Desktop)
```
Logged in as: Somchai (Vientiane Branch)

🔴 New (3)  |  🟡 Contacted (5)  |  🟢 Qualified (2)

| Name     | Phone      | Product     | Received   | Age  | Action |
|---------------------------|-------------|------------|------|--------|
| Mr. X    | 2022123456 | Personal Loan| 10:32 AM  | 12m  | [Call] [View] |
| Ms. Y    | 2055567890 | Savings      | 10:15 AM  | 29m  | [Call] [View] |
```

---

## 9. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Core banking API unavailable | Medium | High | Phase 1 manual check; build stub API first |
| Low rep adoption | Medium | Medium | Mandatory training; manager dashboard shows individual performance |
| Data breach | Low | Critical | Pen test before launch; all access logged |
| Server downtime | Low | Medium | Daily backups; 24-hour restore SLA |
| Regulatory change | Low | Medium | Legal review before each major update |

---

## 10. Acceptance Criteria for Launch

The platform is considered production-ready when:

1. ✅ Customer can submit a lead and receive confirmation message.  
2. ✅ Sales rep can log in, view new leads, update status to contacted, and add notes.  
3. ✅ Duplicate phone number detection works (blocks submission within 30 days).  
4. ✅ Audit log records every status change with user ID and timestamp.  
5. ✅ Penetration test passes (no critical findings).  
6. ✅ Backup and restore successfully tested.  
7. ✅ At least 5 STBank reps complete training and can navigate dashboard.  
8. ✅ SLA metric: 95% of leads contacted within 2 hours (tested with 50 fake leads over 3 days).

---

## 11. Budget Estimate (Lao Context)

| Item | Cost (USD) |
| :--- | :--- |
| Development (18 weeks, local team) | $12,000 – $18,000 |
| Server hosting (first year, local data center) | $1,200 – $2,400 |
| SSL certificate | $100 – $300 |
| Penetration test | $500 – $1,500 |
| SMS gateway integration (optional) | $200 setup + $0.02/message |
| Training & documentation | $500 – $1,000 |
| **Total Estimated** | **$14,500 – $23,400** |

**Alternative:** Use a white-label CRM (e.g., HubSpot Enterprise) with customization: $6,000 – $10,000/year but less control over data residency.

---

## 12. Next Steps for STBank

1. **Internal approval:** Present this spec to STBank IT, Compliance, and Retail Banking heads.  
2. **Vendor selection:** Issue RFP to 2–3 local Lao development agencies (or assign internal team).  
3. **Integration agreement:** Get written commitment from core banking system owner to provide API access (or approved workaround).  
4. **Legal review:** Have STBank legal team review consent checkbox and data retention policy.  
5. **Budget sign-off:** Allocate $15,000–$25,000 for Phase 1 development and first year operations.  

Once these are complete, development can begin immediately following the 18-week plan above.

---

**Document prepared for:** STBank Laos, Retail Banking Division  
**Version:** 1.0  
**Date:** [Current Date]  

*End of SPEC.md*



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
