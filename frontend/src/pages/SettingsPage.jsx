import React, { useState } from 'react'
import { Settings, Shield, Cpu, Key, Database, Save, Check } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const [provider, setProvider] = useState('openai')
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    toast.success('JARVIS System Settings updated!')
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] p-4 md:p-6 bg-[#020613] text-[#e0f7fc] space-y-6 overflow-y-auto max-w-4xl">
      <div className="hud-panel p-5 border border-jarvis-cyan/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-jarvis-cyan/20 border border-jarvis-cyan/50 flex items-center justify-center shadow-neonCyan">
            <Settings size={22} className="text-jarvis-cyan" />
          </div>
          <div>
            <h1 className="font-hud font-bold text-xl text-neon-cyan">JARVIS SYSTEM CONFIGURATION</h1>
            <p className="text-xs font-mono text-jarvis-muted mt-0.5">STARK OS GLOBAL PARADIGMS & PROVIDERS</p>
          </div>
        </div>
        <button
          onClick={handleSave}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-jarvis-blue to-jarvis-cyan text-white font-hud font-bold text-xs shadow-neonCyan hover:scale-105 transition-all flex items-center gap-2"
          id="btn-save-settings"
        >
          {saved ? <Check size={16} /> : <Save size={16} />}
          <span>SAVE CONFIG</span>
        </button>
      </div>

      <div className="hud-panel p-6 space-y-6">
        <div>
          <label className="font-hud font-bold text-sm text-jarvis-cyan block mb-2">PRIMARY LLM PROVIDER</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {['openai', 'gemini', 'claude', 'ollama'].map((p) => (
              <button
                key={p}
                onClick={() => setProvider(p)}
                className={`p-3 rounded-xl border text-center font-hud font-bold text-xs uppercase transition-all ${
                  provider === p 
                    ? 'bg-jarvis-cyan/20 border-jarvis-cyan text-jarvis-cyan shadow-neonCyan' 
                    : 'bg-jarvis-card border-jarvis-border/30 text-jarvis-muted hover:text-jarvis-text'
                }`}
                id={`btn-provider-${p}`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-4 pt-4 border-t border-jarvis-border/20">
          <div>
            <label className="font-mono text-xs text-jarvis-muted block mb-1">FASTAPI BACKEND ENDPOINT</label>
            <input
              type="text"
              defaultValue="http://127.0.0.1:8000"
              className="w-full hud-panel p-3 text-sm font-mono text-jarvis-text outline-none focus:border-jarvis-cyan"
            />
          </div>

          <div>
            <label className="font-mono text-xs text-jarvis-muted block mb-1">OPENAI MODEL PIN</label>
            <input
              type="text"
              defaultValue="gpt-4o"
              className="w-full hud-panel p-3 text-sm font-mono text-jarvis-text outline-none focus:border-jarvis-cyan"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
