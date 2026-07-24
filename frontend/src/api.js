// src/api.js (Frontend client)

export async function queryEpisteme(question) {
  // Relative URL works perfectly because frontend and backend now share the same domain
  const API_BASE_URL = ""; 
  
  const response = await fetch(`${API_BASE_URL}/api/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ question })
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.error || `API error ${response.status}`);
  }

  return response.json();
}