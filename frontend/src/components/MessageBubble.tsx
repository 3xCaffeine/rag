'use client'
import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ChevronDown, ChevronRight } from "lucide-react"
import ReactMarkdown from 'react-markdown';
import TypingIndicator from './TypingIndicator'

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
  isLoading?: boolean
  isStreaming?: boolean
}

export default function MessageBubble({ role, content, isLoading, isStreaming }: MessageBubbleProps) {
  const [isThoughtOpen, setIsThoughtOpen] = useState(false)
  const [displayedContent, setDisplayedContent] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  
  const thoughtMatch = content.match(/<think>(.*?)<\/think>/s)
  const thought = thoughtMatch ? thoughtMatch[1].trim() : null
  const cleanContent = content.replace(/<think>.*?<\/think>/s, '').trim()

  useEffect(() => {
    if (!isStreaming || role === 'user') {
      setDisplayedContent(content)
      return
    }

    if (currentIndex < content.length) {
      const timer = setTimeout(() => {
        setDisplayedContent(content.substring(0, currentIndex + 1))
        setCurrentIndex(currentIndex + 1)
      }, 10) // Adjust speed as needed

      return () => clearTimeout(timer)
    }
  }, [content, currentIndex, isStreaming, role])

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
            {isLoading ? (
              <TypingIndicator />
            ) : (
              <ReactMarkdown className="prose prose-invert max-w-none">
                {isStreaming ? displayedContent : cleanContent}
              </ReactMarkdown>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
