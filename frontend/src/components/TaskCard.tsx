'use client';

import { useState } from 'react'

type Task = {
  id: string
  name: string
  messages: {
    role: 'user' | 'assistant'
    content: string
  }[]
  createdAt: string
  lastExecuted?: string
}

interface TaskCardProps {
  task: Task
  onExecute: (taskId: string, repetitions: number) => Promise<void>
}

export default function TaskCard({ task, onExecute }: TaskCardProps) {
  const [showExecuteDialog, setShowExecuteDialog] = useState(false)
  const [repetitions, setRepetitions] = useState(1)
  const [isExecuting, setIsExecuting] = useState(false)

  const handleExecute = async () => {
    try {
      setIsExecuting(true)
      await onExecute(task.id, repetitions)
      setShowExecuteDialog(false)
    } catch (error) {
      console.error('Error executing task:', error)
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Task Header */}
      <div className="p-6 border-b border-slate-100">
        <h3 className="text-xl font-bold text-slate-900 mb-2">
          {task.name}
        </h3>
        <div className="flex items-center text-sm text-slate-500">
          <span>Created: {new Date(task.createdAt).toLocaleDateString()}</span>
          {task.lastExecuted && (
            <>
              <span className="mx-2">•</span>
              <span>Last run: {new Date(task.lastExecuted).toLocaleDateString()}</span>
            </>
          )}
        </div>
      </div>

      {/* Task Preview */}
      <div className="px-6 py-4 bg-slate-50">
        <div className="text-sm text-slate-600 mb-4">
          <p className="font-medium mb-1">Task Description:</p>
          <p className="line-clamp-2">
            {task.messages[0]?.content || 'No description available'}
          </p>
        </div>
      </div>

      {/* Task Actions */}
      <div className="px-6 py-4 flex justify-between items-center">
        <button
          onClick={() => setShowExecuteDialog(true)}
          className="bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800
            transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isExecuting}
        >
          {isExecuting ? 'Executing...' : 'Execute Task'}
        </button>
      </div>

      {/* Execute Dialog */}
      {showExecuteDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96 shadow-xl">
            <h3 className="text-lg font-bold mb-4 text-slate-900">
              Execute Task: {task.name}
            </h3>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Number of repetitions
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={repetitions}
                onChange={(e) => setRepetitions(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 
                  focus:ring-slate-600 focus:border-transparent"
              />
            </div>

            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowExecuteDialog(false)}
                className="px-4 py-2 text-slate-600 hover:text-slate-900"
                disabled={isExecuting}
              >
                Cancel
              </button>
              <button
                onClick={handleExecute}
                className="bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800
                  disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isExecuting}
              >
                {isExecuting ? 'Executing...' : 'Execute'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}