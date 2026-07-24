// src/api.js (Frontend client)

export async function queryEpisteme(question) {
  // Automatically falls back to the production URL if window.location isn't absolute
  const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:8000' 
    : 'https://episteme-calibration.vercel.app'; 
  
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