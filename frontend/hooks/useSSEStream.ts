"use client";

import { useCallback, useRef, useState } from "react";
import type { SSEEvent, StreamState } from "@/lib/types";
import { INITIAL_STREAM_STATE } from "@/lib/types";

/**
 * Generic SSE stream hook.
 *
 * For SSE endpoints we bypass the Next.js rewrite proxy and call the API
 * directly. Railway's frontend service has a short idle timeout; a 9-minute
 * streaming response must travel directly from the API to the browser.
 *
 * In production set NEXT_PUBLIC_API_URL=https://your-api.up.railway.app in
 * the Railway frontend service env vars so the bundle picks it up at build
 * time. In local dev the var is unset and the relative /api/... path falls
 * back to the Next.js rewrite proxy (which is fine for localhost).
 */

// Strip trailing slash so paths like "/api/..." never produce a double slash
const SSE_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

export function useSSEStream() {
  const [state, setState] = useState<StreamState>(INITIAL_STREAM_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (path: string, body: Record<string, unknown>) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      // Show connecting spinner immediately — before the first SSE byte
      setState({ ...INITIAL_STREAM_STATE, connecting: true });

      try {
        const res = await fetch(`${SSE_BASE}${path}`, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        if (!res.ok) {
          let detail = res.statusText;
          try {
            const errBody = await res.json();
            detail = errBody.detail ?? detail;
          } catch {
            // ignore
          }
          setState((s) => ({ ...s, connecting: false, error: `${res.status}: ${detail}`, done: true }));
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) {
          setState((s) => ({ ...s, connecting: false, error: "No response body", done: true }));
          return;
        }

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // First byte received — clear the connecting flag
          setState((s) => s.connecting ? { ...s, connecting: false } : s);

          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const raw = line.slice(6).trim();
            if (!raw) continue;

            let event: SSEEvent;
            try {
              event = JSON.parse(raw);
            } catch {
              continue;
            }

            if (event.type === "heartbeat") {
              // Keep-alive event — ignore, exists only to prevent Railway proxy timeout
              continue;
            } else if (event.type === "status") {
              setState((s) => ({ ...s, status: event.text }));
            } else if (event.type === "token") {
              setState((s) => ({ ...s, tokens: s.tokens + event.text }));
            } else if (event.type === "done") {
              setState((s) => ({
                ...s,
                fullResponse: event.text,
                tokens: event.text,
                connecting: false,
                done: true,
                status: "",
              }));
              return;
            } else if (event.type === "error") {
              setState((s) => ({
                ...s,
                connecting: false,
                error: event.text,
                done: true,
              }));
              return;
            }
          }
        }
      } catch (err: unknown) {
        if ((err as Error)?.name === "AbortError") return;
        setState((s) => ({
          ...s,
          connecting: false,
          error: (err as Error)?.message ?? "Unknown error",
          done: true,
        }));
      }
    },
    []
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setState((s) => ({ ...s, connecting: false, done: true }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(INITIAL_STREAM_STATE);
  }, []);

  return { state, stream, cancel, reset };
}
