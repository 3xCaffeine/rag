'use client'
import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronDown, ChevronRight } from "lucide-react"

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
}

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  const [isThoughtOpen, setIsThoughtOpen] = useState(false)
  
  const thoughtMatch = content.match(/<think>(.*?)<\/think>/s)
  const thought = thoughtMatch ? thoughtMatch[1].trim() : null
  const cleanContent = content.replace(/<think>.*?<\/think>/s, '').trim()

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] space-y-2 ${role === 'user' ? 'items-end' : 'items-start'}`}>
        {thought && role === 'assistant' && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsThoughtOpen(!isThoughtOpen)}
            className="text-muted-foreground"
          >
            {isThoughtOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            Thought Process
          </Button>
        )}
        
        {thought && isThoughtOpen && (
          <Card className="bg-muted">
            <CardContent className="p-3 text-sm">
              {thought}
            </CardContent>
          </Card>
        )}

        <Card className={`border-0 ${
          role === 'user' 
            ? 'bg-primary text-primary-foreground' 
            : 'bg-muted'
        }`}>
          <CardContent className="p-3">
            {cleanContent}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
