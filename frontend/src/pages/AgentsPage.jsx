import React, { useEffect, useState } from 'react'
import { Bot, Zap, Search, Globe, Database, Terminal, Cpu, Mail, Clock, FileText, Mic, Code2, Calendar, FolderKanban, ShieldCheck } from 'lucide-react'
import { systemApi } from '../services/api'

const AGENT_LIST = [
  { name: 'Controller', icon: Zap, category: 'Core Routing', desc: 'LLM Intent Detection & Security Permission Check', color: '#00f0ff', status: 'ACTIVE' },
  { name: 'Planner', icon: Cpu, category: 'Planning', desc: 'Goal Decomposition & Step-by-Step Execution Graph', color: '#0072ff', status: 'READY' },
  { name: 'Chat Agent', icon: Bot, category: 'Conversation', desc: 'General Conversation, Coding Help, & Complex Reasoning', color: '#00ff9d', status: 'READY' },
  { name: 'Search Agent', icon: Search, category: 'Web Research', desc: 'Tavily & DuckDuckGo Real-Time Web Search Verification', color: '#00f0ff', status: 'READY' },
  { name: 'Research Agent', icon: Globe, category: 'Deep Research', desc: 'Multi-Source Deep Synthesis & Structured Report Writer', color: '#7000ff', status: 'READY' },
  { name: 'pgvector Memory', icon: Database, category: 'Storage', desc: 'PostgreSQL Vector Cosine Similarity Long-Term Memory', color: '#a855f7', status: 'ACTIVE' },
  { name: 'System Agent', icon: Terminal, category: 'Local OS', desc: 'File Operations, Terminal Commands, Local Control', color: '#ff0055', status: 'READY' },
  { name: 'Browser Agent', icon: Globe, category: 'Automation', desc: 'Playwright Browser Navigation, Screenshots, Scraper', color: '#ec4899', status: 'READY' },
  { name: 'Email Agent', icon: Mail, category: 'Communication', desc: 'SMTP / IMAP Inbox Reader & LLM Email Drafting', color: '#3b82f6', status: 'READY' },
  { name: 'Reminder Agent', icon: Clock, category: 'Scheduling', desc: 'NLP One-Time Reminders & Calendar Event Parsing', color: '#ffb700', status: 'READY' },
  { name: 'File Agent', icon: FileText, category: 'Document AI', desc: 'PDF Reader, Analysis, DOCX & PPTX Generation', color: '#14b8a6', status: 'READY' },
  { name: 'Voice Agent', icon: Mic, category: 'Audio STT/TTS', desc: 'OpenAI Whisper STT & OpenAI TTS Audio Synthesizer', color: '#00ff9d', status: 'READY' },
  { name: 'Execution Agent', icon: Code2, category: 'Autonomous Dev', desc: 'GitHub Automation, Code Generation, CI/CD Deployment', color: '#ffb700', status: 'READY' },
  { name: 'Scheduler Agent', icon: Calendar, category: 'Background Tasks', desc: 'Celery Beat Cron Jobs & Automated Background Workflows', color: '#00f0ff', status: 'READY' },
  { name: 'Project Manager', icon: FolderKanban, category: 'Mission Control', desc: 'Project Architecture, Sprint Planning, Milestones', color: '#7000ff', status: 'READY' },
]

export default function AgentsPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto">
      <div className="hud-panel p-5 border border-jarvis-cyan/30 flex items-center justify-between">
        <div>
          <h1 className="font-hud font-bold text-xl text-neon-cyan">JARVIS AGENT FLEET MATRIX</h1>
          <p className="text-xs font-mono text-jarvis-muted mt-0.5">
            15 SPECIALIZED AUTONOMOUS SUB-AGENT MODULES
          </p>
        </div>
        <div className="px-3 py-1 rounded-xl bg-jarvis-green/20 text-jarvis-green border border-jarvis-green/40 font-hud text-xs font-bold">
          15 MODULES OPERATIONAL
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {AGENT_LIST.map((agent, i) => {
          const Icon = agent.icon
          return (
            <div key={i} className="hud-panel p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center border shadow-neonCyan"
                    style={{ backgroundColor: `${agent.color}15`, borderColor: `${agent.color}50` }}
                  >
                    <Icon size={20} style={{ color: agent.color }} />
                  </div>
                  <div>
                    <h3 className="font-hud font-bold text-sm text-jarvis-text">{agent.name}</h3>
                    <span className="text-[10px] font-mono text-jarvis-muted">{agent.category}</span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-hud font-bold bg-jarvis-cyan/10 text-jarvis-cyan border border-jarvis-cyan/30">
                  {agent.status}
                </span>
              </div>
              <p className="text-xs font-sans text-jarvis-muted leading-relaxed">
                {agent.desc}
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
