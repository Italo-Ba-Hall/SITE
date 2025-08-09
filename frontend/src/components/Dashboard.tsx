import React, { useState, useEffect, useCallback, useMemo } from 'react';
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

interface ConversationSummary {
  id: number;
  session_id: string;
  summary: string;
  created_at: string;
  lead_name?: string;
  lead_email?: string;
  messages?: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: string | Date;
  }>;
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
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [selectedConversation, setSelectedConversation] = useState<ConversationSummary | null>(null);
  const [showLeadDetails, setShowLeadDetails] = useState(false);
  const [showConversationDetails, setShowConversationDetails] = useState(false);
  const [activeTab, setActiveTab] = useState<'leads' | 'conversations'>('conversations');
  const [leadSearch, setLeadSearch] = useState('');
  const [leadStatusFilter, setLeadStatusFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [onlyCollected, setOnlyCollected] = useState(false);

  const sortedConversations = useMemo(() => {
    const clone = [...conversations];
    return clone.sort((a, b) => {
      const aCollected = Number(Boolean(a.lead_name) && Boolean(a.lead_email));
      const bCollected = Number(Boolean(b.lead_name) && Boolean(b.lead_email));
      if (aCollected !== bCollected) return bCollected - aCollected; // coletados primeiro
      const aTime = new Date(a.created_at).getTime();
      const bTime = new Date(b.created_at).getTime();
      return bTime - aTime; // mais recentes primeiro
    });
  }, [conversations]);
  
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Carregar leads
      const leadsResponse = await apiCall<{leads: Lead[], stats: DashboardStats, total_leads: number}>('/dashboard/leads', {
        params: { limit: 100 }
      });
      setLeads(leadsResponse.leads || []);
      
      // Carregar conversas
      const conversationsResponse = await apiCall<{summaries: ConversationSummary[]}>('/dashboard/conversation-summaries', {
        params: { limit: 50 }
      });
      setConversations(conversationsResponse.summaries || []);
      
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
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const updateLeadStatus = async (sessionId: string, newStatus: string) => {
    // Atualização otimista
    const prevLeads = leads;
    setLeads((lst) => lst.map((l) => (l.session_id === sessionId ? { ...l, status: newStatus } : l)));
    try {
      await apiCall<{success: boolean, message: string, session_id: string, new_status: string}>(`/dashboard/leads/${sessionId}/status`, {
        method: 'PUT',
        params: { status: newStatus }
      });
      // Recarregar stats/notifications de leve
      loadDashboardData();
    } catch (error) {
      // Reverter em caso de erro
      setLeads(prevLeads);
      // eslint-disable-next-line no-console
      console.error('Erro ao atualizar status:', error);
    }
  };

  const markNotificationRead = async (notificationId: number) => {
    try {
      await apiCall<{success: boolean, message: string, notification_id: number}>(`/dashboard/notifications/${notificationId}/read`, {
        method: 'PUT'
      });
      // Atualização local
      setNotifications((items) => items.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n)));
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao marcar notificação como lida:', error);
    }
  };

  // Filtros e paginação de leads (client-side)
  const filteredLeads = useMemo(() => {
    const term = leadSearch.trim().toLowerCase();
    const byStatus = (l: Lead) => (!leadStatusFilter ? true : l.status === leadStatusFilter);
    const byTerm = (l: Lead) =>
      !term ||
      [l.name, l.email, l.company, l.role]
        .filter(Boolean)
        .map((v) => String(v).toLowerCase())
        .some((v) => v.includes(term));
    const byCollected = (l: Lead) => (!onlyCollected ? true : Boolean(l.name) && Boolean(l.email));
    return leads.filter((l) => byStatus(l) && byTerm(l) && byCollected(l));
  }, [leads, leadSearch, leadStatusFilter, onlyCollected]);

  const paginatedLeads = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredLeads.slice(start, start + pageSize);
  }, [filteredLeads, page, pageSize]);

  useEffect(() => {
    // Resetar para primeira página ao mudar filtros
    setPage(1);
  }, [leadSearch, leadStatusFilter, onlyCollected]);

  const computedStats = useMemo(() => {
    if (stats) return stats;
    // Fallback básico quando stats não disponíveis na API
    const leadsByStatus = filteredLeads.reduce<Record<string, number>>((acc, l) => {
      acc[l.status] = (acc[l.status] || 0) + 1;
      return acc;
    }, {});
    return {
      total_leads: leads.length,
      leads_by_status: leadsByStatus,
      total_conversations: conversations.length,
      unread_notifications: notifications.filter((n) => !n.is_read).length,
    } as DashboardStats;
  }, [stats, filteredLeads, leads.length, conversations.length, notifications]);

  const handleViewLeadDetails = (lead: Lead) => {
    setSelectedLead(lead);
    setShowLeadDetails(true);
  };

  const handleViewConversationDetails = useCallback(async (conversation: ConversationSummary) => {
    try {
      const details = await apiCall<{
        session_id: string;
        messages: ConversationSummary['messages'];
        summary?: unknown;
        user_profile?: { name?: string; email?: string } | null;
      }>(`/chat/conversation/${conversation.session_id}`);

      const enriched: ConversationSummary = {
        ...conversation,
        messages: details.messages || conversation.messages || [],
        lead_name: conversation.lead_name || details.user_profile?.name,
        lead_email: conversation.lead_email || details.user_profile?.email,
      };

      setSelectedConversation(enriched);
      setShowConversationDetails(true);
    } catch (err) {
      setSelectedConversation(conversation);
      setShowConversationDetails(true);
      // eslint-disable-next-line no-console
      console.error('Erro ao carregar conversa completa:', err);
    }
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return 'bg-blue-100 text-blue-800';
      case 'contacted': return 'bg-yellow-100 text-yellow-800';
      case 'qualified': return 'bg-green-100 text-green-800';
      case 'converted': return 'bg-purple-100 text-purple-800';
      case 'lost': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new': return '🆕';
      case 'contacted': return '📞';
      case 'qualified': return '✅';
      case 'converted': return '💰';
      case 'lost': return '❌';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-lg text-gray-600">Carregando dashboard...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <span className="mr-3">⚙️</span>
                Dashboard /-HALL-DEV
              </h1>
              <p className="text-gray-600 mt-2">
                Gerencie leads e acompanhe notificações em tempo real
              </p>
            </div>
            <button
              onClick={loadDashboardData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center"
            >
              <span className="mr-2">🔄</span>
              Atualizar
            </button>
          </div>
        </div>

        {/* Stats Cards - formato de cards modernos */}
        {computedStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <span className="text-2xl">👥</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total de Leads</p>
                  <p className="text-3xl font-bold text-gray-900">{computedStats.total_leads}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-lg">
                  <span className="text-2xl">✅</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Qualificados</p>
                  <p className="text-3xl font-bold text-gray-900">{computedStats.leads_by_status.qualified || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <span className="text-2xl">💬</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Conversas</p>
                  <p className="text-3xl font-bold text-gray-900">{computedStats.total_conversations}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center">
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <span className="text-2xl">🔔</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Notificações</p>
                  <p className="text-3xl font-bold text-gray-900">{computedStats.unread_notifications}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border border-gray-200">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('conversations')}
              className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors duration-200 ${
                activeTab === 'conversations'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              💬 Conversas ({conversations.length})
            </button>
            <button
              onClick={() => setActiveTab('leads')}
              className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors duration-200 ${
                activeTab === 'leads'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              👥 Leads ({leads.length})
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <span className="mr-2">{activeTab === 'conversations' ? '💬' : '👥'}</span>
                  {activeTab === 'conversations' ? 'Conversas Recentes' : 'Leads Capturados'}
                </h2>
              </div>
              
              {activeTab === 'conversations' ? (
                /* Conversas */
                <div className="overflow-y-auto max-h-[70vh]">
                      {sortedConversations.length > 0 ? (
                    <div className="divide-y divide-gray-200">
                      {sortedConversations.map((conversation) => (
                        <div key={conversation.id} className="p-6 hover:bg-gray-50 transition-colors duration-150">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                                <span className="text-sm font-medium text-gray-900">
                                  Sessão: {conversation.session_id}
                                </span>
                                <span className="text-xs text-gray-500">
                                  {formatDate(conversation.created_at)}
                                </span>
                            {/* Indicadores de captura */}
                            {conversation.lead_name ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Nome ✅</span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Nome —</span>
                            )}
                            {conversation.lead_email ? (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Email ✅</span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">Email —</span>
                            )}
                              </div>
                              <p className="text-sm text-gray-600 line-clamp-3">
                                {conversation.summary}
                              </p>
                            </div>
                            <button
                              onClick={() => handleViewConversationDetails(conversation)}
                              className="ml-4 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm font-medium transition-colors duration-200"
                            >
                              👁️ Ver
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 text-center">
                      <div className="text-gray-400 text-6xl mb-4">💬</div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma conversa encontrada</h3>
                      <p className="text-gray-500">As conversas aparecerão aqui quando forem iniciadas</p>
                    </div>
                  )}
                </div>
              ) : (
                /* Leads */
                <div className="overflow-x-auto">
                  {/* Filtros */}
                  <div className="p-4 border-b border-gray-200 flex flex-col md:flex-row md:items-center md:space-x-4 space-y-3 md:space-y-0">
                    <input
                      type="text"
                      value={leadSearch}
                      onChange={(e) => setLeadSearch(e.target.value)}
                      placeholder="Buscar por nome, email, empresa..."
                      className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <select
                      value={leadStatusFilter}
                      onChange={(e) => setLeadStatusFilter(e.target.value)}
                      className="w-full md:w-48 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="">Todos os status</option>
                      <option value="new">Novo</option>
                      <option value="contacted">Contactado</option>
                      <option value="qualified">Qualificado</option>
                      <option value="converted">Convertido</option>
                      <option value="lost">Perdido</option>
                    </select>
                    <label className="inline-flex items-center space-x-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={onlyCollected}
                        onChange={(e) => setOnlyCollected(e.target.checked)}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                      />
                      <span>Somente com Nome e Email</span>
                    </label>
                  </div>
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
                      {paginatedLeads.length > 0 ? (
                        paginatedLeads.map((lead) => (
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
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{lead.company || 'N/A'}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{lead.qualification_score || 0}/100</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(lead.status)}`}>
                                <span className="mr-1">{getStatusIcon(lead.status)}</span>
                                {lead.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleViewLeadDetails(lead)}
                                  className="text-blue-600 hover:text-blue-900 bg-blue-100 hover:bg-blue-200 px-2 py-1 rounded text-xs"
                                >
                                  👁️ Ver
                                </button>
                                <select
                                  value={lead.status}
                                  onChange={(e) => updateLeadStatus(lead.session_id, e.target.value)}
                                  className="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="px-6 py-8 text-center">
                            <div className="text-gray-400 text-6xl mb-4">👥</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum lead encontrado</h3>
                            <p className="text-gray-500">Os leads aparecerão aqui quando forem capturados</p>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                  {/* Paginação */}
                  {filteredLeads.length > pageSize && (
                    <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
                      <div className="text-sm text-gray-600">
                        Mostrando {Math.min((page - 1) * pageSize + 1, filteredLeads.length)}–{Math.min(page * pageSize, filteredLeads.length)} de {filteredLeads.length}
                      </div>
                      <div className="space-x-2">
                        <button
                          onClick={() => setPage((p) => Math.max(1, p - 1))}
                          disabled={page === 1}
                          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm disabled:opacity-50"
                        >
                          Anterior
                        </button>
                        <button
                          onClick={() => setPage((p) => (p * pageSize < filteredLeads.length ? p + 1 : p))}
                          disabled={page * pageSize >= filteredLeads.length}
                          className="px-3 py-1.5 border border-gray-300 rounded-md text-sm disabled:opacity-50"
                        >
                          Próxima
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Notifications Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <span className="mr-2">🔔</span>
                  Notificações Recentes
                </h2>
              </div>
              
              <div className="overflow-y-auto max-h-96">
                {notifications.length > 0 ? (
                  <div className="divide-y divide-gray-200">
                    {notifications.map((notification) => (
                      <div key={notification.id} className={`p-4 ${!notification.is_read ? 'bg-blue-50 border-l-4 border-blue-400' : ''}`}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-sm font-medium text-gray-900">
                                {notification.lead_name || 'Lead'}
                              </span>
                              {!notification.is_read && (
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  Nova
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mb-2">{notification.message}</p>
                            <div className="text-xs text-gray-500">{formatDate(notification.created_at)}</div>
                          </div>
                          {!notification.is_read && (
                            <button
                              onClick={() => markNotificationRead(notification.id)}
                              className="ml-2 text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Marcar lida
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-6 text-center">
                    <div className="text-gray-400 text-4xl mb-4">🔔</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma notificação</h3>
                    <p className="text-gray-500">As notificações aparecerão aqui</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lead Details Modal */}
      {showLeadDetails && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900">Detalhes do Lead</h3>
                <button
                  onClick={() => setShowLeadDetails(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Informações Pessoais</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Nome:</span> {selectedLead.name || 'N/A'}</div>
                    <div><span className="font-medium">Email:</span> {selectedLead.email}</div>
                    <div><span className="font-medium">Cargo:</span> {selectedLead.role || 'N/A'}</div>
                    <div><span className="font-medium">Empresa:</span> {selectedLead.company || 'N/A'}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Qualificação</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Score:</span> {selectedLead.qualification_score || 0}/100</div>
                    <div><span className="font-medium">Status:</span> 
                      <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedLead.status)}`}>
                        <span className="mr-1">{getStatusIcon(selectedLead.status)}</span>
                        {selectedLead.status}
                      </span>
                    </div>
                    <div><span className="font-medium">Criado em:</span> {formatDate(selectedLead.created_at)}</div>
                  </div>
                </div>
              </div>
              
              {selectedLead.pain_points && selectedLead.pain_points.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Pontos de Dor</h4>
                  <div className="space-y-1">
                    {selectedLead.pain_points.map((point, index) => (
                      <div key={index} className="text-sm text-gray-600">• {point}</div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedLead.recommended_solutions && selectedLead.recommended_solutions.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Soluções Recomendadas</h4>
                  <div className="space-y-1">
                    {selectedLead.recommended_solutions.map((solution, index) => (
                      <div key={index} className="text-sm text-gray-600">• {solution}</div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedLead.conversation_summary && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Resumo da Conversa</h4>
                  <p className="text-sm text-gray-600">{selectedLead.conversation_summary}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Conversation Details Modal */}
      {showConversationDetails && selectedConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900">Detalhes da Conversa</h3>
                <button
                  onClick={() => setShowConversationDetails(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>
              {/* Indicador de coleta no topo do modal */}
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {selectedConversation.lead_name && selectedConversation.lead_email ? (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Contato completo (Nome + Email)
                  </span>
                ) : (
                  <>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                      Coleta incompleta
                    </span>
                    {!selectedConversation.lead_name && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        Nome —
                      </span>
                    )}
                    {!selectedConversation.lead_email && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        Email —
                      </span>
                    )}
                  </>
                )}
              </div>
            </div>
            
            <div className="px-6 py-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Informações da Sessão</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">ID da Sessão:</span> {selectedConversation.session_id}</div>
                    <div><span className="font-medium">Data:</span> {formatDate(selectedConversation.created_at)}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Resumo da Conversa</h4>
                  <p className="text-sm text-gray-600 leading-relaxed">{selectedConversation.summary}</p>
                </div>

                {selectedConversation.messages && selectedConversation.messages.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Mensagens</h4>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto space-y-3">
                      {selectedConversation.messages.map((m, idx) => (
                        <div key={idx} className={`text-sm ${m.role === 'user' ? 'text-gray-900' : 'text-gray-700'}`}>
                          <span className="font-medium mr-2">{m.role === 'user' ? 'Usuário' : m.role === 'assistant' ? 'Assistente' : 'Sistema'}:</span>
                          <span className="whitespace-pre-wrap break-words">{m.content}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 