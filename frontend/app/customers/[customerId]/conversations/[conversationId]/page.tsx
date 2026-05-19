"use client";

import { useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import type { Customer, Conversation, Message, CustomerDocument, KnowledgeBaseStatus } from "@/lib/types";
import { customersApi, conversationsApi, documentsApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";
import CustomerHeader from "@/components/customers/CustomerHeader";
import ChatWindow from "@/components/chat/ChatWindow";

export default function ConversationPage() {
  const { customerId, conversationId } = useParams<{
    customerId: string;
    conversationId: string;
  }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = searchParams.get("projectId");
  const backHref = projectId
    ? `/customers/${customerId}/projects/${projectId}`
    : `/customers/${customerId}`;
  const [confirmClear, setConfirmClear] = useState(false);

  // ── Data fetching ─────────────────────────────────────────────────────────
  const { data: customers = [], mutate: mutateCustomers } = useSWR<Customer[]>(
    "customers",
    () => customersApi.list(),
    { refreshInterval: 30_000 }
  );

  const { data: customer, mutate: mutateCustomer } = useSWR<Customer>(
    `customer-${customerId}`,
    () => customersApi.get(customerId)
  );

  const { data: conversation, mutate: mutateConversation } = useSWR<Conversation>(
    `conversation-${conversationId}`,
    () => conversationsApi.get(conversationId)
  );

  const { data: messages = [], mutate: mutateMessages } = useSWR<Message[]>(
    `messages-${conversationId}`,
    () => conversationsApi.getMessages(conversationId)
  );

  const { data: documents = [] } = useSWR<CustomerDocument[]>(
    `documents-${customerId}`,
    () => documentsApi.list(customerId)
  );

  const { data: kb } = useSWR<KnowledgeBaseStatus>("kb-status", () => kbApi.status(), {
    refreshInterval: 60_000,
  });

  // ── Derived ───────────────────────────────────────────────────────────────

  const customerContext = buildCustomerContext(customer, documents);

  // ── Handlers ──────────────────────────────────────────────────────────────

  async function handleClear() {
    await conversationsApi.clearMessages(conversationId);
    mutateMessages([], false);
    mutateConversation();
    setConfirmClear(false);
  }

  if (!customer || !conversation) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-400 text-sm">
        Loading…
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        customers={customers}
        onCustomerCreated={() => mutateCustomers()}
        kbCount={kb?.chunk_count ?? 0}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Customer header */}
        <CustomerHeader
          customer={customer}
          onUpdated={(updated) => {
            mutateCustomer(updated, false);
            mutateCustomers();
          }}
          onDeleted={() => {
            mutateCustomers();
            router.push("/customers");
          }}
        />

        {/* Conversation sub-header */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-2 min-w-0">
            <Link
              href={backHref}
              className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 flex-shrink-0"
            >
              ← Back
            </Link>
            <span className="text-gray-300 dark:text-gray-700">|</span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
              {conversation.title}
            </span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {documents.length > 0 && (
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {documents.filter((d) => d.is_active).length}/{documents.length} docs
              </span>
            )}
            {confirmClear ? (
              <div className="flex items-center gap-1">
                <span className="text-xs text-red-600 dark:text-red-400">Clear history?</span>
                <button
                  onClick={handleClear}
                  className="text-xs text-white bg-red-500 hover:bg-red-600 px-2 py-0.5 rounded"
                >
                  Yes
                </button>
                <button
                  onClick={() => setConfirmClear(false)}
                  className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-1.5 py-0.5"
                >
                  No
                </button>
              </div>
            ) : (
              <button
                onClick={() => setConfirmClear(true)}
                className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 px-2 py-1
                  border border-gray-200 dark:border-gray-700 rounded
                  hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Chat */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow
            convId={conversationId}
            customerId={customerId}
            customerContext={customerContext}
            initialMessages={messages}
            onNewResponse={() => {
              // Refresh conversation title after first response
              mutateConversation();
              mutateCustomers(); // update last_active_at in sidebar
            }}
          />
        </div>
      </div>
    </div>
  );
}


// ── Helpers ───────────────────────────────────────────────────────────────────

function buildCustomerContext(
  customer: Customer | undefined,
  documents: CustomerDocument[]
): string {
  if (!customer) return "";
  const parts: string[] = [];
  if (customer.arch_context?.trim()) {
    parts.push(customer.arch_context.trim());
  }
  // Documents' text is not returned by the list endpoint (too large);
  // the Python agent has access to them via the customer context field.
  // (Document text is passed via arch_context on the customer object.)
  return parts.join("\n\n");
}
