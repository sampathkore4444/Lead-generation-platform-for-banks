// Branch Manager Dashboard - Team Performance View
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { leadApi } from '../services/api';
import { LeadListItem, LeadStats, User } from '../types';
import { authApi } from '../services/api';
import { Button } from '../components/Button';
import { Select } from '../components/Input';
import { 
  Users, TrendingUp, Clock, Phone, 
  Download, LogOut, Building,
  Calendar, RefreshCw
} from 'lucide-react';
import { clearTokens, getAccessToken } from '../services/api';

export function BranchManager() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [leads, setLeads] = useState<LeadListItem[]>([]);
  const [stats, setStats] = useState<LeadStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('today');
  const [branchFilter, setBranchFilter] = useState<string>('all');
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      navigate('/login');
      return;
    }
    loadData();
  }, [navigate, dateRange, branchFilter]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [userData, leadsData, statsData] = await Promise.all([
        authApi.getCurrentUser(),
        leadApi.getLeads(undefined, 1000), // Get all leads for branch
        leadApi.getLeadStats(),
      ]);
      setUser(userData);
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
    setIsExporting(true);
    try {
      const blob = await leadApi.exportLeads();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `branch_report_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const getRepPerformance = () => {
    const repStats: Record<number, { name: string; count: number; converted: number }> = {};
    
    leads.forEach(lead => {
      if (lead.assigned_to) {
        if (!repStats[lead.assigned_to]) {
          repStats[lead.assigned_to] = {
            name: lead.assigned_to_name || 'Unknown',
            count: 0,
            converted: 0,
          };
        }
        repStats[lead.assigned_to].count += 1;
        if (lead.status === 'converted') {
          repStats[lead.assigned_to].converted += 1;
        }
      }
    });
    
    return Object.entries(repStats).map(([id, data]) => ({
      id: parseInt(id),
      ...data,
      rate: data.count > 0 ? (data.converted / data.count * 100).toFixed(1) : '0.0',
    }));
  };

  const dateRangeLabels: Record<string, string> = {
    today: 'Today',
    week: 'This Week',
    month: 'This Month',
    all: 'All Time',
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
              <div>
                <h1 className="text-xl font-bold text-gray-900">Branch Manager</h1>
                <p className="text-xs text-gray-500">Team Performance Dashboard</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                {user?.full_name} • {user?.branch_id ? `Branch ${user.branch_id}` : ''}
              </span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-5 shadow-card">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Users className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                  <p className="text-sm text-gray-500">Total Leads</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-card">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.conversion_rate.toFixed(1)}%</p>
                  <p className="text-sm text-gray-500">Conversion Rate</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-card">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                  <Clock className="w-6 h-6 text-yellow-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{Math.round(stats.avg_time_to_contact)}m</p>
                  <p className="text-sm text-gray-500">Avg Contact Time</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-5 shadow-card">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                  <Phone className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.sla_compliance.toFixed(1)}%</p>
                  <p className="text-sm text-gray-500">SLA Compliance</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters & Export */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-card p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-400" />
              <Select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                options={[
                  { value: 'today', label: 'Today' },
                  { value: 'week', label: 'This Week' },
                  { value: 'month', label: 'This Month' },
                  { value: 'all', label: 'All Time' },
                ]}
              />
            </div>
            <div className="flex items-center gap-2">
              <Building className="w-5 h-5 text-gray-400" />
              <Select
                value={branchFilter}
                onChange={(e) => setBranchFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Branches' },
                  { value: '1', label: 'Vientiane Main' },
                  { value: '2', label: 'Luang Prab' },
                  { value: '3', label: 'Pakse' },
                ]}
              />
            </div>
            <div className="flex-1"></div>
            <Button variant="outline" onClick={loadData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={handleExport} isLoading={isExporting}>
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>
      </div>

      {/* Team Performance Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Team Performance</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sales Rep</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Converted</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversion Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {getRepPerformance().map((rep) => (
                  <tr key={rep.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                          <span className="text-sm font-medium text-primary-600">
                            {rep.name.charAt(0)}
                          </span>
                        </div>
                        <span className="ml-3 font-medium text-gray-900">{rep.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                      {rep.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                      {rep.converted}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        parseFloat(rep.rate) >= 20 ? 'bg-green-100 text-green-800' :
                        parseFloat(rep.rate) >= 10 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {rep.rate}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {parseFloat(rep.rate) >= 15 ? (
                        <span className="text-green-600 text-sm">On Track</span>
                      ) : (
                        <span className="text-yellow-600 text-sm">Needs Attention</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BranchManager;