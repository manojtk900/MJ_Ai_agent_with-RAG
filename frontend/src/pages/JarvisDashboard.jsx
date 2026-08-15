import React from 'react'
import { motion } from 'framer-motion'
import { 
  Zap, Cpu, Activity, ShieldCheck, Database, Radio, 
  Terminal, ArrowUpRight, CheckSquare, Brain, Bot, Code2, Globe, Mail 
} from 'lucide-react'
import JarvisOrb from '../components/Jarvis/JarvisOrb'
import HealthPanel from '../components/Jarvis/HealthPanel'
import MissionLog from '../components/Jarvis/MissionLog'
import ChatInterface from '../components/Chat/ChatInterface'
import { useJarvisStore } from '../store/jarvisStore'
import { useNavigate } from 'react-router-dom'

export default function JarvisDashboard() {
  const { jarvisStatus, activeAgent, systemHealth } = useJarvisStore()
  const navigate = useNavigate()

  const quickActions = [
    { label: 'TACTICAL CHAT', icon: Terminal, route: '/chat', desc: 'Real-time AI Directive', color: '#00f0ff' },
    { label: 'EMAIL COMMAND', icon: Mail, route: '/chat', desc: 'Gmail Internship Filter', color: '#ffb700' },
    { label: 'QUANTUM MEMORY', icon: Brain, route: '/memory', desc: 'pgvector Matrix Search', color: '#7000ff' },
    { label: 'MISSION BOARD', icon: CheckSquare, route: '/projects', desc: 'Sprint & Milestones', color: '#00ff9d' },
  ]

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-jarvis-card border border-jarvis-border/30 backdrop-blur-xl">
        <div>
          <h1 className="font-hud font-extrabold text-xl md:text-2xl text-neon-cyan tracking-wider">
            JARVIS COMMAND CENTER
          </h1>
          <p className="text-xs font-mono text-jarvis-muted mt-0.5">
            STARK INDUSTRIES AGENTIC OS · INTEGRATED TACTICAL DASHBOARD
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-jarvis-green/10 border border-jarvis-green/30 text-jarvis-green text-xs font-hud font-bold">
            <Radio size={14} className="animate-pulse" /> CORE SYSTEM: ONLINE
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-jarvis-cyan/10 border border-jarvis-cyan/30 text-jarvis-cyan text-xs font-hud font-bold">
            <ShieldCheck size={14} /> SECURITY: LEVEL 4
          </div>
        </div>
      </div>

      {/* Live Mission Telemetry & Metrics Widgets */}
      <MissionLog />

      {/* Main Centerpiece Grid: Left Orb & Status | Right Live Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Central Animated JARVIS Orb & Telemetry */}
        <div className="lg:col-span-5 space-y-6 flex flex-col items-center">
          {/* Central Animated Orb HUD Card */}
          <div className="hud-panel p-8 w-full flex flex-col items-center justify-center min-h-[380px] relative overflow-hidden border border-jarvis-cyan/40">
            <div className="text-xs font-hud text-jarvis-muted tracking-widest uppercase mb-4">
              PRIMARY AI REACTOR CORE
            </div>
            
            {/* The Central JARVIS Orb */}
            <JarvisOrb size={260} />

            <div className="mt-8 grid grid-cols-2 gap-3 w-full text-center">
              <div className="p-2.5 rounded-xl bg-jarvis-card border border-jarvis-border/20">
                <span className="text-[10px] font-mono text-jarvis-muted block">ACTIVE MODULE</span>
                <span className="font-hud font-bold text-xs text-jarvis-cyan">{activeAgent}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-jarvis-card border border-jarvis-border/20">
                <span className="text-[10px] font-mono text-jarvis-muted block">SYSTEM MODE</span>
                <span className="font-hud font-bold text-xs text-jarvis-green">{jarvisStatus}</span>
              </div>
            </div>
          </div>

          {/* Diagnostics HUD Panel */}
          <div className="w-full">
            <HealthPanel />
          </div>
        </div>

        {/* Right Column: Live Chat Terminal Component */}
        <div className="lg:col-span-7 hud-panel overflow-hidden flex flex-col h-[740px]">
          <div className="p-3 bg-jarvis-card border-b border-jarvis-border/30 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal size={16} className="text-jarvis-cyan" />
              <span className="font-hud font-bold text-xs text-jarvis-cyan tracking-wider">TACTICAL DIRECTIVE TERMINAL</span>
            </div>
            <span className="text-[10px] font-mono text-jarvis-muted">http://127.0.0.1:8000</span>
          </div>

          <div className="flex-1 overflow-hidden">
            <ChatInterface />
          </div>
        </div>
      </div>

      {/* Quick Tactical Actions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((act, i) => {
          const Icon = act.icon
          return (
            <button
              key={i}
              onClick={() => navigate(act.route)}
              className="hud-panel p-4 text-left transition-all hover:scale-[1.02] flex items-center justify-between group"
              id={`quick-action-btn-${i}`}
            >
              <div className="flex items-center gap-3">
                <div 
                  className="w-10 h-10 rounded-xl flex items-center justify-center border"
                  style={{ backgroundColor: `${act.color}15`, borderColor: `${act.color}40` }}
                >
                  <Icon size={20} style={{ color: act.color }} />
                </div>
                <div>
                  <h3 className="font-hud font-bold text-xs text-jarvis-text group-hover:text-jarvis-cyan transition-colors">
                    {act.label}
                  </h3>
                  <p className="text-[10px] font-mono text-jarvis-muted">{act.desc}</p>
                </div>
              </div>
              <ArrowUpRight size={18} className="text-jarvis-muted group-hover:text-jarvis-cyan transition-colors" />
            </button>
          )
        })}
      </div>
    </div>
  )
}
