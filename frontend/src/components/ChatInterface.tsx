// src/components/ChatInterface.tsx
'use client';  // Add this at the very top
import { useState } from 'react'


type Message = {
  role: 'user' | 'assistant'
  content: string
}

type SaveTaskDialogProps = {
  onSave: (name: string) => void
  onCancel: () => void
}

// Save Task Dialog Component
function SaveTaskDialog({ onSave, onCancel }: SaveTaskDialogProps) {
  const [taskName, setTaskName] = useState('')

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-96">
        <h3 className="text-lg font-bold mb-4">Save Task</h3>
        <input
          type="text"
          value={taskName}
          onChange={(e) => setTaskName(e.target.value)}
          placeholder="Enter task name"
          className="w-full p-2 border border-slate-300 rounded-lg mb-4 focus:ring-2 focus:ring-slate-600 focus:border-transparent"
        />
        <div className="flex justify-end space-x-4">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-slate-600 hover:text-slate-900"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(taskName)}
            className="bg-slate-900 text-white px-4 py-2 rounded-lg hover:bg-slate-800"
            disabled={!taskName.trim()}
          >
            Save Task
          </button>
        </div>
      </div>
    </div>
  )
}

// Main Chat Interface Component
export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showSaveDialog, setShowSaveDialog] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    // Add user message to chat
    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Send message to backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      })

      if (!response.ok) throw new Error('Failed to send message')

      const data = await response.json()
      
      // Add assistant's response to chat
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message
      }
      setMessages(prev => [...prev, assistantMessage])

      // If the response includes task commands, show save dialog
      if (data.commands?.length > 0) {
        setShowSaveDialog(true)
      }
    } catch (error) {
      console.error('Error:', error)
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.'
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveTask = async (taskName: string) => {
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: taskName,
          messages: messages
        }),
      })

      if (!response.ok) throw new Error('Failed to save task')

      // Add success message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Task "${taskName}" has been saved successfully. You can find it in your tasks list.`
      }])
    } catch (error) {
      console.error('Error saving task:', error)
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error saving your task.'
      }])
    } finally {
      setShowSaveDialog(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-lg ${
                message.role === 'user'
                  ? 'bg-slate-900 text-white'
                  : 'bg-slate-100 text-slate-900'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 p-4 rounded-lg text-slate-900">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-200">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your task..."
            className="flex-1 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-600 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="bg-slate-900 text-white px-6 py-3 rounded-lg hover:bg-slate-800 
              disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || !input.trim()}
          >
            Send
          </button>
        </div>
      </form>

      {/* Save Task Dialog */}
      {showSaveDialog && (
        <SaveTaskDialog
          onSave={handleSaveTask}
          onCancel={() => setShowSaveDialog(false)}
        />
      )}
    </div>
  )
}