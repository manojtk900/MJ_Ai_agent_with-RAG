import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  MessageSquare, Brain, CheckSquare, FolderKanban,
  Bot, Zap, TrendingUp, Clock, ArrowRight,
  Cpu, Globe, Code2, FileText, Mail, Mic
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const activityData = [
  { time: '00:00', messages: 0 },
  { time: '04:00', messages: 2 },
  { time: '08:00', messages: 12 },
  { time: '10:00', messages: 28 },
  { time: '12:00', messages: 45 },
  { time: '14:00', messages: 38 },
  { time: '16:00', messages: 52 },
  { time: '18:00', messages: 31 },
  { time: '20:00', messages: 19 },
  { time: '22:00', messages: 8 },
]

const statCards = [
  { label: 'Conversations', value: '24', icon: MessageSquare, color: '#6366f1', delta: '+3 today' },
  { label: 'Tasks Done', value: '18', icon: CheckSquare, color: '#10b981', delta: '+5 today' },
  { label: 'Memories', value: '142', icon: Brain, color: '#8b5cf6', delta: '+12 this week' },
  { label: 'Projects', value: '6', icon: FolderKanban, color: '#06b6d4', delta: '2 active' },
]

const recentActivity = [
  { icon: MessageSquare, label: 'Chat about FastAPI architecture', time: '2m ago', agent: 'Chat' },
  { icon: Globe, label: 'Researched AI agent trends 2026', time: '18m ago', agent: 'Research' },
  { icon: Code2, label: 'Generated REST API boilerplate', time: '1h ago', agent: 'Execution' },
  { icon: FileText, label: 'Analyzed 42-page PDF document', time: '2h ago', agent: 'File' },
  { icon: Mail, label: 'Drafted project proposal email', time: '3h ago', agent: 'Email' },
]

const agentCards = [
  { name: 'Controller', desc: 'Intent routing', status: 'active', icon: Zap, color: '#6366f1' },
  { name: 'Chat', desc: 'Conversation', status: 'idle', icon: MessageSquare, color: '#8b5cf6' },
  { name: 'Research', desc: 'Deep research', status: 'idle', icon: Globe, color: '#06b6d4' },
  { name: 'Execution', desc: 'Code & GitHub', status: 'idle', icon: Code2, color: '#f59e0b' },
  { name: 'Memory', desc: 'pgvector store', status: 'active', icon: Brain, color: '#10b981' },
  { name: 'Browser', desc: 'Playwright', status: 'idle', icon: Cpu, color: '#ec4899' },
]

const fadeUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.35 },
}

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <div className="p-6 overflow-y-auto h-full" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <motion.div {...fadeUp} className="mb-8">
        <h1 className="text-3xl font-bold gradient-text mb-1">Agent Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          MJ AI Agentic Operating System · {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </motion.div>

      {/* Stat Cards */}
      <motion.div
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ staggerChildren: 0.08, delayChildren: 0.1 }}
      >
        {statCards.map(({ label, value, icon: Icon, color, delta }, i) => (
          <motion.div key={i} {...fadeUp} className="card">
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
                <Icon size={18} style={{ color }} />
              </div>
              <TrendingUp size={14} style={{ color: '#10b981' }} />
            </div>
            <p className="text-2xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>{value}</p>
            <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>{label}</p>
            <p className="text-xs mt-1" style={{ color: '#10b981' }}>{delta}</p>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-6 mb-6">
        {/* Activity Chart */}
        <motion.div {...fadeUp} className="card lg:col-span-2">
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            <TrendingUp size={16} style={{ color: 'var(--accent-primary)' }} />
            Today's Activity
          </h2>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="colorMsg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="time" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-default)', borderRadius: '8px', color: 'var(--text-primary)' }}
              />
              <Area type="monotone" dataKey="messages" stroke="#6366f1" strokeWidth={2} fill="url(#colorMsg)" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Recent Activity */}
        <motion.div {...fadeUp} className="card">
          <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
            <Clock size={16} style={{ color: 'var(--accent-tertiary)' }} />
            Recent Activity
          </h2>
          <div className="flex flex-col gap-3">
            {recentActivity.map(({ icon: Icon, label, time, agent }, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)' }}>
                  <Icon size={14} style={{ color: 'var(--accent-primary)' }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate" style={{ color: 'var(--text-primary)' }}>{label}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{time}</span>
                    <span className="badge badge-blue text-xs py-0 px-1.5">{agent}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Agent Grid */}
      <motion.div {...fadeUp} className="mb-6">
        <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
          <Bot size={16} style={{ color: 'var(--accent-secondary)' }} />
          Agent Fleet
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {agentCards.map(({ name, desc, status, icon: Icon, color }, i) => (
            <motion.div key={i} whileHover={{ y: -3 }} className="card text-center py-4">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-3"
                style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
                <Icon size={18} style={{ color }} />
              </div>
              <p className="text-sm font-semibold mb-0.5" style={{ color: 'var(--text-primary)' }}>{name}</p>
              <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>{desc}</p>
              <span className={`badge ${status === 'active' ? 'badge-green' : 'badge-blue'} text-xs`}>
                {status}
              </span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div {...fadeUp} className="card">
        <h2 className="text-base font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'New Chat', icon: MessageSquare, to: '/chat', color: '#6366f1' },
            { label: 'Research Topic', icon: Globe, to: '/chat?prompt=research', color: '#06b6d4' },
            { label: 'Create Project', icon: FolderKanban, to: '/projects', color: '#8b5cf6' },
            { label: 'Voice Chat', icon: Mic, to: '/chat?voice=true', color: '#10b981' },
          ].map(({ label, icon: Icon, to, color }, i) => (
            <button
              key={i}
              onClick={() => navigate(to)}
              className="flex items-center gap-3 p-3 rounded-xl text-left transition-all hover:scale-[1.02]"
              style={{ background: `${color}10`, border: `1px solid ${color}25` }}
              id={`quick-action-${i}`}
            >
              <Icon size={20} style={{ color }} />
              <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{label}</span>
              <ArrowRight size={14} className="ml-auto" style={{ color: 'var(--text-muted)' }} />
            </button>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
