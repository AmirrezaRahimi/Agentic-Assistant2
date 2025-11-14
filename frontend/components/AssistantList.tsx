"use client";

import clsx from "clsx";
import type { Assistant } from "@/lib/api";

interface AssistantListProps {
  assistants: Assistant[];
  selected?: string | null;
  onSelect?: (assistant: Assistant | null) => void;
  onDelete?: (assistant: Assistant) => void;
  onRefresh?: () => void;
  loading?: boolean;
}

export function AssistantList({
  assistants,
  selected,
  onSelect,
  onDelete,
  onRefresh,
  loading = false,
}: AssistantListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Your Assistants</h2>
        <button onClick={onRefresh} className="bg-slate-800 px-3 py-1 text-xs hover:bg-slate-700">
          Refresh
        </button>
      </div>
      {loading && <p className="text-sm text-slate-400">Loading...</p>}
      <ul className="space-y-2">
        {assistants.map((assistant) => (
          <li
            key={assistant.id}
            className={clsx(
              "flex cursor-pointer items-center justify-between rounded-lg border border-slate-800 px-4 py-3",
              selected === assistant.id ? "border-brand bg-slate-800" : "hover:border-slate-700"
            )}
            onClick={() => onSelect?.(assistant)}
          >
            <div>
              <p className="font-semibold">{assistant.name}</p>
              {assistant.description && <p className="text-xs text-slate-400">{assistant.description}</p>}
            </div>
            <button
              onClick={(event) => {
                event.stopPropagation();
                onDelete?.(assistant);
              }}
              className="bg-red-600 px-3 py-1 text-xs hover:bg-red-500"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      {!loading && assistants.length === 0 && (
        <p className="text-sm text-slate-500">No assistants yet. Create one to get started.</p>
      )}
    </div>
  );
}
