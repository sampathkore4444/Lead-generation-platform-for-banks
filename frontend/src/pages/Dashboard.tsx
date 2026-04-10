// Dashboard Page - Sales Rep Kanban View with Drag and Drop + AI Suggestions
import { useState, useEffect, DragEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { leadApi } from '../services/api';
import { LeadListItem, LeadStats, LeadStatus, NextBestAction } from '../types';
import { Button } from '../components/Button';
import { 
  Phone,  Clock, TrendingUp,  
  PhoneIncoming, UserCheck, UserPlus, XCircle, Download, AlertTriangle, Lightbulb, Zap
} from 'lucide-react';
import { clearTokens, getAccessToken } from '../services/api';

const COLUMNS = [
  { status: 'new' as const, title: 'New', icon: Clock, color: 'yellow', desc: 'Lead Created' },
  { status: 'initial_contact' as const, title: 'Initial Contact', icon: PhoneIncoming, color: 'blue', desc: 'First Contact Made' },
  { status: 'needs_assessment' as const, title: 'Needs Assessment', icon: UserCheck, color: 'indigo', desc: 'Gathering Requirements' },
  { status: 'qualification' as const, title: 'Qualification', icon: TrendingUp, color: 'purple', desc: 'Checking Eligibility' },
  { status: 'proposal' as const, title: 'Proposal', icon: UserPlus, color: 'orange', desc: 'Presenting Options' },
  { status: 'negotiation' as const, title: 'Negotiation', icon: Phone, color: 'pink', desc: 'Discussing Terms' },
  { status: 'converted' as const, title: 'Converted', icon: UserPlus, color: 'green', desc: 'Account Opened' },
  { status: 'lost' as const, title: 'Lost', icon: XCircle, color: 'red', desc: 'Not Interested' },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [leads, setLeads] = useState<LeadListItem[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [draggedLead, setDraggedLead] = useState<LeadListItem | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Record<number, NextBestAction>>({});
  const [showSuggestions, setShowSuggestions] = useState(true);

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
        leadApi.getLeads(),
        leadApi.getLeadStats(),
      ]);
      setLeads(leadsData);
      setStats(statsData);
      
      // Load AI suggestions for each lead
      const suggestionPromises = leadsData.map(async (lead) => {
        try {
          const suggestion = await leadApi.getLeadSuggestion(lead.id);
          return { id: lead.id, suggestion };
        } catch {
          return { id: lead.id, suggestion: null };
        }
      });
      
      const suggestionResults = await Promise.all(suggestionPromises);
      const suggestionMap: Record<number, NextBestAction> = {};
      suggestionResults.forEach((result) => {
        if (result.suggestion) {
          suggestionMap[result.id] = result.suggestion;
        }
      });
      setSuggestions(suggestionMap);
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

  // Drag and Drop handlers
  const handleDragStart = (e: DragEvent<HTMLDivElement>, lead: LeadListItem) => {
    setDraggedLead(lead);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', lead.id.toString());
    // Add a transparent drag image
    const dragImage = e.currentTarget.cloneNode(true) as HTMLElement;
    dragImage.style.opacity = '0.8';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 50, 25);
    setTimeout(() => document.body.removeChild(dragImage), 0);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>, status: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverColumn(status);
  };

  const handleDragLeave = () => {
    setDragOverColumn(null);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>, newStatus: string) => {
    e.preventDefault();
    setDragOverColumn(null);
    
    if (draggedLead && draggedLead.status !== newStatus) {
      handleStatusChange(draggedLead.id, newStatus as LeadStatus);
    }
    setDraggedLead(null);
  };

  const handleDragEnd = () => {
    setDraggedLead(null);
    setDragOverColumn(null);
  };

  const getLeadsByStatus = (status: string) => {
    return leads.filter(l => l.status === status);
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
              <Button 
                variant={showSuggestions ? "primary" : "ghost"} 
                size="sm" 
                onClick={() => setShowSuggestions(!showSuggestions)}
              >
                <Lightbulb className={`w-4 h-4 mr-2 ${showSuggestions ? 'text-yellow-400' : ''}`} />
                AI Tips
              </Button>
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 overflow-x-auto">
        <div className="flex gap-4 min-w-max pb-4">
          {COLUMNS.map(column => {
            const columnLeads = getLeadsByStatus(column.status);
            const Icon = column.icon;
            
            return (
              <div
                key={column.status}
                className={`bg-gray-100 rounded-xl p-4 min-h-[500px] transition-all ${
                  dragOverColumn === column.status ? 'ring-2 ring-primary-500 bg-primary-50' : ''
                }`}
                onDragOver={(e) => handleDragOver(e, column.status)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, column.status)}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    <Icon className={`w-4 h-4 text-${column.color}-600`} />
                    {column.title} ({columnLeads.length})
                  </h3>
                </div>
                <div className="space-y-3">
                  {columnLeads.map(lead => {
                    const suggestion = suggestions[lead.id];
                    const isStale = suggestion?.urgency === 'high' && lead.age_minutes > 1440;
                    
                    return (
                    <div
                      key={lead.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, lead)}
                      onDragEnd={handleDragEnd}
                      className={`bg-white rounded-lg border-2 p-3 cursor-move hover:shadow-card-hover transition-all ${
                        draggedLead?.id === lead.id ? 'opacity-50 scale-95' : ''
                      } ${isStale ? 'border-red-400' : ''}`}
                    >
                      {/* Stale Warning */}
                      {isStale && (
                        <div className="mb-2 flex items-center gap-1 text-red-600 text-xs font-medium">
                          <AlertTriangle className="w-3 h-3" />
                          Stale - Contact Now!
                        </div>
                      )}
                      
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium text-gray-900 text-sm">{lead.full_name}</p>
                          <p className="text-xs text-gray-500">{lead.phone_masked}</p>
                        </div>
                        <span className="text-xs text-gray-400">{formatAge(lead.age_minutes)}</span>
                      </div>
                      
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                          {lead.product === 'savings_account' ? 'Savings' : 
                           lead.product === 'personal_loan' ? 'Personal Loan' :
                           lead.product === 'home_loan' ? 'Home Loan' :
                           lead.product === 'credit_card' ? 'Credit Card' : lead.product}
                        </span>
                        {lead.preferred_time && (
                          <span className="text-xs text-gray-400">
                            {lead.preferred_time === 'morning' ? '🌅' : 
                             lead.preferred_time === 'afternoon' ? '☀️' : '🌆'}
                          </span>
                        )}
                      </div>
                      
                      {/* AI Suggestion */}
                      {showSuggestions && suggestion && (
                        <div className={`mt-2 p-2 rounded-lg text-xs ${
                          suggestion.urgency === 'high' ? 'bg-red-50 border border-red-200' :
                          suggestion.urgency === 'medium' ? 'bg-yellow-50 border border-yellow-200' :
                          'bg-blue-50 border border-blue-200'
                        }`}>
                          <div className="flex items-center gap-1 font-medium mb-1">
                            <Zap className="w-3 h-3" />
                            <span className={suggestion.urgency === 'high' ? 'text-red-700' : 'text-gray-700'}>
                              {suggestion.action}
                            </span>
                          </div>
                          <p className="text-gray-600 text-xs">{suggestion.reason}</p>
                        </div>
                      )}
                    </div>
                  )})}
                  {columnLeads.length === 0 && (
                    <div className="text-center py-8 text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-lg">
                      Drop leads here
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
