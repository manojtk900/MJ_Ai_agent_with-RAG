import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const uuidv4 = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
  const r = (Math.random() * 16) | 0
  const v = c === 'x' ? r : (r & 0x3) | 0x8
  return v.toString(16)
})

export const useJarvisStore = create(
  persist(
    (set, get) => ({
      // System Status
      jarvisStatus: 'ONLINE', // ONLINE | LISTENING | PROCESSING | THINKING | ALERT
      activeAgent: 'Controller',
      autonomyLevel: 1, // 0=Manual, 1=Ask, 2=Auto-Safe, 3=Full-Auto
      
      // Voice & Audio State
      isVoiceActive: false,
      isListening: false,
      isSpeaking: false,
      audioLevel: 0, // 0 to 100 for visualizer
      
      // Health Telemetry
      systemHealth: {
        status: 'healthy',
        pingMs: 14,
        cpuUsage: 12.4,
        ramUsage: 34.8,
        services: { api: 'up', postgresql: 'up', redis: 'up', agents: 'ready' },
      },

      // Chat Sessions
      conversations: {},
      activeConversationId: null,

      // Actions
      setJarvisStatus: (status) => set({ jarvisStatus: status }),
      setActiveAgent: (agent) => set({ activeAgent: agent }),
      setAutonomyLevel: (level) => set({ autonomyLevel: level }),
      setVoiceActive: (active) => set({ isVoiceActive: active }),
      setListening: (listening) => set({ isListening: listening }),
      setSpeaking: (speaking) => set({ isSpeaking: speaking }),
      setAudioLevel: (level) => set({ audioLevel: level }),
      setSystemHealth: (health) => set({ systemHealth: health }),

      createNewConversation: () => {
        const id = uuidv4()
        const newConv = {
          id,
          title: 'JARVIS Session',
          messages: [
            {
              id: uuidv4(),
              role: 'assistant',
              content: 'Greetings. JARVIS System v4.2 online and operational. All core sub-systems nominal. How may I assist you today, Boss?',
              agent: 'controller_agent',
              timestamp: new Date().toISOString(),
            },
          ],
          createdAt: Date.now(),
        }
        set((state) => ({
          conversations: { ...state.conversations, [id]: newConv },
          activeConversationId: id,
        }))
        return id
      },

      setActiveConversation: (id) => set({ activeConversationId: id }),

      addMessage: (conversationId, message) => {
        set((state) => {
          const conv = state.conversations[conversationId] || {
            id: conversationId,
            title: 'JARVIS Session',
            messages: [],
            createdAt: Date.now(),
          }
          const newMsg = {
            ...message,
            id: message.id || uuidv4(),
            timestamp: message.timestamp || new Date().toISOString(),
          }
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: {
                ...conv,
                messages: [...conv.messages, newMsg],
              },
            },
          }
        })
      },

      clearConversation: (id) => {
        set((state) => {
          const { [id]: _, ...rest } = state.conversations
          return { conversations: rest, activeConversationId: null }
        })
      },
    }),
    {
      name: 'jarvis-tactical-store',
      partialize: (state) => ({ conversations: state.conversations, autonomyLevel: state.autonomyLevel }),
    }
  )
)
