import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, MessageSquare, Bot, Brain, 
  CheckSquare, FolderKanban, Settings, Plus, 
  Radio, Disc, X, ShieldAlert, Cpu
} from 'lucide-react'
import { useJarvisStore } from '../../store/jarvisStore'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'COMMAND DASHBOARD', sub: 'Tactical Overview' },
  { to: '/chat', icon: MessageSquare, label: 'TACTICAL TERMINAL', sub: 'Real-time Interface' },
  { to: '/agents', icon: Bot, label: 'AGENT FLEET', sub: '15 Active Modules' },
  { to: '/memory', icon: Brain, label: 'QUANTUM MEMORY', sub: 'pgvector Matrix' },
  { to: '/tasks', icon: CheckSquare, label: 'TASK GRID', sub: 'Cron & Workflows' },
  { to: '/projects', icon: FolderKanban, label: 'MISSION BOARD', sub: 'Project Milestones' },
  { to: '/settings', icon: Settings, label: 'SYSTEM CONFIG', sub: 'LLM & Security' },
]

const fleetStatus = [
  { name: 'Controller', role: 'Intent Engine', status: 'ACTIVE', color: '#00f0ff' },
  { name: 'Planner', role: 'Decomposition', status: 'READY', color: '#0072ff' },
  { name: 'Search & Research', role: 'Tavily / DDG', status: 'READY', color: '#00ff9d' },
  { name: 'Execution', role: 'GitHub & Coding', status: 'READY', color: '#ffb700' },
  { name: 'pgvector Memory', role: 'Semantic Store', status: 'ACTIVE', color: '#7000ff' },
]

export default function Sidebar({ onClose }) {
  const navigate = useNavigate()
  const { createNewConversation } = useJarvisStore()

  const handleNewSession = () => {
    const id = createNewConversation()
    navigate(`/chat/${id}`)
    onClose?.()
  }

  return (
    <div className="flex flex-col h-full bg-[#020613]/95 border-r border-jarvis-border/30 p-4 select-none scanline-overlay">
      {/* Top Header Logo */}
      <div className="flex items-center justify-between px-2 py-3 mb-4 border-b border-jarvis-border/20">
        <div className="flex items-center gap-3">
          <div className="relative w-10 h-10 rounded-xl bg-jarvis-card border border-jarvis-cyan/40 flex items-center justify-center shadow-neonCyan">
            <Disc className="text-jarvis-cyan animate-spin-slow" size={22} />
            <div className="absolute inset-0 rounded-xl border border-jarvis-cyan/30 animate-pulse" />
          </div>
          <div>
            <h1 className="font-hud font-bold text-base text-neon-cyan tracking-wider">JARVIS</h1>
            <p className="text-[10px] font-mono text-jarvis-muted">AI AGENTIC OPERATING SYSTEM</p>
          </div>
        </div>

        {/* Mobile Close */}
        {onClose && (
          <button 
            onClick={onClose} 
            className="p-1 rounded-lg text-jarvis-muted hover:text-jarvis-cyan lg:hidden"
            id="sidebar-close-btn"
          >
            <X size={20} />
          </button>
        )}
      </div>

      {/* New Session Tactical Button */}
      <button
        onClick={handleNewSession}
        className="hud-panel p-3 mb-6 flex items-center justify-center gap-2 font-hud font-semibold text-xs text-jarvis-cyan hover:text-white transition-all group"
        id="btn-new-session"
      >
        <Plus size={16} className="group-hover:rotate-90 transition-transform duration-300" />
        <span>INITIALIZE NEW SESSION</span>
      </button>

      {/* Navigation Links */}
      <nav className="flex flex-col gap-1.5 flex-1 overflow-y-auto pr-1">
        <div className="px-2 py-1 text-[10px] font-hud text-jarvis-muted tracking-widest uppercase">
          TACTICAL NAVIGATION
        </div>

        {navItems.map(({ to, icon: Icon, label, sub }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) => `
              relative flex items-center gap-3 p-2.5 rounded-xl border transition-all duration-200 group
              ${isActive 
                ? 'bg-jarvis-cyan/15 border-jarvis-cyan text-jarvis-cyan shadow-neonCyan' 
                : 'bg-transparent border-transparent text-jarvis-muted hover:bg-jarvis-card hover:border-jarvis-border/40 hover:text-jarvis-text'
              }
            `}
            id={`nav-item-${label.toLowerCase().replace(/\s+/g, '-')}`}
          >
            {({ isActive }) => (
              <>
                <Icon size={18} className={isActive ? 'text-jarvis-cyan' : 'group-hover:text-jarvis-cyan'} />
                <div className="flex-1 min-w-0">
                  <div className="font-hud font-semibold text-xs tracking-wide truncate">{label}</div>
                  <div className="text-[10px] font-mono text-jarvis-muted truncate">{sub}</div>
                </div>
                {isActive && (
                  <div className="w-1.5 h-6 rounded-full bg-jarvis-cyan shadow-neonCyan" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Agent Fleet Status Sub-panel */}
      <div className="mt-auto pt-4 border-t border-jarvis-border/20">
        <div className="flex items-center justify-between px-2 mb-2">
          <span className="text-[10px] font-hud text-jarvis-muted tracking-widest uppercase">FLEET MODULES</span>
          <span className="flex items-center gap-1 text-[10px] font-mono text-jarvis-green">
            <Radio size={10} className="animate-pulse" /> 5 ONLINE
          </span>
        </div>

        <div className="flex flex-col gap-1.5">
          {fleetStatus.map((agent, i) => (
            <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-jarvis-card/60 border border-jarvis-border/20 text-xs">
              <div className="flex items-center gap-2 min-w-0">
                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: agent.color, boxShadow: `0 0 8px ${agent.color}` }} />
                <span className="font-mono text-[11px] text-jarvis-text truncate">{agent.name}</span>
              </div>
              <span className="text-[9px] font-hud px-1.5 py-0.5 rounded bg-jarvis-cyan/10 text-jarvis-cyan border border-jarvis-cyan/30">
                {agent.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
