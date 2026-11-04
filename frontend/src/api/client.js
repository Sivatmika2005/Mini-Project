const API_BASE = 'http://localhost:8001/api';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('session_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(data.detail || data.message || 'An error occurred');
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const api = {
  // Auth
  login: (username_or_email, password) =>
    apiRequest('/auth/login', { method: 'POST', body: { username_or_email, password } }),
  register: (username, email, password) =>
    apiRequest('/auth/register', { method: 'POST', body: { username, email, password } }),
  logout: () => apiRequest('/auth/logout', { method: 'POST' }),
  getMe: () => apiRequest('/auth/me'),
  resetPasswordRequest: (email) =>
    apiRequest('/auth/reset-password-request', { method: 'POST', body: { email } }),
  confirmPasswordReset: (oob_code, new_password) =>
    apiRequest('/auth/confirm-reset', { method: 'POST', body: { oob_code, new_password } }),

  // User Settings
  getSettings: () => apiRequest('/user/settings'),
  saveSettings: (settings) => apiRequest('/user/settings', { method: 'POST', body: settings }),
  updateName: (new_name) => apiRequest('/user/update-name', { method: 'POST', body: { new_name } }),

  // Checkins
  getLatestCheckin: () => apiRequest('/checkins/latest'),
  getCheckins: (limit) => apiRequest(`/checkins${limit ? `?limit=${limit}` : ''}`),
  addCheckin: (checkinData) => apiRequest('/checkins', { method: 'POST', body: checkinData }),

  // Journals
  getJournals: () => apiRequest('/journals'),
  addJournal: (journalData) => apiRequest('/journals', { method: 'POST', body: journalData }),
  deleteJournal: (id) => apiRequest(`/journals/${id}`, { method: 'DELETE' }),
  summarizeJournals: () => apiRequest('/journals/summarize', { method: 'POST' }),

  // Chat & Conversations
  getConversations: () => apiRequest('/chat/conversations'),
  createConversation: (title) =>
    apiRequest('/chat/conversations', { method: 'POST', body: { title } }),
  updateConversationTitle: (convId, title) =>
    apiRequest(`/chat/conversations/${convId}`, { method: 'PUT', body: { title } }),
  deleteConversation: (convId) =>
    apiRequest(`/chat/conversations/${convId}`, { method: 'DELETE' }),
  getMessages: (convId) => apiRequest(`/chat/conversations/${convId}/messages`),
  sendMessage: (convId, message) =>
    apiRequest(`/chat/conversations/${convId}/messages`, { method: 'POST', body: { message } }),

  // Companion
  companionChat: (message) => apiRequest('/companion/chat', { method: 'POST', body: { message } }),

  // Translations
  getTranslations: () => apiRequest('/translations'),

  // Professional Discovery
  getProfessionalsMetadata: () => apiRequest('/professionals/metadata'),
  getNearbyProfessionals: (lat, lng, radius = 25, category = '', sortBy = 'distance') => {
    const params = new URLSearchParams({ lat, lng, radius, sort_by: sortBy });
    if (category && category !== 'All') params.append('category', category);
    return apiRequest(`/professionals/nearby?${params.toString()}`);
  },
  searchProfessionals: (searchParams = {}) => {
    const params = new URLSearchParams();
    Object.entries(searchParams).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '' && v !== 'All' && v !== 'All Cities') {
        params.append(k, v);
      }
    });
    return apiRequest(`/professionals/search?${params.toString()}`);
  },
};
