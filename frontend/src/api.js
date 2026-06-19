export async function queryEpisteme(question) {
  const response = await fetch('http://127.0.0.1:8000/api/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question })
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.error || `API error ${response.status}`)
  }

  return response.json()
}