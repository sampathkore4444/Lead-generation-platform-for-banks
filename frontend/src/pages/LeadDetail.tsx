// Lead Detail Page
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { leadApi } from '../services/api';
import { Lead, LeadStatus } from '../types';
import { Button } from '../components/Button';
import { Select } from '../components/Input';
import { 
  ArrowLeft, Phone, CreditCard, Clock, 
   Building, User as UserIcon
} from 'lucide-react';

export function LeadDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notes, setNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (id) {
      loadLead(parseInt(id));
    }
  }, [id]);

  const loadLead = async (leadId: number) => {
    try {
      const data = await leadApi.getLead(leadId);
      setLead(data);
      setNotes(data.notes || '');
    } catch (error) {
      console.error('Failed to load lead:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStatusChange = async (newStatus: LeadStatus) => {
    if (!lead) return;
    setIsSaving(true);
    try {
      const updated = await leadApi.updateLeadStatus(lead.id, { 
        status: newStatus,
        notes: notes 
      });
      setLead(updated);
    } catch (error) {
      console.error('Failed to update status:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveNotes = async () => {
    if (!lead) return;
    setIsSaving(true);
    try {
      await leadApi.updateLeadStatus(lead.id, { 
        status: lead.status,
        notes: notes 
      });
    } catch (error) {
      console.error('Failed to save notes:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const productLabels: Record<string, string> = {
    savings_account: 'Savings Account',
    personal_loan: 'Personal Loan',
    home_loan: 'Home Loan',
    credit_card: 'Credit Card',
  };

  const statusLabels: Record<string, string> = {
    new: 'New',
    contacted: 'Contacted',
    qualified: 'Qualified',
    converted: 'Converted',
    lost: 'Lost',
  };

  const timeLabels: Record<string, string> = {
    morning: 'Morning (8:00 - 12:00)',
    afternoon: 'Afternoon (13:00 - 17:00)',
    evening: 'Evening (17:00 - 20:00)',
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading lead details...</p>
        </div>
      </div>
    );
  }

  if (!lead) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Lead not found</p>
          <Button variant="outline" onClick={() => navigate('/dashboard')} className="mt-4">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Button variant="ghost" onClick={() => navigate('/dashboard')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Lead #{lead.id}</h1>
                <p className="text-sm text-gray-500">
                  {statusLabels[lead.status]} • Created {formatDate(lead.created_at)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="secondary" size="sm">
                <Phone className="w-4 h-4 mr-2" />
                Call
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Customer Info */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Information</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <UserIcon className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Full Name</p>
                    <p className="font-medium text-gray-900">{lead.full_name}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Phone</p>
                    <p className="font-medium text-gray-900">{lead.phone}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CreditCard className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Lao ID</p>
                    <p className="font-medium text-gray-900">{lead.lao_id}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Building className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Product</p>
                    <p className="font-medium text-gray-900">
                      {productLabels[lead.product] || lead.product}
                    </p>
                  </div>
                </div>

                {lead.amount && (
                  <div className="flex items-start gap-3">
                    <div className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Loan Amount</p>
                      <p className="font-medium text-gray-900">
                        {lead.amount.toLocaleString()} LAK
                      </p>
                    </div>
                  </div>
                )}

                {lead.preferred_time && (
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Preferred Contact Time</p>
                      <p className="font-medium text-gray-900">
                        {timeLabels[lead.preferred_time] || lead.preferred_time}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Notes */}
            <div className="bg-white rounded-xl shadow-card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add notes about this lead..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
              />
              <div className="mt-3 flex justify-end">
                <Button 
                  onClick={handleSaveNotes} 
                  isLoading={isSaving}
                  disabled={notes === (lead.notes || '')}
                >
                  Save Notes
                </Button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Update Status</h2>
              
              <div className="space-y-3">
                <Select
                  value={lead.status}
                  onChange={(e) => handleStatusChange(e.target.value as LeadStatus)}
                  options={[
                    { value: LeadStatus.NEW, label: '🆕 New' },
                    { value: LeadStatus.INITIAL_CONTACT, label: '📞 Initial Contact' },
                    { value: LeadStatus.NEEDS_ASSESSMENT, label: '📋 Needs Assessment' },
                    { value: LeadStatus.QUALIFICATION, label: '✅ Qualification' },
                    { value: LeadStatus.PROPOSAL, label: '📝 Proposal' },
                    { value: LeadStatus.NEGOTIATION, label: '🤝 Negotiation' },
                    { value: LeadStatus.CONVERTED, label: '🎉 Converted' },
                    { value: LeadStatus.LOST, label: '❌ Lost' },
                  ]}
                />

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <Button
                    variant={lead.status === LeadStatus.NEW ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.NEW)}
                  >
                    🆕 New
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.INITIAL_CONTACT ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.INITIAL_CONTACT)}
                  >
                    📞 Initial Contact
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.NEEDS_ASSESSMENT ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.NEEDS_ASSESSMENT)}
                  >
                    📋 Needs Assessment
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.QUALIFICATION ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.QUALIFICATION)}
                  >
                    ✅ Qualification
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.PROPOSAL ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.PROPOSAL)}
                  >
                    📝 Proposal
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.NEGOTIATION ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.NEGOTIATION)}
                  >
                    🤝 Negotiation
                  </Button>
                  <Button
                    variant={lead.status === LeadStatus.CONVERTED ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => handleStatusChange(LeadStatus.CONVERTED)}
                  >
                    🎉 Converted
                  </Button>
                </div>

                {lead.status !== LeadStatus.LOST && (
                  <Button
                    variant="danger"
                    className="w-full mt-2"
                    onClick={() => handleStatusChange(LeadStatus.LOST)}
                  >
                    Mark as Lost
                  </Button>
                )}
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-xl shadow-card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
              
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-primary-500 mt-2"></div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Created</p>
                    <p className="text-xs text-gray-500">{formatDate(lead.created_at)}</p>
                  </div>
                </div>

                {lead.first_contact_at && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">First Contact</p>
                      <p className="text-xs text-gray-500">{formatDate(lead.first_contact_at)}</p>
                    </div>
                  </div>
                )}

                {lead.converted_at && (
                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Converted</p>
                      <p className="text-xs text-gray-500">{formatDate(lead.converted_at)}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default LeadDetail;