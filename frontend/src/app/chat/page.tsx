// src/app/chat/page.tsx
import ChatInterface from '@/components/ChatInterface'

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Create New Task</h1>
        <p className="text-slate-600 mt-2">
          Describe your task in natural language and our AI will help you create it
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-1">
        <ChatInterface />
      </div>
    </div>
  )
}
