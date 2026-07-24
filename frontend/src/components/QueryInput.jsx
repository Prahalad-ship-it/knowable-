import { useEffect, useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { queryEpisteme } from './api' // 👈 This imports your new function!

export default function QueryInput({ value, onSubmit, status }) {
  const [input, setInput] = useState(value)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setInput(value)
  }, [value])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!input.trim() || isLoading) return

    setIsLoading(true)
    setError(null)

    try {
      // Send the query straight to the new API utility
      const data = await queryEpisteme(input)
      
      // Send the resulting data object back to App.jsx to update the UI
      if (onSubmit) onSubmit(data) 
    } catch (err) {
      setError(err.message || "Failed to fetch response.")
    } finally {
      setIsLoading(false)
    }
  }

  // ... keep the rest of your JSX template exactly the same as before ...