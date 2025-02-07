// src/app/page.tsx
import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto text-center">
      <h1 className="text-4xl font-bold text-slate-900 mb-6">
        Robot Task Automation
      </h1>
      
      <p className="text-xl text-slate-600 mb-12">
        Create, manage, and automate physical tasks using natural language commands
      </p>

      <div className="flex flex-col sm:flex-row justify-center gap-4">
        <Link 
          href="/chat"
          className="bg-slate-900 text-white px-8 py-4 rounded-lg hover:bg-slate-800 transition-colors
            text-lg font-semibold shadow-lg hover:shadow-xl"
        >
          Create New Task
        </Link>
        
        <Link
          href="/tasks"
          className="bg-slate-800 text-white px-8 py-4 rounded-lg hover:bg-slate-700 transition-colors
            text-lg font-semibold shadow-lg hover:shadow-xl"
        >
          View All Tasks
        </Link>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-slate-900 mb-3">Natural Language</h2>
          <p className="text-slate-600">
            Describe tasks in plain English and let our AI translate them into robot commands
          </p>
        </div>

        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-slate-900 mb-3">Save & Reuse</h2>
          <p className="text-slate-600">
            Store your most common tasks and execute them again with a single click
          </p>
        </div>

        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-slate-900 mb-3">Automation</h2>
          <p className="text-slate-600">
            Set task repetitions and let the robot handle your repetitive workflows
          </p>
        </div>
      </div>
    </div>
  )
}