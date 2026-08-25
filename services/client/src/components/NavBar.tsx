import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Grid3X3, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/slots', label: 'Slot Performance', icon: Grid3X3 },
  { to: '/trends', label: 'Trends', icon: TrendingUp },
]

function NavBar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-0.5">
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors duration-150',
              'active:scale-[0.97] active:transition-transform active:duration-75',
              isActive
                ? 'bg-bg-surface text-white'
                : 'text-gray-500 hover:bg-bg-surface-hover hover:text-gray-300'
            )
          }
        >
          <Icon className="size-[18px] shrink-0" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export default NavBar
