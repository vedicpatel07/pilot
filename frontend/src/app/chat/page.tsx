// src/app/chat/page.tsx
import ChatInterface from '@/components/ChatInterface'

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Create New Task</h1>
      <p className="text-slate-600 mb-8">Describe your task in natural language</p>
      <ChatInterface />
    </div>
  )
}