import React from 'react'
import { FolderKanban, Flag, CheckCircle2, Plus } from 'lucide-react'

export default function ProjectsPage() {
  const projects = [
    { name: 'MJ AI Assistant OS', desc: 'Autonomous 15-Agent Operating System with FastAPI backend and JARVIS HUD UI.', status: 'IN PROGRESS', progress: 85, milestones: 5 },
    { name: 'AgriGuard AI Ecosystem', desc: 'Agricultural crop disease detection & advisory system with multi-tenant skills.', status: 'PLANNING', progress: 40, milestones: 8 },
  ]

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto">
      <div className="hud-panel p-5 border border-jarvis-cyan/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-jarvis-blue/20 border border-jarvis-blue/50 flex items-center justify-center shadow-neonCyan">
            <FolderKanban size={22} className="text-jarvis-cyan" />
          </div>
          <div>
            <h1 className="font-hud font-bold text-xl text-neon-cyan">JARVIS MISSION BOARD</h1>
            <p className="text-xs font-mono text-jarvis-muted mt-0.5">PROJECT ARCHITECTURE & SPRINT MILESTONES</p>
          </div>
        </div>
        <button className="px-3 py-1.5 rounded-xl bg-jarvis-cyan/20 text-jarvis-cyan border border-jarvis-cyan/40 font-hud text-xs font-bold hover:bg-jarvis-cyan/30 flex items-center gap-1.5">
          <Plus size={16} /> NEW PROJECT
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {projects.map((proj, i) => (
          <div key={i} className="hud-panel p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-hud font-bold text-base text-jarvis-text">{proj.name}</h3>
              <span className="px-2.5 py-1 rounded text-xs font-hud font-bold bg-jarvis-cyan/20 text-jarvis-cyan border border-jarvis-cyan/40">
                {proj.status}
              </span>
            </div>

            <p className="text-xs font-sans text-jarvis-muted leading-relaxed">{proj.desc}</p>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-jarvis-muted">COMPLETION</span>
                <span className="text-jarvis-cyan font-bold">{proj.progress}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-jarvis-card overflow-hidden border border-jarvis-border/30">
                <div className="h-full bg-gradient-to-r from-jarvis-blue to-jarvis-cyan shadow-neonCyan" style={{ width: `${proj.progress}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
