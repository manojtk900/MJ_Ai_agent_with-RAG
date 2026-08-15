import React, { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'

// Page Components
import JarvisDashboard from './pages/JarvisDashboard'
import ChatInterface from './components/Chat/ChatInterface'
import AgentsPage from './pages/AgentsPage'
import MemoryPage from './pages/MemoryPage'
import TasksPage from './pages/TasksPage'
import ProjectsPage from './pages/ProjectsPage'
import SettingsPage from './pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30000, retry: 1 },
  },
})

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-[#020613] text-[#e0f7fc]">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block w-64 min-h-screen fixed left-0 top-0 z-50">
        <Sidebar />
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="w-64 bg-[#020613] h-full shadow-2xl">
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </div>
          <div className="flex-1 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] bg-[#020613]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 rounded-xl border-2 border-jarvis-cyan/30 border-t-jarvis-cyan animate-spin" />
        <span className="font-hud font-bold text-xs text-neon-cyan animate-pulse">
          INITIALIZING JARVIS INTERFACE...
        </span>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<JarvisDashboard />} />
            <Route path="chat" element={<ChatInterface />} />
            <Route path="chat/:conversationId" element={<ChatInterface />} />
            <Route path="agents" element={<AgentsPage />} />
            <Route path="memory" element={<MemoryPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>

        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: 'rgba(5, 15, 35, 0.95)',
              color: '#e0f7fc',
              border: '1px solid rgba(0, 240, 255, 0.4)',
              boxShadow: '0 0 20px rgba(0, 240, 255, 0.3)',
              fontFamily: 'Orbitron, sans-serif',
              fontSize: '12px',
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
