// Type Definitions for STBank LeadGen Frontend

// User Types
export enum UserRole {
  SALES_REP = 'sales_rep',
  BRANCH_MANAGER = 'branch_manager',
  COMPLIANCE_OFFICER = 'compliance_officer',
  IT_ADMIN = 'it_admin',
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  branch_id: number | null;
  is_active: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
}

export interface Branch {
  id: number;
  name: string;
  code: string;
  address: string | null;
  phone: string | null;
  is_active: boolean;
}

// Lead Types
export enum ProductType {
  SAVINGS_ACCOUNT = 'savings_account',
  PERSONAL_LOAN = 'personal_loan',
  HOME_LOAN = 'home_loan',
  CREDIT_CARD = 'credit_card',
}

export enum PreferredTime {
  MORNING = 'morning',
  AFTERNOON = 'afternoon',
  EVENING = 'evening',
}

export enum LeadStatus {
  NEW = 'new',
  INITIAL_CONTACT = 'initial_contact',
  NEEDS_ASSESSMENT = 'needs_assessment',
  QUALIFICATION = 'qualification',
  PROPOSAL = 'proposal',
  NEGOTIATION = 'negotiation',
  CONVERTED = 'converted',
  LOST = 'lost',
}

export interface Lead {
  id: number;
  full_name: string;
  phone: string;
  lao_id: string;
  product: ProductType;
  amount: number | null;
  preferred_time: PreferredTime | null;
  consent_given: boolean;
  status: LeadStatus;
  branch_id: number | null;
  assigned_to: number | null;
  notes: string | null;
  resubmit_count: number;
  first_contact_at: string | null;
  converted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadListItem {
  id: number;
  full_name: string;
  phone: string;
  phone_masked: string;
  product: ProductType;
  amount: number | null;
  preferred_time: PreferredTime | null;
  status: LeadStatus;
  assigned_to: number | null;
  assigned_to_name: string | null;
  created_at: string;
  age_minutes: number;
}

export interface LeadStats {
  total: number;
  new_count: number;
  contacted_count: number;
  qualified_count: number;
  converted_count: number;
  lost_count: number;
  conversion_rate: number;
  avg_time_to_contact: number;
  sla_compliance: number;
}

// Form Types
export interface LeadFormData {
  full_name: string;
  phone: string;
  lao_id: string;
  product: ProductType;
  amount?: number;
  preferred_time?: PreferredTime;
  consent_given: boolean;
}

export interface LeadStatusUpdate {
  status: LeadStatus;
  notes?: string;
  lost_reason?: string;
}

export interface LeadAssign {
  assigned_to: number;
}

// Auth Types
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Duplicate Check
export interface DuplicateCheck {
  is_duplicate: boolean;
  original_lead_id: number | null;
  original_submission_date: string | null;
  message: string;
}

// AI Suggestion Types
export interface NextBestAction {
  lead_id: number;
  suggested_stage: string;
  action: string;
  reason: string;
  urgency: 'high' | 'medium' | 'low';
  tips: string[];
}