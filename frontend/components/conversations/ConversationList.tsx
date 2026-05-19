"use client";

import { useState } from "react";
import Link from "next/link";
import type { Conversation } from "@/lib/types";
import { conversationsApi } from "@/lib/api";
import { timeAgo } from "@/lib/utils";

interface Props {
  customerId: string;
  conversations: Conversation[];
  activeConvId?: string;
  onCreated: (conv: Conversation) => void;
  onDeleted: (convId: string) => void;
  /** When set, conversations link back to this project page */
  projectId?: string;
  /** Override the default create conversation call for project-scoped creation */
  createConversation?: () => Promise<Conversation>;
}

export default function ConversationList({
  customerId,
  conversations,
  activeConvId,
  onCreated,
  onDeleted,
  projectId,
  createConversation,
}: Props) {
  const [creating, setCreating] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  async function handleNew() {
    setCreating(true);
    try {
      const conv = createConversation
        ? await createConversation()
        : await conversationsApi.create(customerId);
      onCreated(conv);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(convId: string) {
    await conversationsApi.delete(convId);
    onDeleted(convId);
    setConfirmDelete(null);
  }

  return (
    <div>
      <div className="flex items-center justify-between px-1 mb-2">
        <h3 className="text-sm font-semibold text-gray-700">Conversations</h3>
        <button
          onClick={handleNew}
          disabled={creating}
          className="flex items-center gap-1 text-xs text-aws-orange hover:text-aws-orange-dk
            font-semibold px-2 py-1 rounded hover:bg-orange-50 disabled:opacity-50"
        >
          + New
        </button>
      </div>

      {conversations.length === 0 ? (
        <p className="text-xs text-gray-400 text-center py-4">
          No conversations yet.{" "}
          <button onClick={handleNew} className="text-aws-orange hover:underline">
            Start one
          </button>
        </p>
      ) : (
        <ul className="space-y-1">
          {conversations.map((c) => (
            <li
              key={c.id}
              className={`group flex items-center justify-between rounded-lg px-3 py-2
                transition-colors text-sm
                ${c.id === activeConvId
                  ? "bg-orange-50 border border-aws-orange/30"
                  : "hover:bg-gray-50 border border-transparent"
                }`}
            >
              <Link
                href={`/customers/${customerId}/conversations/${c.id}${projectId ? `?projectId=${projectId}` : ""}`}
                className="flex-1 min-w-0"
              >
                <div className="truncate font-medium text-gray-900">{c.title}</div>
                <div className="text-xs text-gray-400">{timeAgo(c.updated_at)}</div>
              </Link>

              {/* Delete button */}
              {confirmDelete === c.id ? (
                <div className="flex items-center gap-1 ml-2 flex-shrink-0">
                  <button
                    onClick={() => handleDelete(c.id)}
                    className="text-xs text-white bg-red-500 hover:bg-red-600
                      px-1.5 py-0.5 rounded"
                  >
                    Del
                  </button>
                  <button
                    onClick={() => setConfirmDelete(null)}
                    className="text-xs text-gray-500 hover:text-gray-700 px-1 py-0.5"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmDelete(c.id)}
                  className="opacity-0 group-hover:opacity-100 ml-2 flex-shrink-0
                    text-gray-300 hover:text-red-500 transition-all text-base leading-none"
                >
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
