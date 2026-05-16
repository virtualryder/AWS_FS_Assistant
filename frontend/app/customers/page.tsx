"use client";

import { useState } from "react";
import useSWR from "swr";
import type { Customer, KnowledgeBaseStatus } from "@/lib/types";
import { customersApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";

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
      <main className="flex-1 flex flex-col items-center justify-center bg-gray-50">
        <div className="text-center max-w-lg px-6">
          <div className="text-6xl mb-6">🏦</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            AWS Financial Services Assistant
          </h1>
          <p className="text-gray-500 mb-6">
            Presidio AWS Financial Services Practice — dual AI agents providing
            compliance-validated architecture design for GLBA, PCI DSS, SOX,
            FFIEC, and NIST AI RMF.
          </p>
          <div className="grid grid-cols-2 gap-3 text-sm text-left">
            {[
              { icon: "🏗️", label: "AWS Architect Agent", desc: "Compliance-validated architecture with GLBA, PCI DSS v4.0.1, SOX, FFIEC" },
              { icon: "🤖", label: "GenAI/ML Agent", desc: "Bedrock, SageMaker, AgentCore with NIST AI RMF governance" },
              { icon: "🎯", label: "Discovery Briefs", desc: "Pre-call research with regulatory risk tables and 20 discovery questions" },
              { icon: "📄", label: "Document Context", desc: "Upload customer docs (PDF, DOCX) to ground responses" },
            ].map((item) => (
              <div
                key={item.label}
                className="bg-white rounded-xl border border-gray-200 p-4"
              >
                <div className="text-2xl mb-2">{item.icon}</div>
                <div className="font-semibold text-gray-800 mb-1">{item.label}</div>
                <div className="text-gray-500 text-xs">{item.desc}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-6">
            Select or create a customer in the sidebar to get started.
          </p>
        </div>
      </main>
    </div>
  );
}
