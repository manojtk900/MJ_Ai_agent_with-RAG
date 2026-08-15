import React from 'react'
import { motion } from 'framer-motion'
import { useJarvisStore } from '../../store/jarvisStore'

export default function JarvisOrb({ size = 280 }) {
  const { jarvisStatus, audioLevel, isListening, isSpeaking } = useJarvisStore()

  // Dynamic glow color based on status
  const getGlowColor = () => {
    switch (jarvisStatus) {
      case 'LISTENING': return '#00ff9d' // Green
      case 'PROCESSING':
      case 'THINKING': return '#7000ff' // Purple
      case 'ALERT': return '#ff0055' // Red
      default: return '#00f0ff' // Cyan
    }
  }

  const glowColor = getGlowColor()
  const pulseScale = 1 + (audioLevel / 100) * 0.15

  return (
    <div className="relative flex flex-col items-center justify-center select-none" style={{ width: size, height: size }}>
      {/* Outer Holographic Ambient Glow */}
      <div 
        className="absolute inset-0 rounded-full blur-3xl opacity-40 transition-colors duration-500"
        style={{
          background: `radial-gradient(circle, ${glowColor} 0%, transparent 70%)`,
          transform: `scale(${pulseScale * 1.2})`,
        }}
      />

      {/* SVG Arc Reactor / AI Core Rings */}
      <svg viewBox="0 0 300 300" className="w-full h-full relative z-10 filter drop-shadow-[0_0_15px_rgba(0,240,255,0.6)]">
        <defs>
          <radialGradient id="coreGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
            <stop offset="30%" stopColor={glowColor} stopOpacity="0.9" />
            <stop offset="70%" stopColor="#0072ff" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#020613" stopOpacity="0" />
          </radialGradient>

          <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={glowColor} />
            <stop offset="100%" stopColor="#0072ff" />
          </linearGradient>
        </defs>

        {/* Outer Ring 1 — Clockwise Slow Spin */}
        <motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: isListening ? 6 : 16, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '150px 150px' }}
        >
          <circle cx="150" cy="150" r="135" fill="none" stroke="url(#ringGradient)" strokeWidth="1.5" strokeDasharray="12 8 4 8" opacity="0.7" />
          <circle cx="150" cy="15" r="3.5" fill={glowColor} className="shadow-neonCyan" />
          <circle cx="150" cy="285" r="3.5" fill={glowColor} />
          <circle cx="15" cy="150" r="3.5" fill={glowColor} />
          <circle cx="285" cy="150" r="3.5" fill={glowColor} />
        </motion.g>

        {/* Outer Ring 2 — Counter-Clockwise Spin */}
        <motion.g
          animate={{ rotate: -360 }}
          transition={{ duration: isSpeaking ? 8 : 20, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '150px 150px' }}
        >
          <circle cx="150" cy="150" r="115" fill="none" stroke={glowColor} strokeWidth="1" strokeDasharray="30 15 10 15" opacity="0.6" />
          <path d="M 150 35 L 155 45 L 145 45 Z" fill={glowColor} />
          <path d="M 150 265 L 155 255 L 145 255 Z" fill={glowColor} />
        </motion.g>

        {/* Tactical Crosshair / Triangle Marks */}
        <motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
          style={{ transformOrigin: '150px 150px' }}
        >
          <circle cx="150" cy="150" r="95" fill="none" stroke="#00f0ff" strokeWidth="0.75" strokeDasharray="4 16" opacity="0.5" />
        </motion.g>

        {/* Inner Segmented Reactor Ring */}
        <motion.g
          animate={{ rotate: -360, scale: [1, 1.03, 1] }}
          transition={{ rotate: { duration: 12, repeat: Infinity, ease: 'linear' }, scale: { duration: 2, repeat: Infinity } }}
          style={{ transformOrigin: '150px 150px' }}
        >
          {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, idx) => (
            <rect
              key={idx}
              x="146"
              y="68"
              width="8"
              height="14"
              rx="2"
              fill={idx % 2 === 0 ? glowColor : '#0072ff'}
              opacity="0.85"
              transform={`rotate(${angle} 150 150)`}
            />
          ))}
        </motion.g>

        {/* Central Core Sphere */}
        <motion.circle
          cx="150"
          cy="150"
          r="52"
          fill="url(#coreGradient)"
          animate={{
            r: [48, 54 + (audioLevel / 100) * 12, 48],
            opacity: [0.85, 1, 0.85],
          }}
          transition={{ duration: isListening ? 0.6 : 2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Inner Arc Core Dot */}
        <circle cx="150" cy="150" r="16" fill="#ffffff" opacity="0.95" className="filter drop-shadow-[0_0_12px_#ffffff]" />
      </svg>

      {/* Floating Status HUD Label */}
      <div className="absolute -bottom-7 flex flex-col items-center">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#040e20]/90 border border-[#00f0ff]/40 backdrop-blur-md shadow-neonCyan">
          <span className="w-2 h-2 rounded-full animate-ping" style={{ backgroundColor: glowColor }} />
          <span className="font-hud text-xs font-bold tracking-widest text-[#00f0ff]">
            {jarvisStatus}
          </span>
        </div>
        <span className="text-[10px] font-mono text-jarvis-muted mt-1 uppercase tracking-wider">
          {isListening ? '🎤 LISTENING TO VOICE...' : isSpeaking ? '🔊 AUDIO SYNTHESIS ACTIVE' : 'JARVIS CORE ONLINE'}
        </span>
      </div>
    </div>
  )
}
