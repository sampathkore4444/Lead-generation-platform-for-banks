// Dashboard Page - Sales Rep Kanban View
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { leadApi } from '../services/api';
import { LeadListItem, LeadStats, LeadStatus } from '../types';
import { Button } from '../components/Button';
import { 
  Phone,  Clock, TrendingUp,  
  PhoneIncoming, UserCheck, UserPlus, XCircle, Download
} from 'lucide-react';
import { clearTokens, getAccessToken } from '../services/api';

export function Dashboard() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState<LeadListItem[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<LeadStatus | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      navigate('/login');
      return;
    }
    loadData();
  }, [navigate]);

  const loadData = async () => {
    try {
      const [leadsData, statsData] = await Promise.all([
        leadApi.getLeads(activeTab || undefined),
        leadApi.getLeadStats(),
      ]);
      setLeads(leadsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    clearTokens();
    navigate('/login');
  };

  const handleExport = async () => {
    try {
      const blob = await leadApi.exportLeads();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `leads_export_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const handleStatusChange = async (leadId: number, newStatus: LeadStatus) => {
    try {
      await leadApi.updateLeadStatus(leadId, { status: newStatus });
      loadData();
    } catch (error) {
      console.error('Status update failed:', error);
    }
  };

  const getStatusBadge = (status: LeadStatus) => {
    const badges = {
      [LeadStatus.NEW]: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      [LeadStatus.CONTACTED]: { bg: 'bg-blue-100', text: 'text-blue-800', icon: PhoneIncoming },
      [LeadStatus.QUALIFIED]: { bg: 'bg-purple-100', text: 'text-purple-800', icon: UserCheck },
      [LeadStatus.CONVERTED]: { bg: 'bg-green-100', text: 'text-green-800', icon: UserPlus },
      [LeadStatus.LOST]: { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle },
    };
    return badges[status];
  };

  const formatAge = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h`;
    return `${Math.floor(minutes / 1440)}d`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">ST</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">STBank LeadGen</h1>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={handleExport}>
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-4 shadow-card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.new_count}</p>
                  <p className="text-xs text-gray-500">New Leads</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-4 shadow-card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <PhoneIncoming className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.contacted_count}</p>
                  <p className="text-xs text-gray-500">Contacted</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-4 shadow-card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <UserCheck className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.qualified_count}</p>
                  <p className="text-xs text-gray-500">Qualified</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-4 shadow-card">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.conversion_rate.toFixed(1)}%</p>
                  <p className="text-xs text-gray-500">Conversion</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Kanban Board */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* New Column */}
          <div className="bg-gray-100 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-yellow-600" />
                New ({leads.filter(l => l.status === LeadStatus.NEW).length})
              </h3>
            </div>
            <div className="space-y-3">
              {leads
                .filter(l => l.status === LeadStatus.NEW)
                .map(lead => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onStatusChange={handleStatusChange}
                    formatAge={formatAge}
                  />
                ))}
            </div>
          </div>

          {/* Contacted Column */}
          <div className="bg-gray-100 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <PhoneIncoming className="w-4 h-4 text-blue-600" />
                Contacted ({leads.filter(l => l.status === LeadStatus.CONTACTED).length})
              </h3>
            </div>
            <div className="space-y-3">
              {leads
                .filter(l => l.status === LeadStatus.CONTACTED)
                .map(lead => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onStatusChange={handleStatusChange}
                    formatAge={formatAge}
                  />
                ))}
            </div>
          </div>

          {/* Qualified Column */}
          <div className="bg-gray-100 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-purple-600" />
                Qualified ({leads.filter(l => l.status === LeadStatus.QUALIFIED).length})
              </h3>
            </div>
            <div className="space-y-3">
              {leads
                .filter(l => l.status === LeadStatus.QUALIFIED)
                .map(lead => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onStatusChange={handleStatusChange}
                    formatAge={formatAge}
                  />
                ))}
            </div>
          </div>

          {/* Converted Column */}
          <div className="bg-gray-100 rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-green-600" />
                Converted ({leads.filter(l => l.status === LeadStatus.CONVERTED).length})
              </h3>
            </div>
            <div className="space-y-3">
              {leads
                .filter(l => l.status === LeadStatus.CONVERTED)
                .map(lead => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onStatusChange={handleStatusChange}
                    formatAge={formatAge}
                  />
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Lead Card Component
interface LeadCardProps {
  lead: LeadListItem;
  onStatusChange: (id: number, status: LeadStatus) => void;
  formatAge: (minutes: number) => string;
}

function LeadCard({ lead, onStatusChange, formatAge }: LeadCardProps) {
  const [showActions, setShowActions] = useState(false);

  const productLabels: Record<string, string> = {
    savings_account: 'Savings',
    personal_loan: 'Personal Loan',
    home_loan: 'Home Loan',
    credit_card: 'Credit Card',
  };

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 p-3 cursor-pointer hover:shadow-card-hover transition-all"
      onClick={() => setShowActions(!showActions)}
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <p className="font-medium text-gray-900 text-sm">{lead.full_name}</p>
          <p className="text-xs text-gray-500">{lead.phone_masked}</p>
        </div>
        <span className="text-xs text-gray-400">{formatAge(lead.age_minutes)}</span>
      </div>
      
      <div className="flex items-center justify-between">
        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
          {productLabels[lead.product] || lead.product}
        </span>
      </div>

      {showActions && (
        <div className="mt-3 pt-3 border-t border-gray-100 grid grid-cols-2 gap-2">
          {lead.status === LeadStatus.NEW && (
            <Button size="sm" onClick={() => onStatusChange(lead.id, LeadStatus.CONTACTED)}>
              Mark Contacted
            </Button>
          )}
          {lead.status === LeadStatus.CONTACTED && (
            <Button size="sm" onClick={() => onStatusChange(lead.id, LeadStatus.QUALIFIED)}>
              Qualify
            </Button>
          )}
          {lead.status === LeadStatus.QUALIFIED && (
            <Button size="sm" onClick={() => onStatusChange(lead.id, LeadStatus.CONVERTED)}>
              Convert
            </Button>
          )}
          <Button 
            size="sm" 
            variant="outline"
            onClick={() => onStatusChange(lead.id, LeadStatus.LOST)}
          >
            Lost
          </Button>
          <Button size="sm" variant="secondary">
            <Phone className="w-4 h-4 mr-1" />
            Call
          </Button>
        </div>
      )}
    </div>
  );
}

export default Dashboard;