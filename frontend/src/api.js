export async function queryEpisteme(question) {
  // Talk to local standalone Flask server on port 8000, or route relatively on production Vercel
  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000' 
    : ''; 

  try {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: question })
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(payload?.error || `API error (${response.status})`);
    }

    return payload;
  } catch (error) {
    console.error('Network or Operational error in queryEpisteme:', error);
    throw error;
  }
}