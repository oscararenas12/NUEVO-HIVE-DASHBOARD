import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Grid3X3, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/slots', label: 'Slot Performance', icon: Grid3X3 },
  { to: '/trends', label: 'Trends', icon: TrendingUp },
]

function NavBar() {
  return (
    <nav className="flex flex-col gap-1 px-3">
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
              isActive
                ? 'bg-bg-surface text-white'
                : 'text-gray-400 hover:bg-bg-surface/50 hover:text-gray-200'
            )
          }
        >
          <Icon className="size-4" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export default NavBar
