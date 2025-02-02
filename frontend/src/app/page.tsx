'use client'
import PromptForm from '@/components/PromptForm'
import { CategoryProvider } from '@/context/CategoryContext'
import { CategorySelector } from '@/components/CategorySelector'

export default function Home() {
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
