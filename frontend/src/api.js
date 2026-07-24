/**
 * Sends a user query to the Episteme Flask backend.
 * Handles local development (port 8000) and production on Vercel automatically.
 */
export async function queryEpisteme(question) {
  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000' 
    : ''; // Empty string lets Vercel route it relatively on the same domain

  try {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: question.trim() })
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      console.error('Backend error:', response.status, payload);
      throw new Error(payload?.error || `API error (${response.status})`);
    }

    return payload; // Returns the parsed backend object
  } catch (error) {
    console.error('Network error in queryEpisteme:', error);
    throw error;
  }
}