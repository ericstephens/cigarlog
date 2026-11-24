import { userManager } from '../auth/AuthProvider'
import { useAuth } from '../auth/AuthProvider'

interface NavItem {
  label: string
  href: string
  icon: string
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Settings', href: '/settings', icon: '⚙' },
]

function NavLink({ item }: { item: NavItem }) {
  const active = window.location.pathname === item.href
  return (
    <a
      href={item.href}
      className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
        active
          ? 'bg-zinc-700 text-white'
          : 'text-zinc-400 hover:bg-zinc-800 hover:text-white'
      }`}
    >
      <span className="text-base">{item.icon}</span>
      {item.label}
    </a>
  )
}

export function Sidebar() {
  const { user } = useAuth()

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
          <NavLink key={item.href} item={item} />
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
