"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import type {
  Customer, Project, Conversation, CustomerDocument, KnowledgeBaseStatus
} from "@/lib/types";
import { customersApi, projectsApi, conversationsApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";
import CustomerHeader from "@/components/customers/CustomerHeader";
import DocumentsPanel from "@/components/customers/DocumentsPanel";
import DiscoveryPanel from "@/components/discovery/DiscoveryPanel";
import KnowledgeBasePanel from "@/components/knowledge/KnowledgeBasePanel";
import ConversationList from "@/components/conversations/ConversationList";

type TabId = "conversations" | "discovery" | "documents" | "knowledge";

export default function ProjectPage() {
  const { customerId, projectId } = useParams<{ customerId: string; projectId: string }>();
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

  const { data: project, mutate: mutateProject } = useSWR<Project>(
    `project-${projectId}`,
    () => projectsApi.get(projectId)
  );

  const { data: conversations = [], mutate: mutateConversations } = useSWR<Conversation[]>(
    `project-conversations-${projectId}`,
    () => projectsApi.listConversations(projectId),
    { refreshInterval: 30_000 }
  );

  const { data: documents = [], mutate: mutateDocuments } = useSWR<CustomerDocument[]>(
    `project-documents-${projectId}`,
    () => projectsApi.listDocuments(projectId),
  );

  const { data: kb } = useSWR<KnowledgeBaseStatus>("kb-status", () => kbApi.status(), {
    refreshInterval: (data) => data?.ingest_running ? 5_000 : 60_000,
  });

  if (!customer || !project) {
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
    { id: "knowledge",     label: "Knowledge Base" },
  ];

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        customers={customers}
        onCustomerCreated={() => mutateCustomers()}
        kbCount={kb?.chunk_count ?? 0}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
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

        {/* Project breadcrumb + name */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-2 flex items-center gap-2">
          <Link
            href={`/customers/${customerId}`}
            className="text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ← Projects
          </Link>
          <span className="text-gray-300 dark:text-gray-700 text-xs">|</span>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
            📁 {project.name}
          </span>
          {project.description && (
            <>
              <span className="text-gray-300 dark:text-gray-700 text-xs">·</span>
              <span className="text-xs text-gray-400 dark:text-gray-500 truncate max-w-xs">
                {project.description}
              </span>
            </>
          )}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-6">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-aws-orange text-aws-orange"
                  : "border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-hidden bg-gray-50 dark:bg-gray-950">
          {activeTab === "conversations" && (
            <div className="h-full overflow-y-auto px-6 py-4">
              <ConversationList
                customerId={customerId}
                conversations={conversations}
                onCreated={(conv) => {
                  mutateConversations([conv, ...conversations], false);
                  router.push(
                    `/customers/${customerId}/conversations/${conv.id}?projectId=${projectId}`
                  );
                }}
                onDeleted={(convId) => {
                  mutateConversations(
                    conversations.filter((c) => c.id !== convId),
                    false
                  );
                }}
                projectId={projectId}
                createConversation={() => projectsApi.createConversation(projectId)}
                activeConvId={undefined}
              />
            </div>
          )}

          {activeTab === "discovery" && (
            <DiscoveryPanel
              customer={customer}
              projectName={project.name}
              onBriefSaved={() => mutateConversations()}
            />
          )}

          {activeTab === "documents" && (
            <div className="h-full overflow-y-auto px-6 py-4">
              <DocumentsPanel
                customerId={customerId}
                projectId={projectId}
                documents={documents}
                onChanged={() => mutateDocuments()}
              />
            </div>
          )}

          {activeTab === "knowledge" && (
            <div className="h-full overflow-y-auto px-6 py-4 max-w-3xl">
              <KnowledgeBasePanel status={kb} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
