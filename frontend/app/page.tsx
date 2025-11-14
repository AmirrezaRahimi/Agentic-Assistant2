"use client";

import { useEffect, useState } from "react";
import type { Assistant } from "@/lib/api";
import { deleteAssistant, listAssistants } from "@/lib/api";
import { AssistantForm } from "@/components/AssistantForm";
import { AssistantList } from "@/components/AssistantList";
import { ChatPanel } from "@/components/ChatPanel";

export default function HomePage() {
  const [assistants, setAssistants] = useState<Assistant[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAssistant, setSelectedAssistant] = useState<Assistant | null>(null);

  const loadAssistants = async () => {
    setLoading(true);
    try {
      const data = await listAssistants();
      setAssistants(data);
      if (!selectedAssistant && data.length) {
        setSelectedAssistant(data[0]);
      } else if (selectedAssistant) {
        const updated = data.find((item) => item.id === selectedAssistant.id) ?? null;
        setSelectedAssistant(updated);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAssistants();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async (assistant: Assistant) => {
    if (!confirm(`Delete assistant "${assistant.name}"?`)) return;
    await deleteAssistant(assistant.id);
    await loadAssistants();
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <div className="space-y-6">
        <AssistantForm
          onCreated={(assistant) => {
            setAssistants((prev) => [assistant, ...prev]);
            setSelectedAssistant(assistant);
          }}
        />
        <AssistantList
          assistants={assistants}
          selected={selectedAssistant?.id ?? null}
          onSelect={(assistant) => setSelectedAssistant(assistant)}
          onDelete={handleDelete}
          onRefresh={() => void loadAssistants()}
          loading={loading}
        />
      </div>
      <ChatPanel assistant={selectedAssistant} />
    </div>
  );
}
