"use client";

import { useEffect, useState } from "react";
import type { Assistant, ChatResponse, KnowledgeDocument, Message } from "@/lib/api";
import { addKnowledge, chatExistingSession, chatNewSession, listKnowledge } from "@/lib/api";

interface ChatPanelProps {
  assistant: Assistant | null;
}

export function ChatPanel({ assistant }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [knowledge, setKnowledge] = useState<KnowledgeDocument[]>([]);
  const [knowledgeTitle, setKnowledgeTitle] = useState("");
  const [knowledgeContent, setKnowledgeContent] = useState("");
  const [loadingKnowledge, setLoadingKnowledge] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (!assistant) {
      setMessages([]);
      setKnowledge([]);
      setSessionId(null);
      return;
    }

    const fetchKnowledge = async () => {
      setLoadingKnowledge(true);
      try {
        const docs = await listKnowledge(assistant.id);
        setKnowledge(docs);
      } finally {
        setLoadingKnowledge(false);
      }
    };

    void fetchKnowledge();
  }, [assistant?.id]);

  const handleSend = async () => {
    if (!assistant || !input.trim()) return;
    setIsSending(true);
    try {
      let response: ChatResponse;
      if (sessionId) {
        response = await chatExistingSession(assistant.id, sessionId, { user_message: input });
      } else {
        response = await chatNewSession(assistant.id, { user_message: input });
        setMessages([]); // clear to avoid mixing previous assistant history
      }
      setSessionId(response.session.id);
      setMessages((prev) => [...prev, ...response.messages]);
      setInput("");
    } finally {
      setIsSending(false);
    }
  };

  const handleAddKnowledge = async () => {
    if (!assistant || !knowledgeTitle.trim() || !knowledgeContent.trim()) return;
    const doc = await addKnowledge(assistant.id, { title: knowledgeTitle, content: knowledgeContent });
    setKnowledge((prev) => [...prev, doc]);
    setKnowledgeTitle("");
    setKnowledgeContent("");
  };

  if (!assistant) {
    return <p className="text-sm text-slate-400">Select an assistant to start chatting.</p>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div className="flex flex-col gap-4 rounded-lg border border-slate-800 bg-slate-900 p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Conversation</h2>
          <span className="text-xs text-slate-400">Assistant: {assistant.name}</span>
        </div>
        <div className="flex flex-1 flex-col gap-3 overflow-y-auto rounded border border-slate-800 bg-slate-950 p-4">
          {messages.length === 0 && <p className="text-sm text-slate-500">No messages yet. Say hello!</p>}
          {messages.map((message) => (
            <div key={message.id} className="space-y-1 rounded border border-slate-800 bg-slate-900 p-3">
              <p className="text-xs uppercase tracking-wide text-slate-400">{message.role}</p>
              <p className="whitespace-pre-line text-sm text-slate-100">{message.content}</p>
            </div>
          ))}
        </div>
        <div className="flex items-end gap-3">
          <textarea
            className="h-24 flex-1"
            value={input}
            placeholder="Ask something"
            onChange={(event) => setInput(event.target.value)}
          />
          <button onClick={handleSend} disabled={isSending}>
            {isSending ? "Sending..." : sessionId ? "Send" : "Start Chat"}
          </button>
        </div>
      </div>

      <div className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-5">
        <div>
          <h2 className="text-lg font-semibold">Knowledge Base</h2>
          {loadingKnowledge && <p className="text-xs text-slate-400">Loading snippets...</p>}
        </div>
        <ul className="max-h-60 space-y-3 overflow-y-auto">
          {knowledge.map((doc) => (
            <li key={doc.id} className="rounded border border-slate-800 bg-slate-950 p-3">
              <p className="font-semibold">{doc.title}</p>
              <p className="text-xs text-slate-400">
                {doc.content.slice(0, 180)}
                {doc.content.length > 180 ? "..." : ""}
              </p>
            </li>
          ))}
          {!loadingKnowledge && knowledge.length === 0 && (
            <p className="text-xs text-slate-400">No knowledge yet. Add documents below.</p>
          )}
        </ul>
        <div className="space-y-3">
          <input
            placeholder="Document title"
            value={knowledgeTitle}
            onChange={(event) => setKnowledgeTitle(event.target.value)}
          />
          <textarea
            placeholder="Document content"
            rows={4}
            value={knowledgeContent}
            onChange={(event) => setKnowledgeContent(event.target.value)}
          />
          <button className="w-full" onClick={() => void handleAddKnowledge()}>
            Add Knowledge
          </button>
        </div>
      </div>
    </div>
  );
}
