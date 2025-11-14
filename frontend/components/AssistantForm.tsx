"use client";

import { useState } from "react";
import type { Assistant } from "@/lib/api";
import { createAssistant } from "@/lib/api";

interface AssistantFormProps {
  onCreated?: (assistant: Assistant) => void;
}

export function AssistantForm({ onCreated }: AssistantFormProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const assistant = await createAssistant({ name, description, system_prompt: systemPrompt });
      setName("");
      setDescription("");
      setSystemPrompt("");
      onCreated?.(assistant);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create assistant");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-5 shadow-lg">
      <div>
        <h2 className="text-lg font-semibold">Create Assistant</h2>
        <p className="text-xs text-slate-400">Define a persona and optional system instructions.</p>
      </div>
      <div className="grid gap-3">
        <label className="text-xs uppercase tracking-wide text-slate-400">Name</label>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Support Bot" required />
      </div>
      <div className="grid gap-3">
        <label className="text-xs uppercase tracking-wide text-slate-400">Description</label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={2}
          placeholder="Short summary"
        />
      </div>
      <div className="grid gap-3">
        <label className="text-xs uppercase tracking-wide text-slate-400">System Prompt</label>
        <textarea
          value={systemPrompt}
          onChange={(event) => setSystemPrompt(event.target.value)}
          rows={3}
          placeholder="Respond in a friendly, concise tone."
        />
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}
      <button type="submit" disabled={isSubmitting} className="w-full disabled:opacity-60">
        {isSubmitting ? "Creating..." : "Create Assistant"}
      </button>
    </form>
  );
}
