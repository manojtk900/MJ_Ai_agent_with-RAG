import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { 
  Send, Mic, MicOff, Terminal, Zap, Shield, CheckCircle, 
  AlertCircle, Sparkles, Loader2, Paperclip, FileText, Code2, 
  Bot, RefreshCw, ChevronRight, Play
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useJarvisStore } from '../../store/jarvisStore'
import { chatApi } from '../../services/api'
import toast from 'react-hot-toast'

const AGENT_COLORS = {
  controller_agent: '#00f0ff',
  chat_agent: '#0072ff',
  search_agent: '#00ff9d',
  research_agent: '#7000ff',
  memory_agent: '#a855f7',
  execution_agent: '#ffb700',
  browser_agent: '#ec4899',
  file_agent: '#14b8a6',
  system_agent: '#ff0055',
  project_manager_agent: '#3b82f6',
}

function MessageBubble({ message, onApprove }) {
  const isUser = message.role === 'user'
  const agentColor = AGENT_COLORS[message.agent] || '#00f0ff'

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 select-text`}
    >
      {!isUser && (
        <div 
          className="w-9 h-9 rounded-xl flex items-center justify-center mr-3 mt-1 flex-shrink-0 border shadow-neonCyan"
          style={{ backgroundColor: 'rgba(5, 15, 35, 0.9)', borderColor: agentColor }}
        >
          <Zap size={18} style={{ color: agentColor }} className="animate-pulse" />
        </div>
      )}

      <div className="max-w-[85%] md:max-w-[75%]">
        {!isUser && message.agent && (
          <div className="flex items-center gap-2 mb-1.5 ml-1">
            <span className="text-[10px] font-hud font-bold px-2 py-0.5 rounded bg-jarvis-card border border-jarvis-border/40 text-jarvis-cyan uppercase">
              {message.agent.replace(/_/g, ' ')}
            </span>
            {message.latency_ms && (
              <span className="text-[10px] font-mono text-jarvis-muted">
                ⚡ {message.latency_ms}ms
              </span>
            )}
          </div>
        )}

        <div 
          className={`
            p-4 rounded-2xl text-sm leading-relaxed hud-corner
            ${isUser 
              ? 'bg-gradient-to-r from-[#0072ff]/30 to-[#00f0ff]/30 border border-[#00f0ff]/50 text-white rounded-tr-none shadow-neonBlue' 
              : 'hud-panel text-jarvis-text rounded-tl-none'
            }
          `}
        >
          {isUser ? (
            <p className="font-sans whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-invert max-w-none text-sm">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>{children}</code>
                    )
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Artifact Cards */}
          {message.artifacts?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-jarvis-border/20 flex flex-wrap gap-2">
              {message.artifacts.map((art, idx) => (
                <div key={idx} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-jarvis-card border border-jarvis-cyan/30 text-xs font-mono text-jarvis-cyan">
                  <FileText size={14} />
                  <span>{art.type || 'Artifact'}</span>
                </div>
              ))}
            </div>
          )}

          {/* Human-in-the-Loop Approval Card */}
          {message.requires_approval && (
            <div className="mt-4 p-4 rounded-xl bg-jarvis-amber/10 border border-jarvis-amber/50">
              <div className="flex items-center gap-2 text-jarvis-amber font-hud font-bold text-xs mb-1">
                <AlertCircle size={16} />
                <span>HUMAN APPROVAL REQUIRED</span>
              </div>
              <p className="text-xs text-jarvis-text font-mono mb-3">
                {message.approval_request?.description || 'The agent requires your authorization to perform a high-risk system action.'}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => onApprove(message.session_id, true)}
                  className="px-3 py-1.5 rounded-lg bg-jarvis-green/20 border border-jarvis-green text-jarvis-green font-hud text-xs font-bold hover:bg-jarvis-green/30 flex items-center gap-1.5"
                  id={`btn-approve-${message.id}`}
                >
                  <CheckCircle size={14} /> AUTHORIZE
                </button>
                <button
                  onClick={() => onApprove(message.session_id, false)}
                  className="px-3 py-1.5 rounded-lg bg-jarvis-red/20 border border-jarvis-red text-jarvis-red font-hud text-xs font-bold hover:bg-jarvis-red/30 flex items-center gap-1.5"
                  id={`btn-reject-${message.id}`}
                >
                  <AlertCircle size={14} /> REJECT
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="text-[10px] font-mono text-jarvis-muted mt-1 px-1">
          {message.timestamp && new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </motion.div>
  )
}

export default function ChatInterface() {
  const { conversationId } = useParams()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)

  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const recognitionRef = useRef(null)

  const { 
    conversations, 
    activeConversationId, 
    createNewConversation, 
    addMessage, 
    autonomyLevel,
    setJarvisStatus,
    setActiveAgent,
    setAudioLevel
  } = useJarvisStore()

  const currentConvId = conversationId || activeConversationId

  useEffect(() => {
    if (!currentConvId) {
      createNewConversation()
    }
  }, [currentConvId, createNewConversation])

  const messages = (currentConvId && conversations[currentConvId]?.messages) || []

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const rec = new SpeechRecognition()
      rec.continuous = false
      rec.interimResults = true

      rec.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((res) => res[0].transcript)
          .join('')
        setInput(transcript)
      }

      rec.onend = () => {
        setIsRecording(false)
        setJarvisStatus('ONLINE')
      }

      recognitionRef.current = rec
    }
  }, [setJarvisStatus])

  const toggleVoice = () => {
    if (!recognitionRef.current) {
      toast.error('Voice recognition not supported in this browser.')
      return
    }

    if (isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
      setJarvisStatus('ONLINE')
    } else {
      try {
        recognitionRef.current.start()
        setIsRecording(true)
        setJarvisStatus('LISTENING')
        toast('JARVIS is listening...', { icon: '🎤' })
      } catch (e) {
        setIsRecording(false)
      }
    }
  }

  const handleSend = useCallback(async (textToSend = input) => {
    if (!textToSend.trim() || isLoading) return

    const userMessage = textToSend.trim()
    setInput('')

    // Add User Message
    addMessage(currentConvId, {
      role: 'user',
      content: userMessage,
    })

    setIsLoading(true)
    setJarvisStatus('PROCESSING')
    setActiveAgent('Controller')

    try {
      const data = await chatApi.sendMessage({
        message: userMessage,
        conversation_id: currentConvId,
        autonomy_level: autonomyLevel,
      })

      // Add Assistant Message
      addMessage(currentConvId, {
        role: 'assistant',
        content: data.message,
        agent: data.agent_used || 'controller_agent',
        response_type: data.response_type,
        artifacts: data.artifacts || [],
        requires_approval: data.requires_approval,
        approval_request: data.approval_request,
        session_id: data.session_id,
        latency_ms: data.latency_ms,
      })

      setActiveAgent(data.agent_used || 'Controller')
    } catch (e) {
      const errText = e.response?.data?.detail || e.message || 'System error'
      toast.error(errText)
      addMessage(currentConvId, {
        role: 'assistant',
        content: `❌ **JARVIS System Error**: ${errText}`,
        agent: 'system_agent',
      })
    } finally {
      setIsLoading(false)
      setJarvisStatus('ONLINE')
    }
  }, [input, isLoading, currentConvId, autonomyLevel, addMessage, setJarvisStatus, setActiveAgent])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleApprove = async (sessionId, approved) => {
    try {
      const res = await chatApi.approveAction(sessionId, approved)
      toast.success(res.message || 'Action processed')
      addMessage(currentConvId, {
        role: 'assistant',
        content: approved ? `✅ **Action Authorized**: ${res.result || 'Execution completed.'}` : '❌ **Action Rejected by User.**',
        agent: 'controller_agent',
      })
    } catch (e) {
      toast.error('Approval error: ' + e.message)
    }
  }

  const quickPrompts = [
    '🔍 Run deep research on AI Agent trends 2026',
    '💻 Build a FastAPI REST API endpoint',
    '📊 Generate a 4-week project plan for AgriGuard',
    '📧 Draft a project status report email',
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#020613] text-[#e0f7fc] overflow-hidden relative">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {messages.length === 1 && (
          <div className="my-8 flex flex-col items-center justify-center text-center max-w-xl mx-auto space-y-6">
            <div className="hud-panel p-6 rounded-2xl w-full border border-jarvis-cyan/30 text-center relative overflow-hidden">
              <div className="w-16 h-16 rounded-2xl bg-jarvis-cyan/10 border border-jarvis-cyan/50 flex items-center justify-center mx-auto mb-4 shadow-neonCyan">
                <Sparkles size={32} className="text-jarvis-cyan animate-pulse" />
              </div>
              <h2 className="font-hud font-bold text-xl text-neon-cyan mb-2">JARVIS TACTICAL TERMINAL</h2>
              <p className="text-xs text-jarvis-muted font-mono leading-relaxed">
                Connected to FastAPI Agentic OS Core at <code className="text-jarvis-cyan">http://127.0.0.1:8000</code>.
                Ask me to write code, conduct deep research, execute commands, or manage tasks.
              </p>
            </div>

            {/* Quick Command Pills */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
              {quickPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(prompt.slice(2))}
                  className="hud-panel p-3 text-left hover:border-jarvis-cyan transition-all text-xs font-mono text-jarvis-text flex items-center justify-between group"
                  id={`btn-quick-prompt-${idx}`}
                >
                  <span className="truncate pr-2">{prompt}</span>
                  <Play size={12} className="text-jarvis-cyan opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} onApprove={handleApprove} />
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3 p-4 rounded-xl bg-jarvis-card border border-jarvis-cyan/30 w-fit">
            <Loader2 size={18} className="animate-spin text-jarvis-cyan" />
            <span className="font-hud font-bold text-xs text-jarvis-cyan animate-pulse">
              JARVIS AGENTS PROCESSING...
            </span>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Sci-Fi Tactical Input Bar */}
      <div className="p-4 border-t border-jarvis-border/30 bg-[#020613]/95 backdrop-blur-xl scanline-overlay">
        <div className="max-w-4xl mx-auto relative">
          <div className="hud-panel p-2 flex items-end gap-2 border border-jarvis-border/50 focus-within:border-jarvis-cyan focus-within:shadow-neonCyan transition-all rounded-2xl">
            {/* Left Tools */}
            <button className="p-2 text-jarvis-muted hover:text-jarvis-cyan transition-colors" title="Attach file" id="btn-attach">
              <Paperclip size={18} />
            </button>

            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter directive for JARVIS... (Shift+Enter for newline)"
              className="flex-1 bg-transparent outline-none text-sm text-jarvis-text font-sans p-2 resize-none max-h-32 min-h-[40px]"
              rows={1}
              id="input-directive"
            />

            {/* Right Buttons: Voice + Send */}
            <button
              onClick={toggleVoice}
              className={`p-2.5 rounded-xl border transition-all ${
                isRecording 
                  ? 'bg-jarvis-red/20 border-jarvis-red text-jarvis-red shadow-neonRed animate-pulse' 
                  : 'bg-jarvis-card border-jarvis-border/40 text-jarvis-muted hover:text-jarvis-cyan'
              }`}
              title={isRecording ? 'Stop Voice Recording' : 'Activate Voice Input'}
              id="btn-voice-toggle"
            >
              {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
            </button>

            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isLoading}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-jarvis-blue to-jarvis-cyan text-white font-hud font-bold text-xs tracking-wider disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-neonCyan transition-all flex items-center gap-1.5"
              id="btn-send-directive"
            >
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              <span className="hidden sm:inline">TRANSMIT</span>
            </button>
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-jarvis-muted mt-2 px-2">
            <span>DIRECTIVE TARGET: POST /api/v1/chat/</span>
            <span>AUTONOMY: LEVEL {autonomyLevel}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
