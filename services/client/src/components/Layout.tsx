import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import NavBar from './NavBar'
import logoIcon from '@/assets/logo-icon.png'

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-bg-primary">
      {/* Mobile overlay — fades in/out instead of popping */}
      <div
        className={`fixed inset-0 z-20 bg-black/50 transition-opacity duration-300 lg:pointer-events-none lg:hidden ${
          sidebarOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar — translucent material with backdrop blur (§12) */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-[260px] flex-col border-r border-white/[0.06] bg-sidebar backdrop-blur-xl transition-transform duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-2.5">
            <img src={logoIcon} alt="Nuevo Hive" className="h-7 w-auto" />
            <span className="text-[15px] font-semibold tracking-tight text-white">
              Nuevo Hive
            </span>
          </div>
          <button
            className="rounded-md p-1 text-gray-500 transition-colors hover:text-white active:scale-90 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="size-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-3">
          <NavBar onNavigate={() => setSidebarOpen(false)} />
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center px-4 lg:hidden">
          <button
            className="rounded-md p-1.5 text-gray-500 transition-colors hover:text-white active:scale-90"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
