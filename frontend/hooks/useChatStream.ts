"use client";

import { useCallback } from "react";
import { useSSEStream } from "./useSSEStream";

/**
 * Chat-specific wrapper around useSSEStream.
 * Posts to /api/conversations/{convId}/chat and streams the response.
 */
export function useChatStream() {
  const { state, stream, cancel, reset } = useSSEStream();

  const sendMessage = useCallback(
    (convId: string, userMessage: string, customerContext: string = "") => {
      return stream(`/api/conversations/${convId}/chat`, {
        user_message: userMessage,
        customer_context: customerContext,
      });
    },
    [stream]
  );

  return { state, sendMessage, cancel, reset };
}
