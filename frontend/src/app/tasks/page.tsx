import TaskList from '@/components/TaskList'
import Link from 'next/link'

export default function TasksPage() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Your Tasks</h1>
          <p className="text-slate-600">View and manage your saved tasks</p>
        </div>
        <Link 
          href="/chat"
          className="bg-slate-900 text-white px-6 py-3 rounded-lg hover:bg-slate-800"
        >
          Create New Task
        </Link>
      </div>
      <TaskList />
    </div>
  )
}