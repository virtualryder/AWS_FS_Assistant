"use client";

import { useCallback, useRef, useState } from "react";
import type { SSEEvent, StreamState } from "@/lib/types";
import { INITIAL_STREAM_STATE } from "@/lib/types";

/**
 * Generic SSE stream hook.
 *
 * Opens a POST → EventSource connection by first making the POST request and
 * then reading the response body as a ReadableStream of SSE data.
 *
 * (Native EventSource only supports GET; we use fetch + ReadableStream to
 * support POST endpoints with a JSON body.)
 */
export function useSSEStream() {
  const [state, setState] = useState<StreamState>(INITIAL_STREAM_STATE);
  const abortRef = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (url: string, body: Record<string, unknown>) => {
      // Cancel any in-flight request
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setState({ ...INITIAL_STREAM_STATE });

      try {
        const res = await fetch(url, {
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
          setState((s) => ({ ...s, error: `${res.status}: ${detail}`, done: true }));
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) {
          setState((s) => ({ ...s, error: "No response body", done: true }));
          return;
        }

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // SSE lines look like: "data: {...}\n\n"
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

            if (event.type === "status") {
              setState((s) => ({ ...s, status: event.text }));
            } else if (event.type === "token") {
              setState((s) => ({ ...s, tokens: s.tokens + event.text }));
            } else if (event.type === "done") {
              setState((s) => ({
                ...s,
                fullResponse: event.text,
                tokens: event.text,
                done: true,
                status: "",
              }));
              return;
            } else if (event.type === "error") {
              setState((s) => ({
                ...s,
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
          error: (err as Error)?.message ?? "Unknown error",
          done: true,
        }));
      }
    },
    []
  );

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setState((s) => ({ ...s, done: true }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(INITIAL_STREAM_STATE);
  }, []);

  return { state, stream, cancel, reset };
}
