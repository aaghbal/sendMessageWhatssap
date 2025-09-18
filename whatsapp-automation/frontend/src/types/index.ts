export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  is_verified: boolean;
  is_active: boolean;
  date_joined: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface PhoneNumber {
  id: number;
  phone_number: string;
  country_code: string;
  name: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PhoneNumberGroup {
  id: number;
  name: string;
  description?: string;
  phone_numbers: PhoneNumber[];
  created_at: string;
  updated_at: string;
}

export interface MessageTemplate {
  id: number;
  name: string;
  template_type: 'text' | 'media' | 'location';
  content: string;
  media_url?: string;
  variables: string[];
  created_at: string;
  updated_at: string;
}

export interface SentMessage {
  id: number;
  template: MessageTemplate;
  recipient: PhoneNumber;
  content: string;
  status: 'pending' | 'sent' | 'delivered' | 'read' | 'failed';
  twilio_sid?: string;
  error_message?: string;
  sent_at?: string;
  delivered_at?: string;
  read_at?: string;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  template: MessageTemplate;
  recipients: PhoneNumber[];
  recipient_groups: PhoneNumberGroup[];
  status: 'draft' | 'scheduled' | 'running' | 'completed' | 'failed';
  scheduled_at?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CampaignMessage {
  id: number;
  campaign: number;
  message: SentMessage;
  created_at: string;
}

export interface CampaignAnalytics {
  id: number;
  campaign: number;
  total_messages: number;
  sent_messages: number;
  delivered_messages: number;
  read_messages: number;
  failed_messages: number;
  success_rate: number;
  delivery_rate: number;
  read_rate: number;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_contacts: number;
  total_templates: number;
  total_campaigns: number;
  active_campaigns: number;
  messages_sent_today: number;
  messages_sent_this_month: number;
  success_rate_this_month: number;
  recent_campaigns: Campaign[];
}

export interface APIError {
  detail?: string;
  message?: string;
  [key: string]: any;
}
