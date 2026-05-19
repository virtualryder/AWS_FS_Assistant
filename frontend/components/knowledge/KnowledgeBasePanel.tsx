"use client";

import { useState } from "react";
import type { KnowledgeBaseStatus, SeedEntry } from "@/lib/types";
import { kbApi } from "@/lib/api";

interface Props {
  status: KnowledgeBaseStatus | undefined;
  onIngestTriggered?: () => void;
}

const TIER_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Core FinServ",  color: "bg-aws-orange/10 text-aws-orange border-aws-orange/30" },
  2: { label: "Extended",      color: "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800" },
  3: { label: "Reference",     color: "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700" },
};

function groupByTier(seeds: SeedEntry[]): Record<number, SeedEntry[]> {
  const groups: Record<number, SeedEntry[]> = {};
  for (const s of seeds) {
    const t = s.tier ?? 1;
    if (!groups[t]) groups[t] = [];
    groups[t].push(s);
  }
  return groups;
}

function formatDate(iso: string | null): string {
  if (!iso) return "never";
  try {
    return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch {
    return "unknown";
  }
}

function ServiceTile({ seed, isCurrentlyIndexing }: { seed: SeedEntry; isCurrentlyIndexing: boolean }) {
  const [expanded, setExpanded] = useState(false);

  const statusColor = isCurrentlyIndexing
    ? "border-yellow-400 dark:border-yellow-500 bg-yellow-50 dark:bg-yellow-950/30"
    : seed.indexed
    ? "border-green-300 dark:border-green-700 bg-white dark:bg-gray-900"
    : "border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50";

  const dotColor = isCurrentlyIndexing
    ? "bg-yellow-400 animate-pulse"
    : seed.indexed
    ? "bg-green-400"
    : "bg-gray-300 dark:bg-gray-600";

  return (
    <div className={`rounded-lg border transition-colors ${statusColor}`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-2.5 py-1.5 text-left"
      >
        {isCurrentlyIndexing ? (
          <span className="w-2 h-2 rounded-full bg-yellow-400 animate-ping flex-shrink-0" />
        ) : (
          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />
        )}
        <span className="flex-1 text-xs font-medium text-gray-800 dark:text-gray-200 truncate">
          {seed.name}
        </span>
        {seed.indexed && (
          <span className="text-[10px] text-gray-400 dark:text-gray-500 flex-shrink-0">
            {seed.chunks.toLocaleString()}
          </span>
        )}
        <span className="text-[10px] text-gray-400 dark:text-gray-600 flex-shrink-0">
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {expanded && (
        <div className="px-3 pb-3 pt-0 border-t border-gray-100 dark:border-gray-800 space-y-1.5 mt-1">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-gray-500 dark:text-gray-400">Status</span>
            <span className={`font-medium ${
              isCurrentlyIndexing ? "text-yellow-600 dark:text-yellow-400" :
              seed.indexed ? "text-green-600 dark:text-green-400" :
              "text-gray-400 dark:text-gray-500"
            }`}>
              {isCurrentlyIndexing ? "Indexing now…" : seed.indexed ? "Indexed" : "Pending"}
            </span>
          </div>
          {seed.indexed && (
            <>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-500 dark:text-gray-400">Chunks</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{seed.chunks.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-500 dark:text-gray-400">Pages scraped</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{seed.pages}</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-500 dark:text-gray-400">Last indexed</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{formatDate(seed.last_indexed)}</span>
              </div>
            </>
          )}
          {seed.url && (
            <a
              href={seed.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-[11px] text-aws-orange hover:underline mt-1"
            >
              View AWS Docs ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export default function KnowledgeBasePanel({ status, onIngestTriggered }: Props) {
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  const isIndexing = status?.ingest_running ?? false;
  const chunkCount = status?.chunk_count ?? 0;
  const progress = status?.ingest_progress;
  const allSeeds = status?.all_seeds ?? [];
  const indexedCount = status?.indexed_services ?? 0;
  const totalCount = status?.total_services ?? 0;

  const groups = groupByTier(allSeeds);
  const tiers = Object.keys(groups).map(Number).sort((a, b) => a - b);

  // Which service name is currently being indexed?
  const activeServiceName = progress?.current_service ?? null;

  function formatElapsed(secs: number | null | undefined): string {
    if (!secs) return "0s";
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  }

  const PHASE_LABEL: Record<string, string> = {
    starting: "Starting up…",
    fetching: "Scraping pages",
    chunking: "Splitting into chunks",
    upserting: "Writing to database",
    completed: "Service complete",
    skipped: "Skipped (no pages found)",
  };

  async function handleTrigger() {
    setTriggering(true);
    setTriggerMsg(null);
    try {
      const res = await kbApi.triggerIngest();
      setTriggerMsg(res.message ?? "Indexing started.");
      onIngestTriggered?.();
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
          disabled={triggering || isIndexing}
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

      {/* Live progress panel */}
      {isIndexing && progress && (
        <div className="rounded-lg border border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-950/30 p-3 space-y-2.5">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-yellow-800 dark:text-yellow-300">
              Indexing in progress
            </span>
            <span className="text-[11px] text-yellow-700 dark:text-yellow-400">
              Elapsed: {formatElapsed(progress.elapsed_seconds)}
            </span>
          </div>

          {/* Progress bar */}
          <div>
            <div className="flex items-center justify-between text-[11px] mb-1">
              <span className="text-yellow-700 dark:text-yellow-400">
                {progress.services_done}/{progress.services_total} services
              </span>
              <span className="text-yellow-700 dark:text-yellow-400">
                {progress.services_total > 0
                  ? `${Math.round((progress.services_done / progress.services_total) * 100)}%`
                  : "0%"}
              </span>
            </div>
            <div className="h-2 w-full bg-yellow-200 dark:bg-yellow-900 rounded-full overflow-hidden">
              <div
                className="h-full bg-yellow-400 dark:bg-yellow-500 rounded-full transition-all duration-500"
                style={{
                  width: progress.services_total > 0
                    ? `${Math.max(2, Math.round((progress.services_done / progress.services_total) * 100))}%`
                    : "2%",
                }}
              />
            </div>
          </div>

          {/* Current service + phase */}
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div>
              <div className="text-yellow-600 dark:text-yellow-500 mb-0.5">Current service</div>
              <div className="font-medium text-yellow-900 dark:text-yellow-200 truncate">
                {progress.current_service ?? "—"}
              </div>
            </div>
            <div>
              <div className="text-yellow-600 dark:text-yellow-500 mb-0.5">Phase</div>
              <div className="font-medium text-yellow-900 dark:text-yellow-200">
                {PHASE_LABEL[progress.phase ?? ""] ?? progress.phase ?? "—"}
              </div>
            </div>
          </div>

          {/* Phase-specific detail */}
          {progress.phase === "upserting" && progress.current_total_batches > 0 && (
            <div className="text-[11px] text-yellow-700 dark:text-yellow-400">
              Writing batch {progress.current_batch}/{progress.current_total_batches}
              {" · "}{progress.current_chunks.toLocaleString()} chunks total
            </div>
          )}
          {progress.phase === "chunking" && progress.current_pages > 0 && (
            <div className="text-[11px] text-yellow-700 dark:text-yellow-400">
              {progress.current_pages} pages scraped — splitting into chunks…
            </div>
          )}

          {/* Run totals */}
          <div className="flex gap-4 pt-1 border-t border-yellow-200 dark:border-yellow-800 text-[11px]">
            <div>
              <span className="text-yellow-600 dark:text-yellow-500">Pages this run: </span>
              <span className="font-medium text-yellow-900 dark:text-yellow-200">
                {progress.pages_this_run.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-yellow-600 dark:text-yellow-500">Chunks added: </span>
              <span className="font-medium text-yellow-900 dark:text-yellow-200">
                {progress.chunks_this_run.toLocaleString()}
              </span>
            </div>
            <div>
              <span className="text-yellow-600 dark:text-yellow-500">Done: </span>
              <span className="font-medium text-yellow-900 dark:text-yellow-200">
                {progress.services_completed.length}
              </span>
            </div>
          </div>
        </div>
      )}

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
            {totalCount > 0 ? `${indexedCount}/${totalCount}` : "—"}
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

      {/* Legend */}
      <div className="flex items-center gap-4 text-[10px] text-gray-400 dark:text-gray-500">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-400 inline-block" /> Indexed</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse inline-block" /> Indexing now</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-gray-300 dark:bg-gray-600 inline-block" /> Pending</span>
        <span className="ml-auto italic">Click any service to expand</span>
      </div>

      {/* Service tiles grouped by tier */}
      {allSeeds.length === 0 ? (
        <div className="text-center py-8 text-sm text-gray-400 dark:text-gray-500">
          {isIndexing
            ? "Loading service list…"
            : "No data yet. Click \"Run Indexer\" above to start."}
        </div>
      ) : (
        <div className="space-y-4">
          {tiers.map((tier) => {
            const meta = TIER_LABELS[tier] ?? TIER_LABELS[1];
            const tierSeeds = groups[tier];
            const tierIndexed = tierSeeds.filter((s) => s.indexed).length;
            return (
              <div key={tier}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${meta.color}`}>
                    Tier {tier} — {meta.label}
                  </span>
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">
                    {tierIndexed}/{tierSeeds.length} indexed
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-1">
                  {tierSeeds.map((s) => (
                    <ServiceTile
                      key={s.key}
                      seed={s}
                      isCurrentlyIndexing={activeServiceName === s.name}
                    />
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
