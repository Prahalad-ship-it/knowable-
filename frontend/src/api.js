export async function queryEpisteme(question) {
  // Use absolute URL locally, but use a relative path in production
  const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:8000' 
    : ''; // Empty string means it stays on the current domain

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