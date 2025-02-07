import { NextResponse } from 'next/server'

// Mock database
let tasks = [
  {
    id: '1',
    name: 'Pick and Place Task',
    messages: [
      { role: 'user', content: 'Pick up the green box and place it in the bin' },
      { role: 'assistant', content: 'I understand you want to pick up the green box and place it in the bin. Here are the steps...' }
    ],
    createdAt: new Date().toISOString(),
    lastExecuted: null
  }
]

export async function GET() {
  return NextResponse.json({ tasks })
}

export async function POST(req: Request) {
  const body = await req.json()
  
  const newTask = {
    id: String(tasks.length + 1),
    ...body,
    createdAt: new Date().toISOString(),
    lastExecuted: null
  }
  
  tasks.push(newTask)
  return NextResponse.json({ task: newTask })
}