import React, { useState, useEffect } from 'react'
import { Menu, Shield, Activity, Volume2, VolumeX, Cpu, Terminal, Zap } from 'lucide-react'
import { useJarvisStore } from '../../store/jarvisStore'

export default function Header({ onMenuClick }) {
  const { autonomyLevel, setAutonomyLevel, isVoiceActive, setVoiceActive, systemHealth } = useJarvisStore()
  const [timeStr, setTimeStr] = useState('')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }))
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  const AUTONOMY_NAMES = { 0: '0: MANUAL', 1: '1: ASK FIRST', 2: '2: AUTO SAFE', 3: '3: FULL AUTO' }
  const AUTONOMY_COLORS = { 0: 'text-gray-400', 1: 'text-jarvis-cyan', 2: 'text-jarvis-amber', 3: 'text-jarvis-red' }

  return (
    <header className="h-16 border-b border-jarvis-border/40 bg-[#020613]/90 backdrop-blur-xl sticky top-0 z-40 flex items-center justify-between px-4 lg:px-6 select-none scanline-overlay">
      {/* Left: Mobile Menu + Protocol Status */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg lg:hidden text-jarvis-cyan hover:bg-jarvis-cyan/10 border border-jarvis-border/30 transition-colors"
          id="btn-mobile-menu"
        >
          <Menu size={20} />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-jarvis-cyan/10 border border-jarvis-cyan/40 flex items-center justify-center shadow-neonCyan">
            <Zap size={18} className="text-jarvis-cyan animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-hud font-bold text-sm text-jarvis-cyan tracking-wider">JARVIS OS</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-jarvis-blue/20 text-jarvis-cyan border border-jarvis-cyan/30">
                v4.2-PROD
              </span>
            </div>
            <p className="text-[10px] font-mono text-jarvis-muted hidden sm:block">
              STARK INDUSTRIES TACTICAL NETWORK
            </p>
          </div>
        </div>
      </div>

      {/* Middle: Live Clock + System Load (Hidden on small screens) */}
      <div className="hidden md:flex items-center gap-6 px-4 py-1.5 rounded-full bg-jarvis-card border border-jarvis-border/30">
        <div className="flex items-center gap-2 text-xs font-mono text-jarvis-text">
          <Terminal size={14} className="text-jarvis-cyan" />
          <span className="text-jarvis-cyan font-bold">{timeStr}</span>
          <span className="text-jarvis-muted">SYS_TIME</span>
        </div>
        <div className="h-3 w-[1px] bg-jarvis-border/40" />
        <div className="flex items-center gap-2 text-xs font-mono">
          <Cpu size={14} className="text-jarvis-green" />
          <span className="text-jarvis-muted">CPU:</span>
          <span className="text-jarvis-green font-semibold">{systemHealth.cpuUsage || 12.4}%</span>
        </div>
        <div className="h-3 w-[1px] bg-jarvis-border/40" />
        <div className="flex items-center gap-2 text-xs font-mono">
          <Activity size={14} className="text-jarvis-cyan" />
          <span className="text-jarvis-muted">PING:</span>
          <span className="text-jarvis-cyan font-semibold">{systemHealth.pingMs || 14}ms</span>
        </div>
      </div>

      {/* Right: Autonomy Level + Audio Toggle */}
      <div className="flex items-center gap-3">
        {/* Autonomy Level Control */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-lg bg-jarvis-card border border-jarvis-border/40">
          <Shield size={14} className="text-jarvis-cyan" />
          <span className="text-[11px] font-mono text-jarvis-muted">AUTONOMY:</span>
          <select
            value={autonomyLevel}
            onChange={(e) => setAutonomyLevel(Number(e.target.value))}
            className={`bg-transparent text-xs font-hud font-bold outline-none cursor-pointer ${AUTONOMY_COLORS[autonomyLevel]}`}
            id="header-autonomy-select"
          >
            <option value={0} className="bg-[#050c1e] text-gray-300">0: MANUAL (Chat Only)</option>
            <option value={1} className="bg-[#050c1e] text-[#00f0ff]">1: ASK FIRST (Confirmation)</option>
            <option value={2} className="bg-[#050c1e] text-[#ffb700]">2: AUTO SAFE (Autonomous)</option>
            <option value={3} className="bg-[#050c1e] text-[#ff0055]">3: FULL AUTO (Unrestricted)</option>
          </select>
        </div>

        {/* Voice Audio Toggle */}
        <button
          onClick={() => setVoiceActive(!isVoiceActive)}
          className={`p-2 rounded-lg border transition-all ${
            isVoiceActive
              ? 'bg-jarvis-cyan/20 border-jarvis-cyan text-jarvis-cyan shadow-neonCyan'
              : 'bg-jarvis-card border-jarvis-border/30 text-jarvis-muted hover:text-jarvis-text'
          }`}
          title={isVoiceActive ? 'Voice Synthesis Enabled' : 'Voice Synthesis Muted'}
          id="header-voice-toggle"
        >
          {isVoiceActive ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
      </div>
    </header>
  )
}
