"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import type { Customer, Conversation, CustomerDocument, KnowledgeBaseStatus } from "@/lib/types";
import { customersApi, conversationsApi, documentsApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";
import CustomerHeader from "@/components/customers/CustomerHeader";
import ConversationList from "@/components/conversations/ConversationList";
import DocumentsPanel from "@/components/customers/DocumentsPanel";
import DiscoveryPanel from "@/components/discovery/DiscoveryPanel";

type TabId = "conversations" | "discovery" | "documents";

export default function CustomerPage() {
  const { customerId } = useParams<{ customerId: string }>();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabId>("conversations");

  const { data: customers = [], mutate: mutateCustomers } = useSWR<Customer[]>(
    "customers",
    () => customersApi.list(),
    { refreshInterval: 30_000 }
  );

  const { data: customer, mutate: mutateCustomer } = useSWR<Customer>(
    `customer-${customerId}`,
    () => customersApi.get(customerId)
  );

  const { data: conversations = [], mutate: mutateConversations } = useSWR<Conversation[]>(
    `conversations-${customerId}`,
    () => conversationsApi.list(customerId)
  );

  const { data: documents = [], mutate: mutateDocuments } = useSWR<CustomerDocument[]>(
    `documents-${customerId}`,
    () => documentsApi.list(customerId)
  );

  const { data: kb } = useSWR<KnowledgeBaseStatus>("kb-status", () => kbApi.status(), {
    refreshInterval: 60_000,
  });

  if (!customer) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-400 text-sm">
        Loading…
      </div>
    );
  }

  const TABS: { id: TabId; label: string }[] = [
    { id: "conversations", label: "Conversations" },
    { id: "discovery",     label: "Discovery Brief" },
    { id: "documents",     label: `Documents (${documents.length})` },
  ];

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

        {/* Tabs */}
        <div className="flex border-b border-gray-200 bg-white px-6">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-aws-orange text-aws-orange"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === "conversations" && (
            <div className="h-full overflow-y-auto px-6 py-4">
              <ConversationList
                customerId={customerId}
                conversations={conversations}
                onCreated={(conv) => {
                  mutateConversations([conv, ...conversations], false);
                  router.push(`/customers/${customerId}/conversations/${conv.id}`);
                }}
                onDeleted={(convId) => {
                  mutateConversations(
                    conversations.filter((c) => c.id !== convId),
                    false
                  );
                }}
              />
            </div>
          )}

          {activeTab === "discovery" && (
            <DiscoveryPanel
              customer={customer}
              onBriefSaved={() => mutateConversations()}
            />
          )}

          {activeTab === "documents" && (
            <div className="h-full overflow-y-auto px-6 py-4">
              <DocumentsPanel
                customerId={customerId}
                documents={documents}
                onChanged={() => mutateDocuments()}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
