import React, { useState } from 'react'
import { Brain, Search, Database, Plus, Trash2, Tag, ShieldAlert } from 'lucide-react'

export default function MemoryPage() {
  const [query, setQuery] = useState('')
  const [memories, setMemories] = useState([
    { id: '1', content: 'User prefers Python 3.12, FastAPI backend, and dark neon cyan HUD theme.', type: 'user_preference', score: 0.96, date: '2026-08-11' },
    { id: '2', content: 'AgriGuard project architecture built using 15 autonomous sub-agents with pgvector memory.', type: 'learned_behavior', score: 0.89, date: '2026-08-11' },
    { id: '3', content: 'PostgreSQL 17 pgvector extension enabled for 1536-dimensional OpenAI embeddings.', type: 'system_fact', score: 0.84, date: '2026-08-11' },
  ])

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto">
      <div className="hud-panel p-5 border border-jarvis-cyan/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-jarvis-purple/20 border border-jarvis-purple/50 flex items-center justify-center shadow-neonCyan">
            <Brain size={22} className="text-jarvis-purple" />
          </div>
          <div>
            <h1 className="font-hud font-bold text-xl text-neon-cyan">QUANTUM MEMORY MATRIX</h1>
            <p className="text-xs font-mono text-jarvis-muted mt-0.5">POSTGRESQL + PGVECTOR COSINE SIMILARITY SEARCH</p>
          </div>
        </div>
        <div className="px-3 py-1 rounded-xl bg-jarvis-purple/20 text-jarvis-purple border border-jarvis-purple/40 font-hud text-xs font-bold">
          1,536-DIM VECTOR EMBEDDINGS
        </div>
      </div>

      {/* Semantic Search Bar */}
      <div className="hud-panel p-3 flex items-center gap-3 border border-jarvis-cyan/40">
        <Search size={18} className="text-jarvis-cyan ml-2" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Execute semantic search query across pgvector memory..."
          className="flex-1 bg-transparent outline-none text-sm text-jarvis-text font-mono"
        />
        <button className="px-4 py-2 rounded-xl bg-jarvis-cyan/20 border border-jarvis-cyan text-jarvis-cyan font-hud text-xs font-bold hover:bg-jarvis-cyan/30">
          SEARCH MATRIX
        </button>
      </div>

      {/* Memory Record Cards */}
      <div className="space-y-3">
        {memories.map((mem) => (
          <div key={mem.id} className="hud-panel p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="space-y-1 max-w-3xl">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-hud font-bold bg-jarvis-purple/20 text-jarvis-purple border border-jarvis-purple/40">
                  {mem.type}
                </span>
                <span className="text-[10px] font-mono text-jarvis-cyan">
                  MATCH SCORE: {(mem.score * 100).toFixed(1)}%
                </span>
              </div>
              <p className="text-sm font-sans text-jarvis-text">{mem.content}</p>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-[10px] font-mono text-jarvis-muted">{mem.date}</span>
              <button className="p-1.5 rounded-lg text-jarvis-muted hover:text-jarvis-red transition-colors">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
