import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutes (300,000 ms)
})

export const chatApi = {
  // Send message to main agent workflow (POST /api/v1/chat/)
  sendMessage: async (data) => {
    console.log("Sending chat request to backend:", data);
    const startTime = performance.now();
    try {
      const response = await api.post('/api/v1/chat/', {
        message: data.message,
        conversation_id: data.conversation_id || null,
        user_id: data.user_id || 'jarvis-user',
        autonomy_level: data.autonomy_level ?? 1,
        metadata: data.metadata || {},
        input_type: data.input_type || 'text',
      });
      const duration = (performance.now() - startTime).toFixed(2);
      console.log("Response received from backend:", response.data);
      console.log("Request duration:", duration, "ms");
      return response.data;
    } catch (error) {
      const duration = (performance.now() - startTime).toFixed(2);
      console.error("Chat request failed after duration:", duration, "ms", error);
      throw error;
    }
  },

  // Approve action (POST /api/v1/chat/{session_id}/approve)
  approveAction: async (sessionId, approved) => {
    const response = await api.post(`/api/v1/chat/${sessionId}/approve?approved=${approved}`)
    return response.data
  },
}

export const systemApi = {
  // Health check (GET /health/detailed)
  getDetailedHealth: async () => {
    try {
      const response = await api.get('/health/detailed')
      return response.data
    } catch (e) {
      return {
        status: 'degraded',
        version: '1.0.0',
        checks: {
          api: { status: 'down', error: e.message },
          postgresql: { status: 'down' },
          redis: { status: 'down' },
        },
      }
    }
  },

  // Get agent fleet (GET /api/v1/agents/)
  getAgents: async () => {
    try {
      const response = await api.get('/api/v1/agents/')
      return response.data
    } catch (e) {
      return []
    }
  },

  // Get tools manifest (GET /api/v1/tools/manifest)
  getToolsManifest: async () => {
    try {
      const response = await api.get('/api/v1/tools/manifest')
      return response.data
    } catch (e) {
      return { tools: [] }
    }
  },
}

export default api
