import { useState, useCallback, useRef } from 'react'
import api, { chatApi } from '../services/api'
import { useChatStore } from '../store/chatStore'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useChat(conversationId) {
  const [isLoading, setIsLoading] = useState(false)
  const { addMessage, getMessages, createNewConversation, updateConversationTitle } = useChatStore()
  const convId = conversationId || createNewConversation()
  const messages = getMessages(convId)
  const wsRef = useRef(null)

  const sendMessage = useCallback(async (content, options = {}) => {
    if (!content.trim()) return

    // Add user message to store
    addMessage(convId, { role: 'user', content })

    setIsLoading(true)
    console.log("[CHAT REQUEST RECEIVED] Sending to backend via api client...");
    const startTime = performance.now();
    try {
      const data = await chatApi.sendMessage({
        message: content,
        conversation_id: convId,
        autonomy_level: options.autonomy_level ?? 1,
        metadata: options.metadata ?? {},
        input_type: options.input_type ?? 'text',
      })
      const duration = (performance.now() - startTime).toFixed(2);
      console.log(`[OLLAMA RESPONSE RECEIVED] Duration: ${duration} ms`, data);
      addMessage(convId, {
        role: 'assistant',
        content: data.message,
        agent: data.agent_used,
        response_type: data.response_type,
        artifacts: data.artifacts || [],
        requires_approval: data.requires_approval,
        approval_request: data.approval_request,
        latency_ms: data.latency_ms,
      })

      // Auto-title from first message
      if (messages.length === 0) {
        updateConversationTitle(convId, content.slice(0, 50))
      }

      return data
    } catch (error) {
      const errMsg = error.response?.data?.detail || error.message || 'Failed to send message'
      toast.error(errMsg)
      addMessage(convId, {
        role: 'assistant',
        content: `❌ Error: ${errMsg}`,
        is_error: true,
      })
    } finally {
      setIsLoading(false)
    }
  }, [convId, addMessage, messages.length, updateConversationTitle])

  const approveAction = useCallback(async (sessionId, approved) => {
    try {
      const response = await api.post(
        `/api/v1/chat/${sessionId}/approve?approved=${approved}`
      )
      if (approved) {
        addMessage(convId, {
          role: 'assistant',
          content: `✅ ${response.data.result || 'Action completed successfully'}`,
        })
      } else {
        addMessage(convId, {
          role: 'assistant',
          content: '❌ Action rejected by user.',
        })
      }
    } catch (error) {
      toast.error('Approval failed: ' + error.message)
    }
  }, [convId, addMessage])

  // WebSocket streaming (optional)
  const connectWebSocket = useCallback(() => {
    if (wsRef.current) return
    const ws = new WebSocket(`${API_BASE.replace('http', 'ws')}/api/v1/chat/ws/${convId}`)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'message') {
        addMessage(convId, {
          role: 'assistant',
          content: data.content,
          agent: data.agent,
        })
      }
    }
    ws.onerror = () => toast.error('WebSocket connection failed')
    wsRef.current = ws
    return () => ws.close()
  }, [convId, addMessage])

  return { messages, isLoading, sendMessage, approveAction, connectWebSocket }
}
