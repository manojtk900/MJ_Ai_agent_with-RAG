import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { v4 as uuidv4 } from 'uuid'

export const useChatStore = create(
  persist(
    (set, get) => ({
      conversations: {},      // { [id]: { id, title, messages: [] } }
      activeConversationId: null,

      createNewConversation: () => {
        const id = uuidv4()
        set(state => ({
          conversations: {
            ...state.conversations,
            [id]: { id, title: 'New Conversation', messages: [], createdAt: Date.now() },
          },
          activeConversationId: id,
        }))
        return id
      },

      setActiveConversation: (id) => set({ activeConversationId: id }),

      addMessage: (conversationId, message) => {
        set(state => {
          const conv = state.conversations[conversationId] || {
            id: conversationId,
            title: 'Conversation',
            messages: [],
            createdAt: Date.now(),
          }
          const updatedMessages = [...conv.messages, { ...message, id: uuidv4(), timestamp: new Date().toISOString() }]
          return {
            conversations: {
              ...state.conversations,
              [conversationId]: { ...conv, messages: updatedMessages },
            },
          }
        })
      },

      updateConversationTitle: (conversationId, title) => {
        set(state => ({
          conversations: {
            ...state.conversations,
            [conversationId]: { ...state.conversations[conversationId], title },
          },
        }))
      },

      getMessages: (conversationId) => {
        return get().conversations[conversationId]?.messages || []
      },

      getAllConversations: () => {
        return Object.values(get().conversations).sort((a, b) => b.createdAt - a.createdAt)
      },

      deleteConversation: (id) => {
        set(state => {
          const { [id]: _, ...rest } = state.conversations
          return { conversations: rest, activeConversationId: null }
        })
      },
    }),
    {
      name: 'mj-chat-store',
      partialize: (state) => ({ conversations: state.conversations }),
    }
  )
)
