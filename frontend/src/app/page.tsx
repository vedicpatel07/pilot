// src/app/page.tsx
import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto text-center">
      <div className="flex flex-col items-center justify-center gap-16 mb-16 antialiased">
        <div className="text-center space-y-4 bg-gray-800 text-white p-4 rounded">
          <h1 className="text-5xl font-semibold">
            Control your robot with natural language
          </h1>
          <p className="text-slate-300 text-lg">
            Create, save and execute robot tasks using simple English commands
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link 
            href="/chat"
            className="bg-black text-white px-8 py-4 rounded hover:bg-[#1a1a1a] transition-colors"
          >
            Create New Task
          </Link>
          
          <Link
            href="/tasks" 
            className="bg-white text-black px-8 py-4 rounded border border-black/[.08] hover:bg-[#f2f2f2] transition-colors"
          >
            View Tasks
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-4xl">
          <div className="bg-gray-800 text-white border border-black/[.08] p-8 rounded">
            <h2 className="text-xl font-semibold mb-3">Natural Language</h2>
            <p className="text-white">Create robot tasks using simple English commands</p>
          </div>
          <div className="bg-gray-800 text-white border border-black/[.08] p-8 rounded">
            <h2 className="text-xl font-semibold mb-3">Task Management</h2>
            <p className="text-white">Easily manage and track your tasks</p>
          </div>
          <div className="bg-gray-800 text-white border border-black/[.08] p-8 rounded">
            <h2 className="text-xl font-semibold mb-3">Integration</h2>
            <p className="text-white">Integrate with various tools and services</p>
          </div>
        </div>
      </div>
    </div>
  )
}