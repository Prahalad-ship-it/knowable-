export async function queryEpisteme(question) {
  const API_BASE_URL = import.meta.env.VITE_API_URL || https://knowable-production-ae19.up.railway.app/;
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
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