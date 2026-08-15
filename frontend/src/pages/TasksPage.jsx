import React from 'react'
import { CheckSquare, Clock, Plus, Play, Calendar, AlertCircle } from 'lucide-react'

export default function TasksPage() {
  const tasks = [
    { id: '1', title: 'Daily AgriGuard Weather Telemetry Pull', cron: '0 0 * * *', status: 'SCHEDULED', next: '2026-08-12 00:00 UTC', priority: 'HIGH' },
    { id: '2', title: 'Vector Embedding Index Optimization', cron: '0 2 * * 0', status: 'ACTIVE', next: '2026-08-16 02:00 UTC', priority: 'MEDIUM' },
    { id: '3', title: 'Automated GitHub Repository Backup', cron: '0 12 * * *', status: 'SCHEDULED', next: '2026-08-12 12:00 UTC', priority: 'LOW' },
  ]

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto">
      <div className="hud-panel p-5 border border-jarvis-cyan/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-jarvis-green/20 border border-jarvis-green/50 flex items-center justify-center shadow-neonCyan">
            <CheckSquare size={22} className="text-jarvis-green" />
          </div>
          <div>
            <h1 className="font-hud font-bold text-xl text-neon-cyan">JARVIS TASK GRID</h1>
            <p className="text-xs font-mono text-jarvis-muted mt-0.5">CELERY BEAT BACKGROUND CRON WORKFLOWS</p>
          </div>
        </div>
        <button className="px-3 py-1.5 rounded-xl bg-jarvis-green/20 text-jarvis-green border border-jarvis-green/40 font-hud text-xs font-bold hover:bg-jarvis-green/30 flex items-center gap-1.5">
          <Plus size={16} /> NEW CRON TASK
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {tasks.map((task) => (
          <div key={task.id} className="hud-panel p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-hud font-bold text-sm text-jarvis-text">{task.title}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-jarvis-card border border-jarvis-border/30 text-jarvis-cyan">
                  {task.cron}
                </span>
              </div>
              <p className="text-xs font-mono text-jarvis-muted">Next execution: {task.next}</p>
            </div>

            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 rounded text-xs font-hud font-bold bg-jarvis-green/20 text-jarvis-green border border-jarvis-green/40">
                {task.status}
              </span>
              <button className="p-2 rounded-xl bg-jarvis-cyan/20 text-jarvis-cyan border border-jarvis-cyan/40 hover:bg-jarvis-cyan/30">
                <Play size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
