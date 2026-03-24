'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Briefcase, Bookmark, ListChecks, Settings } from 'lucide-react'

const LINKS = [
  { href: '/',          label: 'Jobs',      icon: Briefcase },
  { href: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
  { href: '/bid-queue', label: 'Bid Queue', icon: ListChecks },
  { href: '/settings',  label: 'Settings',  icon: Settings },
]

export default function Nav() {
  const pathname = usePathname()

  return (
    <nav className="border-b border-white/8 bg-[#1e1e1e] px-6 py-0 flex items-stretch justify-between sticky top-0 z-50 h-14">
      {/* Brand */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#208ec7] to-[#1f5b99] flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-[#208ec7]/20">
          N
        </div>
        <div className="flex flex-col -gap-0.5">
          <span className="text-white font-semibold text-sm leading-none">Job Scout</span>
          <span className="text-[10px] text-[#208ec7]/70 leading-none mt-0.5">NexusPoint</span>
        </div>
      </div>

      {/* Links */}
      <div className="flex items-stretch gap-0">
        {LINKS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={`relative flex items-center gap-1.5 px-4 text-sm transition-colors ${
                active
                  ? 'text-[#208ec7]'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Icon size={14} />
              {label}
              {active && (
                <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#208ec7] to-[#1f5b99] rounded-t-full" />
              )}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
