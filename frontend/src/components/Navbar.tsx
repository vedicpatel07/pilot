// src/components/Navbar.tsx
'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navbar() {
  const pathname = usePathname()

  // Function to determine if a link is active
  const isActive = (path: string) => {
    return pathname === path
  }

  return (
    <nav className="bg-slate-900">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <Link 
            href="/" 
            className="text-white text-xl font-bold hover:text-slate-200 transition-colors"
          >
            RoboTask
          </Link>

          {/* Navigation Links */}
          <div className="flex space-x-8">
            <Link
              href="/chat"
              className={`${
                isActive('/chat')
                  ? 'text-white border-b-2 border-white'
                  : 'text-slate-300 hover:text-white'
              } transition-colors px-1 py-1`}
            >
              Create Task
            </Link>
            
            <Link
              href="/tasks"
              className={`${
                isActive('/tasks')
                  ? 'text-white border-b-2 border-white'
                  : 'text-slate-300 hover:text-white'
              } transition-colors px-1 py-1`}
            >
              View Tasks
            </Link>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-400"></div>
              <span className="text-slate-300 text-sm">Connected</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}