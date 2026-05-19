// ── Domain types mirroring the FastAPI response shapes ───────────────────────

export type Stage =
  | "Prospect"
  | "Active Opportunity"
  | "POC / Pilot"
  | "Closed Won"
  | "Inactive";

export interface Customer {
  id: string;
  name: string;
  industry: string;
  arch_context: string;
  stage: Stage;
  created_at: string;
  updated_at: string;
  last_active_at: string | null;
}

export interface Conversation {
  id: string;
  customer_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  turn_index: number;
}

export interface CustomerDocument {
  id: string;
  customer_id: string;
  filename: string;
  char_count: number;
  is_active: boolean;
  uploaded_at: string;
}

export interface KnowledgeBaseStatus {
  chunk_count: number;
  last_updated: string | null;
  total_chunks: number;
  sources: Record<string, unknown>;
  ingest_running: boolean;
}

export interface KBSource {
  source_label: string;
  chunk_count: number;
  tier: number;
  last_indexed: string;
}

// ── SSE event types ───────────────────────────────────────────────────────────

export type SSEEventType = "status" | "token" | "done" | "error";

export interface SSEEvent {
  type: SSEEventType;
  text: string;
}

// ── UI state helpers ──────────────────────────────────────────────────────────

export interface StreamState {
  status: string;       // latest status message from the agent
  tokens: string;       // accumulated token stream (partial response)
  done: boolean;
  error: string | null;
  fullResponse: string; // complete response once done
}

export const INITIAL_STREAM_STATE: StreamState = {
  status: "",
  tokens: "",
  done: false,
  error: null,
  fullResponse: "",
};
