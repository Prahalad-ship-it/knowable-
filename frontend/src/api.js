/**
 * Sends a user query to the Episteme Research Agent backend.
 * Handles both local development and production routing seamlessly.
 */
export async function queryEpisteme(question) {
  // Determine backend base URL: 
  // Vercel routes '/api' locally via its CLI dev server, but if you run Vite separately, 
  // it needs to fallback to the standalone Flask server port (8000).
  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000' 
    : ''; 

  try {
    const response = await fetch(`${API_BASE_URL}/api/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ question: question.strip ? question.strip() : question })
    });

    // Capture response data safely
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      console.error('Backend returned an error status:', response.status, payload);
      throw new Error(payload?.error || `API error (${response.status}): Failed to fetch response.`);
    }

    return payload;
  } catch (error) {
    console.error('Network or Operational error in queryEpisteme:', error);
    throw error;
  }
}