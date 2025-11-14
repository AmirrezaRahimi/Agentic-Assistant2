const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export interface Assistant {
  id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeDocument {
  id: string;
  assistant_id?: string;
  title: string;
  content: string;
}

export interface ConversationSession {
  id: string;
  assistant_id: string;
  title: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  session_id: string;
}

export interface ChatResponse {
  assistant_message: string;
  session: ConversationSession;
  messages: Message[];
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }

  return response.json();
}

export async function listAssistants(): Promise<Assistant[]> {
  return request<Assistant[]>("/assistants/");
}

export async function createAssistant(payload: Partial<Assistant>): Promise<Assistant> {
  return request<Assistant>("/assistants/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAssistant(id: string, payload: Partial<Assistant>): Promise<Assistant> {
  return request<Assistant>(`/assistants/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function deleteAssistant(id: string): Promise<void> {
  await request<void>(`/assistants/${id}`, { method: "DELETE" });
}

export async function listKnowledge(assistantId: string): Promise<KnowledgeDocument[]> {
  return request<KnowledgeDocument[]>(`/assistants/${assistantId}/knowledge/`);
}

export async function addKnowledge(
  assistantId: string,
  payload: { title: string; content: string }
): Promise<KnowledgeDocument> {
  return request<KnowledgeDocument>(`/assistants/${assistantId}/knowledge/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function chatNewSession(
  assistantId: string,
  payload: { user_message: string }
): Promise<ChatResponse> {
  return request<ChatResponse>(`/chat/assistants/${assistantId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function chatExistingSession(
  assistantId: string,
  sessionId: string,
  payload: { user_message: string }
): Promise<ChatResponse> {
  return request<ChatResponse>(`/chat/assistants/${assistantId}/sessions/${sessionId}`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
