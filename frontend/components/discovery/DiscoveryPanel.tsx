"use client";

import { useState } from "react";
import { useDiscoveryStream } from "@/hooks/useDiscoveryStream";
import type { Customer } from "@/lib/types";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import StatusTicker from "@/components/common/StatusTicker";
import CopyButton from "@/components/common/CopyButton";
import { downloadText } from "@/lib/utils";

interface Props {
  customer: Customer;
  onBriefSaved?: () => void;
}

export default function DiscoveryPanel({ customer, onBriefSaved }: Props) {
  const [website, setWebsite] = useState("");
  const [notes, setNotes] = useState("");
  const { state, generateBrief, cancel } = useDiscoveryStream();

  const isRunning = !state.done && (state.connecting || state.status !== "");
  const hasResult = state.done && state.fullResponse;

  async function handleGenerate() {
    await generateBrief(customer.id, { website, notes, save_as_conversation: true });
    onBriefSaved?.();
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Form */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-3">
          Generate Discovery Brief — {customer.name}
        </h2>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Company Website
            </label>
            <input
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              placeholder="https://www.example.com"
              disabled={isRunning}
              className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
                bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                placeholder-gray-400 dark:placeholder-gray-500
                focus:outline-none focus:ring-2 focus:ring-aws-orange disabled:opacity-60"
            />
          </div>
          <div className="flex items-end">
            {isRunning ? (
              <button
                onClick={cancel}
                className="w-full px-4 py-2 text-sm font-semibold text-white bg-red-500
                  hover:bg-red-600 rounded-lg transition-colors"
              >
                Stop
              </button>
            ) : (
              <button
                onClick={handleGenerate}
                className="w-full px-4 py-2 text-sm font-semibold text-white bg-aws-orange
                  hover:bg-aws-orange-dk rounded-lg transition-colors"
              >
                Generate Brief
              </button>
            )}
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
            Notes / Context
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Pre-call notes, recent news, known pain points…"
            rows={2}
            disabled={isRunning}
            className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm
              bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
              placeholder-gray-400 dark:placeholder-gray-500
              focus:outline-none focus:ring-2 focus:ring-aws-orange resize-none disabled:opacity-60"
          />
        </div>

        {isRunning && (
          <div className="mt-2">
            <StatusTicker
              message={state.connecting ? "⏳  Connecting to discovery agent…" : state.status}
              visible
            />
          </div>
        )}
      </div>

      {/* Result */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {!hasResult && !isRunning && (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div className="text-4xl mb-4">🎯</div>
            <p className="text-sm text-gray-500 max-w-md">
              Enter the company website and click Generate Brief to create a
              compliance-aware financial services discovery brief powered by web
              research and regulatory context.
            </p>
          </div>
        )}

        {isRunning && state.tokens && (
          <MarkdownRenderer content={state.tokens} />
        )}

        {state.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            Error: {state.error}
          </div>
        )}

        {hasResult && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <CopyButton text={state.fullResponse} label="Copy brief" />
              <button
                onClick={() =>
                  downloadText(
                    `discovery-brief-${customer.name.replace(/\s+/g, "-").toLowerCase()}.md`,
                    state.fullResponse
                  )
                }
                className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium
                  rounded border border-gray-300 bg-white hover:bg-gray-50 text-gray-600"
              >
                ⬇ Download
              </button>
              <span className="text-xs text-green-600 font-medium ml-1">
                ✓ Saved as conversation
              </span>
            </div>
            <MarkdownRenderer content={state.fullResponse} />
          </div>
        )}
      </div>
    </div>
  );
}
