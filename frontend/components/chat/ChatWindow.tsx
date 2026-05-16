"use client";

import { useEffect, useRef, useState } from "react";
import type { Message } from "@/lib/types";
import { useChatStream } from "@/hooks/useChatStream";
import MarkdownRenderer from "@/components/common/MarkdownRenderer";
import StatusTicker from "@/components/common/StatusTicker";
import CopyButton from "@/components/common/CopyButton";
import { downloadText } from "@/lib/utils";

interface Props {
  convId: string;
  customerId: string;
  customerContext: string;
  initialMessages: Message[];
  onNewResponse?: (response: string) => void;
}

export default function ChatWindow({
  convId,
  customerId,
  customerContext,
  initialMessages,
  onNewResponse,
}: Props) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { state, sendMessage, cancel } = useChatStream();

  // Scroll to bottom on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, state.tokens, state.status]);

  async function handleSend() {
    const msg = input.trim();
    if (!msg || state.done === false && state.status !== "") return;

    const userMsg: Message = {
      role: "user",
      content: msg,
      turn_index: messages.length * 2,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    await sendMessage(convId, msg, customerContext);
  }

  // When streaming finishes, commit to messages list
  useEffect(() => {
    if (state.done && state.fullResponse) {
      const assistantMsg: Message = {
        role: "assistant",
        content: state.fullResponse,
        turn_index: messages.length * 2 + 1,
      };
      setMessages((prev) => {
        // Avoid duplicates if effect fires twice
        if (prev.at(-1)?.role === "assistant" && prev.at(-1)?.content === state.fullResponse) {
          return prev;
        }
        return [...prev, assistantMsg];
      });
      onNewResponse?.(state.fullResponse);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.done, state.fullResponse]);

  const isStreaming = !state.done && state.status !== "";

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <div className="text-4xl mb-4">🏦</div>
            <h2 className="text-lg font-semibold text-gray-700 mb-2">
              AWS Financial Services Assistant
            </h2>
            <p className="text-sm text-gray-500 max-w-md">
              Ask about AWS architecture design, compliance requirements (GLBA, PCI DSS,
              SOX, FFIEC), or GenAI/ML opportunities. Both agents will analyze your question.
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-3xl w-full ${
                m.role === "user" ? "chat-user px-4 py-3" : "chat-assistant px-5 py-4"
              }`}
            >
              {m.role === "user" ? (
                <p className="text-sm text-gray-800 whitespace-pre-wrap">{m.content}</p>
              ) : (
                <>
                  <MarkdownRenderer content={m.content} />
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
                    <CopyButton text={m.content} label="Copy response" />
                    <button
                      onClick={() => downloadText("response.md", m.content)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium
                        rounded border border-gray-300 bg-white hover:bg-gray-50 text-gray-600"
                    >
                      ⬇ Download
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        ))}

        {/* Streaming state */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="chat-assistant max-w-3xl w-full px-5 py-4 space-y-3">
              <StatusTicker message={state.status} visible={!!state.status && !state.tokens} />
              {state.tokens && (
                <MarkdownRenderer content={state.tokens} />
              )}
            </div>
          </div>
        )}

        {state.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            Error: {state.error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        {isStreaming && (
          <div className="mb-2">
            <StatusTicker message={state.status} visible />
          </div>
        )}
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about AWS architecture, compliance requirements, GenAI/ML opportunities…"
            rows={2}
            disabled={isStreaming}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm
              focus:outline-none focus:ring-2 focus:ring-aws-orange resize-none
              disabled:opacity-60 disabled:cursor-not-allowed"
          />
          {isStreaming ? (
            <button
              onClick={cancel}
              className="px-5 py-3 text-sm font-semibold text-white bg-red-500
                hover:bg-red-600 rounded-xl transition-colors"
            >
              Stop
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="px-5 py-3 text-sm font-semibold text-white bg-aws-orange
                hover:bg-aws-orange-dk rounded-xl disabled:opacity-50 transition-colors"
            >
              Send
            </button>
          )}
        </div>
        <p className="text-xs text-gray-400 mt-1.5">
          Shift+Enter for new line · Enter to send
        </p>
      </div>
    </div>
  );
}
