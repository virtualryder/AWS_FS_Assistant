"use client";

import { useState } from "react";
import useSWR from "swr";
import type { Customer, KnowledgeBaseStatus } from "@/lib/types";
import { customersApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";
import KnowledgeBasePanel from "@/components/knowledge/KnowledgeBasePanel";

const fetchCustomers = () => customersApi.list();
const fetchKb = () => kbApi.status();

export default function CustomersPage() {
  const { data: customers = [], mutate: mutateCustomers } = useSWR<Customer[]>(
    "customers",
    fetchCustomers,
    { refreshInterval: 30_000 }
  );

  const { data: kb } = useSWR<KnowledgeBaseStatus>("kb-status", fetchKb, {
    refreshInterval: 60_000,
  });

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        customers={customers}
        onCustomerCreated={() => mutateCustomers()}
        kbCount={kb?.chunk_count ?? 0}
      />

      {/* Main area — no customer selected */}
      <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-950">
        <div className="max-w-4xl mx-auto px-8 py-10">
          {/* Hero */}
          <div className="text-center mb-8">
            <div className="text-5xl mb-4">🏦</div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              AWS Financial Services Assistant
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm max-w-xl mx-auto">
              AWS Financial Services Assistant — dual AI agents providing
              compliance-validated architecture design for GLBA, PCI DSS, SOX,
              FFIEC, and NIST AI RMF.
            </p>
          </div>

          {/* Capability cards */}
          <div className="grid grid-cols-2 gap-3 mb-8 text-sm text-left">
            {[
              { icon: "🏗️", label: "AWS Architect Agent", desc: "Compliance-validated architecture with GLBA, PCI DSS v4.0.1, SOX, FFIEC" },
              { icon: "🤖", label: "GenAI/ML Agent", desc: "Bedrock, SageMaker, AgentCore with NIST AI RMF governance" },
              { icon: "🎯", label: "Discovery Briefs", desc: "Pre-call research with regulatory risk tables and 20 discovery questions" },
              { icon: "📄", label: "Document Context", desc: "Upload customer docs (PDF, DOCX) to ground responses" },
            ].map((item) => (
              <div
                key={item.label}
                className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
              >
                <div className="text-2xl mb-2">{item.icon}</div>
                <div className="font-semibold text-gray-800 dark:text-gray-200 mb-1">{item.label}</div>
                <div className="text-gray-500 dark:text-gray-400 text-xs">{item.desc}</div>
              </div>
            ))}
          </div>

          {/* Knowledge base panel */}
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <KnowledgeBasePanel status={kb} />
          </div>

          <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-6">
            Select or create a customer in the sidebar to get started.
          </p>
        </div>
      </main>
    </div>
  );
}
