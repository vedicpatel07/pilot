// src/app/api/tasks/execute/route.ts
import { NextResponse } from 'next/server'

// Assuming you have these types defined somewhere in your project
type Message = {
  role: 'user' | 'assistant'
  content: string
}

type Task = {
  id: string
  name: string
  messages: Message[]
  createdAt: string
  lastExecuted?: string
}

// Mock tasks database - in production, this would be your actual database
let tasks: Task[] = []

export async function POST(req: Request) {
  try {
    const { taskId, repetitions } = await req.json()

    // Validate input
    if (!taskId || !repetitions || repetitions < 1) {
      return NextResponse.json(
        { error: 'Invalid taskId or repetitions' },
        { status: 400 }
      )
    }

    // In production, this would be a call to your robot control service
    // For now, we'll simulate the execution with a delay
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Update the task's lastExecuted timestamp
    const now = new Date().toISOString()
    tasks = tasks.map(task =>
      task.id === taskId
        ? { ...task, lastExecuted: now }
        : task
    )

    // In production, you would send the actual execution status
    return NextResponse.json({
      success: true,
      executedAt: now,
      message: `Task executed ${repetitions} time${repetitions > 1 ? 's' : ''}`
    })

  } catch (error) {
    console.error('Error executing task:', error)
    return NextResponse.json(
      { error: 'Failed to execute task' },
      { status: 500 }
    )
  }
}

// For debugging purposes, you can also add a GET handler
export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const taskId = searchParams.get('taskId')

  if (!taskId) {
    return NextResponse.json(
      { error: 'taskId is required' },
      { status: 400 }
    )
  }

  const task = tasks.find(t => t.id === taskId)
  
  if (!task) {
    return NextResponse.json(
      { error: 'Task not found' },
      { status: 404 }
    )
  }

  return NextResponse.json({
    task,
    lastExecuted: task.lastExecuted
  })
}