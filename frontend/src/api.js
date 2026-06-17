export async function queryEpisteme(query) {
  const response = await fetch('http://127.0.0.1:8000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query })
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.error || `API error ${response.status}`)
  }

  return response.json()
}
