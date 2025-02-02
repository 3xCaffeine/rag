'use client'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useCategory } from '@/context/CategoryContext'

export function CategorySelector() {
  const { category, setCategory } = useCategory();
  
  return (
    <Select value={category} onValueChange={setCategory}>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select category" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="medical">Medical</SelectItem>
        <SelectItem value="law">Law</SelectItem>
        <SelectItem value="tech">Technical</SelectItem>
        <SelectItem value="architecture">Architecture</SelectItem>
        <SelectItem value="literature">Literature</SelectItem>
        <SelectItem value="finance">Finance</SelectItem>
      </SelectContent>
    </Select>
  )
}
