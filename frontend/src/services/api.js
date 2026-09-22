const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  if (!response.ok) {
    throw new Error(payload?.detail || "The analysis service could not complete this request.");
  }
  return payload;
}

export function analyzeText(text, conversationId = "custom_text") {
  return request("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, conversation_id: conversationId }),
  });
}

export function analyzeMessages(messages, conversationId = "custom_conversation") {
  return request("/api/analyze/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, conversation_id: conversationId }),
  });
}

export function analyzeFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/analyze/file", { method: "POST", body: formData });
}
