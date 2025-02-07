import { NextResponse } from 'next/server'

// This is a mock response. In production, this would connect to your actual backend
export async function POST(req: Request) {
  const { message } = await req.json()

  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 1000))

  // Mock response
  return NextResponse.json({
    message: `I understand you want to "${message}". I've broken this down into the following steps:\n1. First step\n2. Second step\n3. Third step\n\nWould you like me to save this as a task?`,
    commands: ['command1', 'command2', 'command3']
  })
}
