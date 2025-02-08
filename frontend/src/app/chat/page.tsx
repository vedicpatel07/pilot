import ChatInterface from '@/components/ChatInterface'
import Link from 'next/link'

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-black p-4 rounded-lg text-white">
        <div className="flex justify-between mb-4">
          <Link href="/" className="bg-white text-black p-2 rounded hover:bg-gray-200">
            Home
          </Link>
          <Link href="/tasks" className="bg-white text-black p-2 rounded hover:bg-gray-200">
            View Tasks
          </Link>
        </div>
        <h1 className="text-3xl font-bold mb-2">Create New Task</h1>
        <p className="mb-4">Describe your task in natural language</p>
        <ChatInterface />
      </div>
    </div>
  )
}