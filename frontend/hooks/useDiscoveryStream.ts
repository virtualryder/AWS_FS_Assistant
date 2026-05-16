"use client";

import { useCallback } from "react";
import { useSSEStream } from "./useSSEStream";

/**
 * Discovery brief wrapper around useSSEStream.
 * Posts to /api/customers/{customerId}/discovery and streams the brief.
 */
export function useDiscoveryStream() {
  const { state, stream, cancel, reset } = useSSEStream();

  const generateBrief = useCallback(
    (
      customerId: string,
      opts: { website?: string; notes?: string; save_as_conversation?: boolean } = {}
    ) => {
      return stream(`/api/customers/${customerId}/discovery`, {
        website: opts.website ?? "",
        notes: opts.notes ?? "",
        save_as_conversation: opts.save_as_conversation ?? true,
      });
    },
    [stream]
  );

  return { state, generateBrief, cancel, reset };
}
