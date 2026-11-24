import { useQuery } from '@tanstack/react-query'
import { userManager } from '../auth/AuthProvider'
import { useAuth } from '../auth/AuthProvider'
import { getMe } from '../api/me'

interface NavItem {
  label: string
  href: string
  icon: string
  quickAdd?: string   // href to navigate to for quick-create (admin only)
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Lounges', href: '/lounges', icon: '🏛', quickAdd: '/lounges?new=1' },
  { label: 'Settings', href: '/settings', icon: '⚙' },
]

function NavLink({ item, isAdmin }: { item: NavItem; isAdmin: boolean }) {
  const active = window.location.pathname === item.href
  return (
    <div className="group flex items-center">
      <a
        href={item.href}
        className={`flex flex-1 items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
          active
            ? 'bg-zinc-700 text-white'
            : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
        }`}
      >
        <span className="text-base">{item.icon}</span>
        {item.label}
      </a>
      {item.quickAdd && isAdmin && (
        <a
          href={item.quickAdd}
          title={`New ${item.label.toLowerCase().replace(/s$/, '')}`}
          className="mr-1 rounded px-1.5 py-1 text-zinc-500 opacity-0 transition-opacity hover:bg-zinc-700 hover:text-white group-hover:opacity-100"
        >
          +
        </a>
      )}
    </div>
  )
}

export function Sidebar() {
  const { user } = useAuth()
  const token = user?.access_token ?? ''

  const { data: me } = useQuery({
    queryKey: ['me'],
    queryFn: () => getMe(token),
    enabled: !!token,
  })
  const isAdmin = me?.role === 'admin'

  async function handleLogout() {
    await userManager.removeUser()
    window.location.replace('/login')
  }

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-zinc-800 bg-zinc-900">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5 border-b border-zinc-800">
        <span className="text-xl">🍃</span>
        <span className="font-semibold text-white tracking-wide">Cigar Log</span>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.href} item={item} isAdmin={isAdmin} />
        ))}
      </nav>

      {/* User + logout */}
      <div className="border-t border-zinc-800 px-3 py-3 flex flex-col gap-1">
        {user && (
          <p className="truncate px-3 py-1 text-xs text-zinc-500">
            {user.profile?.email as string ?? ''}
          </p>
        )}
        <button
          onClick={() => void handleLogout()}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-red-400"
        >
          <span className="text-base">↩</span>
          Log out
        </button>
      </div>
    </aside>
  )
}
