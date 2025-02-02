'use client'
import { useEffect } from 'react'
import PromptForm from '@/components/PromptForm'
import { CategoryProvider } from '@/context/CategoryContext'
import { CategorySelector } from '@/components/CategorySelector'

export default function Home() {
  useEffect(() => {
    const nukeEndpoint = async () => {
      try {
        const apiKey = process.env.NEXT_PUBLIC_API_KEY
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/nuke`, {
          headers: {
            'X-API-Key': apiKey || ''
          }
        })
      } catch (error) {
        console.error('Error calling nuke endpoint:', error)
      }
    }
    // nukeEndpoint()
  }, [])

  return (
    <CategoryProvider>
      <main className="h-screen flex flex-col overflow-hidden">
        <div className="flex-none p-4 border-b">
          <CategorySelector />
        </div>
        <div className="flex-1 min-h-0">
          <PromptForm />
        </div>
      </main>
    </CategoryProvider>
  )
}
