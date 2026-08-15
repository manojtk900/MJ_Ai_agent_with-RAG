import React, { useState, useEffect } from 'react'
import { Activity, Bell, CheckCircle2, Clock, Zap, Shield, Flame, Mail } from 'lucide-react'

export default function MissionLog() {
  const [logs, setLogs] = useState([
    { time: '19:42:01', action: 'Desktop Agent', detail: 'Opened YouTube (open_browser)', status: 'SUCCESS', color: '#00f0ff' },
    { time: '19:42:05', action: 'Desktop Agent', detail: 'Searched Yash Toxic Trailer', status: 'SUCCESS', color: '#00f0ff' },
    { time: '19:43:10', action: 'Desktop Agent', detail: 'Opened Calculator (calc.exe)', status: 'SUCCESS', color: '#00f0ff' },
    { time: '19:44:20', action: 'Reminder Agent', detail: 'Scheduled reminder: Submit VTU Assignment', status: 'ACTIVE', color: '#00ff9d' },
    { time: '19:45:00', action: 'Gmail Agent', detail: 'Fetched 3 Internship Emails (Deloitte, TCS)', status: 'SUCCESS', color: '#ffb700' },
  ])

  const [notifications, setNotifications] = useState([
    { id: 1, title: 'Submit VTU Assignment', message: 'Task scheduled for 09:00 AM UTC', time: 'Just now' }
  ])

  // Connect to live SSE notification stream
  useEffect(() => {
    try {
      const eventSource = new EventSource('/api/v1/notifications/stream')
      eventSource.addEventListener('notification', (event) => {
        const data = JSON.parse(event.data)
        setNotifications(prev => [data, ...prev])
        setLogs(prev => [
          {
            time: new Date().toLocaleTimeString(),
            action: 'Notification Agent',
            detail: `${data.title}: ${data.message}`,
            status: 'DELIVERED',
            color: '#ffb700'
          },
          ...prev
        ])
      })
      return () => eventSource.close()
    } catch (err) {
      console.warn('SSE notification stream fallback:', err)
    }
  }, [])

  return (
    <div className="space-y-4">
      {/* Top 4 Metrics Widgets */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-jarvis-card border border-jarvis-cyan/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-jarvis-muted uppercase block">Stored Memories</span>
            <span className="font-hud font-extrabold text-lg text-neon-cyan">27 Facts</span>
          </div>
          <Shield size={20} className="text-jarvis-cyan" />
        </div>

        <div className="p-3.5 rounded-xl bg-jarvis-card border border-jarvis-green/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-jarvis-muted uppercase block">Active Tasks</span>
            <span className="font-hud font-extrabold text-lg text-jarvis-green">5 Pending</span>
          </div>
          <Clock size={20} className="text-jarvis-green" />
        </div>

        <div className="p-3.5 rounded-xl bg-jarvis-card border border-[#ffb700]/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-jarvis-muted uppercase block">Commands Executed</span>
            <span className="font-hud font-extrabold text-lg text-[#ffb700]">34 Today</span>
          </div>
          <Zap size={20} className="text-[#ffb700]" />
        </div>

        <div className="p-3.5 rounded-xl bg-jarvis-card border border-jarvis-magenta/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono text-jarvis-muted uppercase block">Streak Tracker</span>
            <span className="font-hud font-extrabold text-lg text-jarvis-magenta flex items-center gap-1">
              7 Days <Flame size={16} className="text-jarvis-magenta fill-jarvis-magenta" />
            </span>
          </div>
          <Flame size={20} className="text-jarvis-magenta" />
        </div>
      </div>

      {/* Mission Activity Feed */}
      <div className="p-4 rounded-2xl bg-jarvis-card border border-jarvis-border/40 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-3 border-b border-jarvis-border/30 pb-2">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-jarvis-cyan animate-pulse" />
            <h3 className="font-hud font-bold text-xs text-neon-cyan tracking-wider uppercase">
              MISSION LOG & TACTICAL FEED
            </h3>
          </div>
          <span className="text-[10px] font-mono text-jarvis-muted">LIVE TELEMETRY</span>
        </div>

        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
          {logs.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-[#040c20]/60 border border-jarvis-border/20">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] text-jarvis-muted">{item.time}</span>
                <span className="font-hud font-bold text-[11px]" style={{ color: item.color }}>
                  [{item.action}]
                </span>
                <span className="text-jarvis-text text-[11px] truncate max-w-[280px]">{item.detail}</span>
              </div>
              <span className="font-mono text-[9px] px-2 py-0.5 rounded bg-jarvis-cyan/10 text-jarvis-cyan border border-jarvis-cyan/30">
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
