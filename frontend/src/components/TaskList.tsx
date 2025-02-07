'use client';

import { useState, useEffect } from 'react'
import TaskCard from './TaskCard'

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

export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [executingTaskId, setExecutingTaskId] = useState<string | null>(null)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await fetch('/api/tasks')
      
      if (!response.ok) {
        throw new Error('Failed to fetch tasks')
      }

      const data = await response.json()
      setTasks(data.tasks)
    } catch (error) {
      console.error('Error fetching tasks:', error)
      setError('Failed to load tasks. Please try again later.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExecuteTask = async (taskId: string, repetitions: number) => {
    try {
      setExecutingTaskId(taskId)
      const response = await fetch('/api/tasks/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId, repetitions }),
      })

      if (!response.ok) {
        throw new Error('Failed to execute task')
      }

      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId
            ? { ...task, lastExecuted: new Date().toISOString() }
            : task
        )
      )
    } catch (error) {
      console.error('Error executing task:', error)
      throw error
    } finally {
      setExecutingTaskId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="flex items-center space-x-4">
          <div className="w-3 h-3 bg-slate-900 rounded-full animate-bounce" />
          <div className="w-3 h-3 bg-slate-800 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
          <div className="w-3 h-3 bg-slate-700 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <button
              onClick={fetchTasks}
              className="mt-2 text-sm font-medium text-red-800 hover:text-red-900"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-slate-900 mb-2">
          No tasks yet
        </h3>
        <p className="text-slate-600 mb-4">
          Create your first task by using the chat interface
        </p>
        <a
          href="/chat"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md 
            text-white bg-slate-900 hover:bg-slate-800"
        >
          Create New Task
        </a>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onExecute={handleExecuteTask}
        />
      ))}
    </div>
  )
}