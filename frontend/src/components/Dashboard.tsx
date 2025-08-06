import React, { useState, useEffect, useCallback } from 'react';
import { apiCall } from '../hooks/useApi';

interface Lead {
  id: number;
  session_id: string;
  name: string;
  email: string;
  company: string;
  role: string;
  qualification_score: number;
  status: string;
  created_at: string;
  conversation_summary: string;
  pain_points: string[];
  recommended_solutions: string[];
}

interface Notification {
  id: number;
  lead_id: number;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
  lead_name: string;
  lead_email: string;
}

interface DashboardStats {
  total_leads: number;
  leads_by_status: Record<string, number>;
  total_conversations: number;
  unread_notifications: number;
}

const Dashboard: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Carregar leads
      const leadsResponse = await apiCall<{leads: Lead[], stats: DashboardStats, total_leads: number}>('/dashboard/leads', {
        params: { status: selectedStatus || undefined, limit: 100 }
      });
      setLeads(leadsResponse.leads || []);
      
      // Carregar notificações
      const notificationsResponse = await apiCall<{notifications: Notification[], total: number}>('/dashboard/notifications');
      setNotifications(notificationsResponse.notifications || []);
      
      // Carregar estatísticas
      const statsResponse = await apiCall<{database: DashboardStats, chat: Record<string, unknown>, llm: Record<string, unknown>, timestamp: string}>('/dashboard/stats');
      setStats(statsResponse.database);
      
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedStatus]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const updateLeadStatus = async (sessionId: string, newStatus: string) => {
    try {
      await apiCall<{success: boolean, message: string, session_id: string, new_status: string}>(`/dashboard/leads/${sessionId}/status`, {
        method: 'PUT',
        data: { status: newStatus }
      });
      
      // Recarregar dados
      loadDashboardData();
      
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao atualizar status:', error);
    }
  };

  const markNotificationRead = async (notificationId: number) => {
    try {
      await apiCall<{success: boolean, message: string, notification_id: number}>(`/dashboard/notifications/${notificationId}/read`, {
        method: 'PUT'
      });
      
      // Recarregar notificações
      const notificationsResponse = await apiCall<{notifications: Notification[], total: number}>('/dashboard/notifications');
      setNotifications(notificationsResponse.notifications || []);
      
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao marcar notificação:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  const getStatusColor = (status: string) => {
    const colors = {
      new: 'bg-blue-100 text-blue-800',
      contacted: 'bg-yellow-100 text-yellow-800',
      qualified: 'bg-green-100 text-green-800',
      converted: 'bg-purple-100 text-purple-800',
      lost: 'bg-red-100 text-red-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎯 Dashboard /-HALL-DEV
          </h1>
          <p className="text-gray-600">
            Gerencie leads e acompanhe notificações em tempo real
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <span className="text-2xl">👥</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total de Leads</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_leads}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <span className="text-2xl">✅</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Qualificados</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.leads_by_status.qualified || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <span className="text-2xl">💬</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Conversas</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_conversations}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <span className="text-2xl">🔔</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Notificações</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.unread_notifications}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-wrap gap-4 items-center">
            <label className="text-sm font-medium text-gray-700">Filtrar por Status:</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">Todos os Status</option>
              <option value="new">Novos</option>
              <option value="contacted">Contactados</option>
              <option value="qualified">Qualificados</option>
              <option value="converted">Convertidos</option>
              <option value="lost">Perdidos</option>
            </select>
            
            <button
              onClick={loadDashboardData}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
            >
              🔄 Atualizar
            </button>
          </div>
        </div>

        {/* Leads Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Leads Capturados</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lead
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Empresa
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {lead.name || 'Sem nome'}
                        </div>
                        <div className="text-sm text-gray-500">{lead.email}</div>
                        <div className="text-xs text-gray-400">{lead.role}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {lead.company || 'Não informado'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${lead.qualification_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">
                          {Math.round(lead.qualification_score * 100)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(lead.status)}`}>
                        {lead.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(lead.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <select
                        value={lead.status}
                        onChange={(e) => updateLeadStatus(lead.session_id, e.target.value)}
                        className="border border-gray-300 rounded px-2 py-1 text-xs"
                      >
                        <option value="new">Novo</option>
                        <option value="contacted">Contactado</option>
                        <option value="qualified">Qualificado</option>
                        <option value="converted">Convertido</option>
                        <option value="lost">Perdido</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Notificações Recentes</h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {notifications.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                Nenhuma notificação não lida
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`px-6 py-4 ${!notification.is_read ? 'bg-blue-50' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-900">
                          {notification.message}
                        </span>
                        {!notification.is_read && (
                          <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Nova
                          </span>
                        )}
                      </div>
                      <div className="mt-1 text-sm text-gray-500">
                        {notification.lead_name && (
                          <span>Lead: {notification.lead_name} ({notification.lead_email})</span>
                        )}
                        <span className="ml-2">• {formatDate(notification.created_at)}</span>
                      </div>
                    </div>
                    {!notification.is_read && (
                      <button
                        onClick={() => markNotificationRead(notification.id)}
                        className="ml-4 text-sm text-blue-600 hover:text-blue-800"
                      >
                        Marcar como lida
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 