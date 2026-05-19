"use client";

import { useState } from "react";
import useSWR from "swr";
import type { KBSource, KnowledgeBaseStatus } from "@/lib/types";
import { kbApi } from "@/lib/api";

interface Props {
  status: KnowledgeBaseStatus | undefined;
  onIngestTriggered?: () => void;
}

const TIER_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Core FinServ", color: "bg-aws-orange/10 text-aws-orange border-aws-orange/30" },
  2: { label: "Extended",     color: "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800" },
  3: { label: "Reference",    color: "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700" },
};

const PILLARS = [
  { icon: "🏗️", label: "Architecture" },
  { icon: "📈", label: "Scalability" },
  { icon: "🔭", label: "Observability" },
  { icon: "💰", label: "Cost Optimization" },
  { icon: "🔒", label: "Security" },
];

function groupByTier(sources: KBSource[]): Record<number, KBSource[]> {
  const groups: Record<number, KBSource[]> = {};
  for (const s of sources) {
    const t = s.tier ?? 3;
    if (!groups[t]) groups[t] = [];
    groups[t].push(s);
  }
  return groups;
}

export default function KnowledgeBasePanel({ status, onIngestTriggered }: Props) {
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  const { data, mutate: mutateSources } = useSWR("kb-sources", kbApi.sources, {
    refreshInterval: 120_000,
  });

  const sources = data?.sources ?? [];
  const groups = groupByTier(sources);
  const tiers = Object.keys(groups).map(Number).sort((a, b) => a - b);

  const isIndexing = status?.ingest_running;
  const chunkCount = status?.chunk_count ?? 0;

  async function handleTrigger() {
    setTriggering(true);
    setTriggerMsg(null);
    try {
      const res = await kbApi.triggerIngest();
      setTriggerMsg(res.message ?? "Indexing started — check back in 15–20 minutes.");
      onIngestTriggered?.();
      // Refresh sources after a short delay
      setTimeout(() => mutateSources(), 5000);
    } catch (err: unknown) {
      setTriggerMsg((err as Error).message ?? "Failed to start indexing.");
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1">
            AWS Knowledge Base
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Every response is grounded in current AWS documentation — architecture, scalability,
            observability, cost optimization, and security built into every recommendation.
          </p>
        </div>
        <button
          onClick={handleTrigger}
          disabled={triggering || !!isIndexing}
          title={isIndexing ? "Indexing already in progress" : "Scrape and index all AWS documentation now"}
          className="flex-shrink-0 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-colors
            disabled:opacity-50 disabled:cursor-not-allowed
            border-aws-orange text-aws-orange hover:bg-aws-orange hover:text-white
            dark:border-aws-orange dark:text-aws-orange dark:hover:bg-aws-orange dark:hover:text-white"
        >
          {triggering ? "Starting…" : isIndexing ? "Indexing…" : "Run Indexer"}
        </button>
      </div>

      {/* Trigger feedback */}
      {triggerMsg && (
        <div className="px-3 py-2 rounded-lg text-xs bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300">
          {triggerMsg}
        </div>
      )}

      {/* Well-Architected pillars */}
      <div className="grid grid-cols-5 gap-2">
        {PILLARS.map((p) => (
          <div
            key={p.label}
            className="flex flex-col items-center gap-1 p-2 rounded-lg
              bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-center"
          >
            <span className="text-xl">{p.icon}</span>
            <span className="text-[10px] font-medium text-gray-600 dark:text-gray-400 leading-tight">
              {p.label}
            </span>
          </div>
        ))}
      </div>

      {/* Stats bar */}
      <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
        <div className="text-center flex-1">
          <div className="text-xl font-bold text-aws-orange">
            {chunkCount > 0 ? chunkCount.toLocaleString() : "—"}
          </div>
          <div className="text-[10px] text-gray-500 dark:text-gray-400">Indexed chunks</div>
        </div>
        <div className="w-px h-8 bg-gray-200 dark:bg-gray-700" />
        <div className="text-center flex-1">
          <div className="text-xl font-bold text-gray-800 dark:text-gray-200">
            {sources.length > 0 ? sources.length : "—"}
          </div>
          <div className="text-[10px] text-gray-500 dark:text-gray-400">Services indexed</div>
        </div>
        <div className="w-px h-8 bg-gray-200 dark:bg-gray-700" />
        <div className="text-center flex-1">
          <div className={`text-xs font-semibold ${isIndexing ? "text-yellow-600 dark:text-yellow-400" : chunkCount > 0 ? "text-green-600 dark:text-green-400" : "text-gray-400 dark:text-gray-500"}`}>
            {isIndexing ? "Indexing…" : chunkCount > 0 ? "Ready" : "Empty"}
          </div>
          <div className="text-[10px] text-gray-500 dark:text-gray-400">Status</div>
        </div>
      </div>

      {/* Source list by tier */}
      {sources.length === 0 ? (
        <div className="text-center py-8 text-sm text-gray-400 dark:text-gray-500">
          {isIndexing
            ? "Indexing AWS documentation… check back in 15–20 minutes."
            : "No sources indexed yet. Click \"Run Indexer\" above to start."}
        </div>
      ) : (
        <div className="space-y-4">
          {tiers.map((tier) => {
            const meta = TIER_LABELS[tier] ?? TIER_LABELS[3];
            return (
              <div key={tier}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${meta.color}`}>
                    Tier {tier} — {meta.label}
                  </span>
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">
                    {groups[tier].length} service{groups[tier].length !== 1 ? "s" : ""}
                  </span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {groups[tier].map((s) => (
                    <div
                      key={s.source_label}
                      title={`${s.chunk_count.toLocaleString()} chunks · last indexed ${s.last_indexed ?? "unknown"}`}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs
                        bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700
                        text-gray-700 dark:text-gray-300 hover:border-aws-orange/50 transition-colors cursor-default"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0" />
                      {s.source_label}
                      <span className="text-gray-400 dark:text-gray-600 text-[10px]">
                        {s.chunk_count}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer note */}
      <p className="text-[10px] text-gray-400 dark:text-gray-600 border-t border-gray-100 dark:border-gray-800 pt-3">
        Documentation refreshed weekly · Sources include AWS User Guides, Developer Guides,
        Prescriptive Guidance, Solutions Library, and Reference Architecture Center.
      </p>
    </div>
  );
}
