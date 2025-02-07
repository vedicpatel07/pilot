// src/app/tasks/page.tsx
import TaskList from '@/components/TaskList'

export default function TasksPage() {
  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Your Tasks</h1>
            <p className="text-slate-600 mt-2">
              View and manage all your saved robot tasks
            </p>
          </div>
          <div>
            <button 
              onClick={() => window.location.href = '/chat'}
              className="bg-slate-900 text-white px-6 py-3 rounded-lg hover:bg-slate-800
                transition-colors shadow-md hover:shadow-lg"
            >
              Create New Task
            </button>
          </div>
        </div>
      </div>

      <div className="bg-slate-50 rounded-xl p-6">
        <TaskList />
      </div>
    </div>
  )
}