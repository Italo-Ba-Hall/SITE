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
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [showLeadDetails, setShowLeadDetails] = useState(false);
  
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

  const handleViewLeadDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setShowLeadDetails(true);
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

  const getStatusIcon = (status: string) => {
    const icons = {
      new: '🆕',
      contacted: '📞',
      qualified: '✅',
      converted: '💰',
      lost: '❌'
    };
    return icons[status as keyof typeof icons] || '❓';
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center">
                <span className="mr-3">🎯</span>
                Dashboard /-HALL-DEV
              </h1>
              <p className="text-gray-600 text-lg">
                Gerencie leads e acompanhe notificações em tempo real
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={loadDashboardData}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
              >
                <span>🔄</span>
                <span>Atualizar</span>
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <span className="text-2xl">👥</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total de Leads</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_leads}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <span className="text-2xl">✅</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Qualificados</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.leads_by_status.qualified || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <span className="text-2xl">💬</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Conversas</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_conversations}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-200">
              <div className="flex items-center">
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <span className="text-2xl">🔔</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Notificações</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.unread_notifications}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <div className="flex flex-wrap gap-4 items-center">
            <label className="text-sm font-medium text-gray-700">Filtrar por Status:</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos os Status</option>
              <option value="new">🆕 Novos</option>
              <option value="contacted">📞 Contactados</option>
              <option value="qualified">✅ Qualificados</option>
              <option value="converted">💰 Convertidos</option>
              <option value="lost">❌ Perdidos</option>
            </select>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Leads Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <span className="mr-2">👥</span>
                  Leads Capturados
                </h2>
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
                        Ações
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {leads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50 transition-colors duration-150">
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
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${lead.qualification_score * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-900">
                              {Math.round(lead.qualification_score * 100)}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(lead.status)}`}>
                            <span className="mr-1">{getStatusIcon(lead.status)}</span>
                            {lead.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleViewLeadDetails(lead)}
                              className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                            >
                              👁️ Ver
                            </button>
                            <select
                              value={lead.status}
                              onChange={(e) => updateLeadStatus(lead.session_id, e.target.value)}
                              className="border border-gray-300 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
                            >
                              <option value="new">🆕 Novo</option>
                              <option value="contacted">📞 Contactado</option>
                              <option value="qualified">✅ Qualificado</option>
                              <option value="converted">💰 Convertido</option>
                              <option value="lost">❌ Perdido</option>
                            </select>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {leads.length === 0 && (
                <div className="px-6 py-12 text-center text-gray-500">
                  <div className="text-4xl mb-4">📭</div>
                  <p className="text-lg font-medium">Nenhum lead encontrado</p>
                  <p className="text-sm">Os leads aparecerão aqui quando forem capturados</p>
                </div>
              )}
            </div>
          </div>

          {/* Notifications Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <span className="mr-2">🔔</span>
                  Notificações Recentes
                </h2>
              </div>
              
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="px-6 py-8 text-center text-gray-500">
                    <div className="text-4xl mb-4">🔕</div>
                    <p className="text-lg font-medium">Nenhuma notificação</p>
                    <p className="text-sm">As notificações aparecerão aqui</p>
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`px-6 py-4 ${!notification.is_read ? 'bg-blue-50 border-l-4 border-blue-400' : ''}`}
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

        {/* Lead Details Modal */}
        {showLeadDetails && selectedLead && (
          <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-[9999] p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Detalhes do Lead</h3>
                  <button
                    onClick={() => setShowLeadDetails(false)}
                    className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Informações Pessoais</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Nome:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedLead.name || 'Não informado'}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Email:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedLead.email}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Cargo:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedLead.role || 'Não informado'}</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Empresa:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedLead.company || 'Não informado'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Qualificação</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Score:</span>
                        <span className="ml-2 text-sm text-gray-900">{Math.round(selectedLead.qualification_score * 100)}%</span>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Status:</span>
                        <span className={`ml-2 inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedLead.status)}`}>
                          <span className="mr-1">{getStatusIcon(selectedLead.status)}</span>
                          {selectedLead.status}
                        </span>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Data:</span>
                        <span className="ml-2 text-sm text-gray-900">{formatDate(selectedLead.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {selectedLead.pain_points && selectedLead.pain_points.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Pontos de Dor</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedLead.pain_points.map((point, index) => (
                        <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedLead.recommended_solutions && selectedLead.recommended_solutions.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Soluções Recomendadas</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedLead.recommended_solutions.map((solution, index) => (
                        <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                          {solution}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {selectedLead.conversation_summary && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Resumo da Conversa</h4>
                    <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                      {selectedLead.conversation_summary}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 