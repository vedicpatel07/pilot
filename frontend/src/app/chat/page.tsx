import Link from 'next/link'
import ChatInterface from '@/components/ChatInterface'

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">Create New Task</h1>
      <p className="text-slate-600 mb-8">Describe your task in natural language</p>
      <ChatInterface />
      <div className="mt-4">
        <Link href="/">
          <a className="text-blue-500 hover:underline">Go to Home Page</a>
        </Link>
        <Link href="/tasks">
          <a className="text-blue-500 hover:underline ml-4">Go to Tasks Page</a>
        </Link>
      </div>
    </div>
  )
}