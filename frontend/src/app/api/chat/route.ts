import { NextResponse } from 'next/server'
import Anthropic from "@anthropic-ai/sdk";
import { promises as fs } from 'fs';
import path from 'path';

const anthropic = new Anthropic({
  apiKey: "put keys in the bag lil bro",
});

export async function POST(req: Request) {
  try {
    const { message } = await req.json()

    // Read the prompt file
    const promptPath = path.join(process.cwd(), 'src/app/prompts/robotInterpreter.txt');
    const systemPrompt = await fs.readFile(promptPath, 'utf8');

    const response = await anthropic.messages.create({
      model: "claude-3-5-sonnet-20241022",
      system: systemPrompt,
      messages: [{
        role: "user",
        content: message
      }],
      max_tokens: 1024,
      temperature: 0.7,
    });

    // Type check the response content
    const content = response.content[0];
    if (content.type !== 'text') {
      throw new Error('Unexpected response type from Claude');
    }

    return NextResponse.json({
      message: content.text,
      success: true
    });

  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({
      message: "Unable to connect to Claude. Please try again later.",
      success: false
    }, { status: 500 });
  }
}