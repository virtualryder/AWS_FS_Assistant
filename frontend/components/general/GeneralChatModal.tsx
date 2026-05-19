"use client";

import { useEffect, useRef, useState } from "react";
import { useSSEStream } from "@/hooks/useSSEStream";
import { INITIAL_STREAM_STATE } from "@/lib/types";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import StatusTicker from "@/components/common/StatusTicker";
import CopyButton from "@/components/common/CopyButton";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  onClose: () => void;
}

export default function GeneralChatModal({ onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { state, stream, cancel, reset } = useSSEStream();

  const isStreaming = !state.done && (state.connecting || state.tokens !== "");

  // Scroll to bottom on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, state.tokens]);

  // When streaming finishes, commit assistant message
  useEffect(() => {
    if (state.done && state.fullResponse) {
      setMessages((prev) => {
        if (prev.at(-1)?.role === "assistant" && prev.at(-1)?.content === state.fullResponse) {
          return prev;
        }
        return [...prev, { role: "assistant", content: state.fullResponse }];
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.done, state.fullResponse]);

  async function handleSend() {
    const msg = input.trim();
    if (!msg || isStreaming) return;

    const updatedMessages: Message[] = [...messages, { role: "user", content: msg }];
    setMessages(updatedMessages);
    setInput("");
    reset();

    await stream("/api/general-chat", {
      messages: updatedMessages.map((m) => ({ role: m.role, content: m.content })),
    });
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  // Close on Escape
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50 p-4">
      <div
        className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700
          w-full max-w-2xl flex flex-col"
        style={{ height: "min(80vh, 700px)" }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 dark:border-gray-800 flex-shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="text-xl">✦</span>
            <div>
              <div className="text-sm font-semibold text-gray-900 dark:text-gray-100 leading-tight">
                Chat with Claude
              </div>
              <div className="text-[10px] text-gray-400 dark:text-gray-500">
                General knowledge · claude-sonnet-4-6
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-xl leading-none p-1"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.length === 0 && !isStreaming && (
            <div className="flex flex-col items-center justify-center h-full text-center py-10">
              <span className="text-4xl mb-3">✦</span>
              <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                Ask Claude anything — general knowledge, coding, strategy, analysis,
                or anything else. No agents, no frameworks, just Claude.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] ${m.role === "user" ? "chat-user px-4 py-2.5" : "chat-assistant px-4 py-3"}`}>
                {m.role === "user" ? (
                  <p className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{m.content}</p>
                ) : (
                  <>
                    <MarkdownRenderer content={m.content} />
                    <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
                      <CopyButton text={m.content} label="Copy" />
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}

          {/* Streaming */}
          {isStreaming && (
            <div className="flex justify-start">
              <div className="chat-assistant max-w-[85%] px-4 py-3 space-y-2">
                {!state.tokens && (
                  <StatusTicker message="⏳  Claude is thinking…" visible />
                )}
                {state.tokens && <MarkdownRenderer content={state.tokens} />}
              </div>
            </div>
          )}

          {state.error && (
            <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3 text-sm text-red-700 dark:text-red-400">
              Error: {state.error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 dark:border-gray-800 px-4 py-3 flex-shrink-0">
          <div className="flex gap-2 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Claude anything…"
              rows={2}
              disabled={isStreaming}
              className="flex-1 border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-2.5 text-sm
                bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
                placeholder-gray-400 dark:placeholder-gray-500
                focus:outline-none focus:ring-2 focus:ring-aws-orange resize-none
                disabled:opacity-60 disabled:cursor-not-allowed"
            />
            {isStreaming ? (
              <button
                onClick={cancel}
                className="px-4 py-2.5 text-sm font-semibold text-white bg-red-500 hover:bg-red-600 rounded-xl transition-colors"
              >
                Stop
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                className="px-4 py-2.5 text-sm font-semibold text-white bg-aws-orange
                  hover:bg-aws-orange-dk rounded-xl disabled:opacity-50 transition-colors"
              >
                Send
              </button>
            )}
          </div>
          <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-1.5">
            Shift+Enter for new line · Enter to send · Esc to close
          </p>
        </div>
      </div>
    </div>
  );
}
