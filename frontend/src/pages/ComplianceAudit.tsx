// Compliance Officer - Audit Log Viewer
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, clearTokens, getAccessToken } from '../services/api';
import { User } from '../types';
import { Button } from '../components/Button';
import { Input, Select } from '../components/Input';
import { 
  Shield, Search, Calendar, Download, 
  LogOut, RefreshCw, FileText,
  Eye, Edit, Trash2, Download
} from 'lucide-react';

interface AuditLog {
  id: number;
  lead_id: number;
  user_id: number | null;
  user_name: string | null;
  action: string;
  old_status: string | null;
  new_status: string | null;
  details: string | null;
  ip_address: string | null;
  created_at: string;
}

export function ComplianceAudit() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('week');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      navigate('/login');
      return;
    }
    loadData();
  }, [navigate, actionFilter, dateRange]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      
      // In production, fetch from compliance API endpoint
      // For now, mock data
      setLogs([
        {
          id: 1,
          lead_id: 123,
          user_id: 1,
          user_name: 'Somchai',
          action: 'view',
          old_status: null,
          new_status: null,
          details: 'Viewed lead details',
          ip_address: '192.168.1.100',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          lead_id: 123,
          user_id: 1,
          user_name: 'Somchai',
          action: 'status_change',
          old_status: 'new',
          new_status: 'contacted',
          details: 'Called customer',
          ip_address: '192.168.1.100',
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
          id: 3,
          lead_id: 124,
          user_id: 2,
          user_name: 'Somsak',
          action: 'export',
          old_status: null,
          new_status: null,
          details: 'Exported 50 leads',
          ip_address: '192.168.1.101',
          created_at: new Date(Date.now() - 7200000).toISOString(),
        },
      ]);
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

  const handleExportAudit = () => {
    // Export audit logs as CSV
    const csvContent = [
      ['ID', 'Lead ID', 'User', 'Action', 'Old Status', 'New Status', 'IP Address', 'Timestamp'],
      ...logs.map(log => [
        log.id,
        log.lead_id,
        log.user_name,
        log.action,
        log.old_status || '',
        log.new_status || '',
        log.ip_address || '',
        log.created_at,
      ]),
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_log_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const getActionIcon = (action: string) => {
    const icons: Record<string, any> = {
      view: Eye,
      create: FileText,
      update: Edit,
      status_change: Edit,
      export: Download,
      delete: Trash2,
    };
    return icons[action] || FileText;
  };

  const getActionBadge = (action: string) => {
    const badges: Record<string, string> = {
      view: 'bg-blue-100 text-blue-800',
      create: 'bg-green-100 text-green-800',
      update: 'bg-yellow-100 text-yellow-800',
      status_change: 'bg-purple-100 text-purple-800',
      export: 'bg-gray-100 text-gray-800',
      delete: 'bg-red-100 text-red-800',
    };
    return badges[action] || 'bg-gray-100 text-gray-800';
  };

  const filteredLogs = logs.filter(log => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        log.lead_id.toString().includes(query) ||
        log.user_name?.toLowerCase().includes(query) ||
        log.details?.toLowerCase().includes(query)
      );
    }
    if (actionFilter !== 'all' && log.action !== actionFilter) {
      return false;
    }
    return true;
  });

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading audit logs...</p>
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
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Compliance Audit</h1>
                <p className="text-xs text-gray-500">Audit Log Viewer</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">{user?.full_name}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-xl shadow-card p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px]">
              <Input
                placeholder="Search by lead ID, user, or details..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon={<Search className="w-5 h-5" />}
              />
            </div>
            <Select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Actions' },
                { value: 'view', label: 'View' },
                { value: 'create', label: 'Create' },
                { value: 'status_change', label: 'Status Change' },
                { value: 'export', label: 'Export' },
                { value: 'delete', label: 'Delete' },
              ]}
            />
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
            <Button variant="outline" onClick={loadData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={handleExportAudit}>
              <Download className="w-4 h-4 mr-2" />
              Export Logs
            </Button>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Audit Log</h2>
            <span className="text-sm text-gray-500">{filteredLogs.length} entries</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lead ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredLogs.map((log) => {
                  const Icon = getActionIcon(log.action);
                  return (
                    <tr 
                      key={log.id} 
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedLog(log)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="font-medium text-gray-900">#{log.lead_id}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {log.user_name || 'System'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getActionBadge(log.action)}`}>
                          <Icon className="w-3 h-3" />
                          {log.action.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {log.details || (log.old_status && log.new_status ? `${log.old_status} → ${log.new_status}` : '-')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {log.ip_address || '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          {filteredLogs.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No audit logs found matching your criteria.
            </div>
          )}
        </div>
      </div>

      {/* Log Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">Audit Log Details</h3>
              <Button variant="ghost" size="sm" onClick={() => setSelectedLog(null)}>
                ×
              </Button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Lead ID</p>
                <p className="font-medium">#{selectedLog.lead_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">User</p>
                <p className="font-medium">{selectedLog.user_name || 'System'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Action</p>
                <p className="font-medium">{selectedLog.action}</p>
              </div>
              {selectedLog.old_status && selectedLog.new_status && (
                <div>
                  <p className="text-sm text-gray-500">Status Change</p>
                  <p className="font-medium">{selectedLog.old_status} → {selectedLog.new_status}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500">Details</p>
                <p className="font-medium">{selectedLog.details || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">IP Address</p>
                <p className="font-medium">{selectedLog.ip_address || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Timestamp</p>
                <p className="font-medium">{formatDate(selectedLog.created_at)}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ComplianceAudit;