"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";
import { UserButton } from "@clerk/nextjs";
import { COMPLIANCE_REFS, KB_CATALOG } from "@/lib/constants";
import type { Customer } from "@/lib/types";
import CustomerList from "@/components/customers/CustomerList";
import { useTheme } from "@/lib/theme";
import GeneralChatModal from "@/components/general/GeneralChatModal";

interface Props {
  customers: Customer[];
  onCustomerCreated: () => void;
  kbCount: number;
}

export default function Sidebar({ customers, onCustomerCreated, kbCount }: Props) {
  const [complianceOpen, setComplianceOpen] = useState(false);
  const [kbOpen, setKbOpen] = useState(false);
  const [claudeChatOpen, setClaudeChatOpen] = useState(false);
  const pathname = usePathname();
  const { theme, toggle } = useTheme();

  return (
    <>
    <aside className="sidebar flex flex-col h-screen bg-gray-100 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">🏦</span>
          <div>
            <div className="text-sm font-bold text-gray-900 dark:text-gray-100 leading-tight">
              AWS FinServ Assistant
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Compliance-Validated Architecture</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded transition-colors"
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>
          <UserButton />
        </div>
      </div>

      {/* Customer list */}
      <div className="flex-1 overflow-y-auto">
        <CustomerList
          customers={customers}
          onCreated={onCustomerCreated}
          activePath={pathname}
        />
      </div>

      {/* Chat with Claude button */}
      <div className="px-3 py-2 border-t border-gray-100 dark:border-gray-800">
        <button
          onClick={() => setClaudeChatOpen(true)}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium
            bg-gray-50 dark:bg-gray-800 hover:bg-aws-orange/10 dark:hover:bg-aws-orange/10
            text-gray-700 dark:text-gray-300 hover:text-aws-orange dark:hover:text-aws-orange
            border border-gray-200 dark:border-gray-700 hover:border-aws-orange/40
            transition-colors"
        >
          <span className="text-base">✦</span>
          <span>Chat with Claude</span>
        </button>
      </div>

      {/* Knowledge Base reference */}
      <div className="border-t border-gray-100 dark:border-gray-800">
        <button
          onClick={() => setKbOpen(!kbOpen)}
          className="w-full flex items-center justify-between px-4 py-2.5
            text-xs font-semibold text-gray-500 dark:text-gray-400
            hover:text-gray-700 dark:hover:text-gray-200
            hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <span>📚 Knowledge Base</span>
          <span className="text-gray-400 dark:text-gray-600">{kbOpen ? "▲" : "▼"}</span>
        </button>

        {kbOpen && (
          <div className="px-4 pb-3 space-y-3 max-h-72 overflow-y-auto">
            <p className="text-[10px] text-gray-400 dark:text-gray-500">
              {kbCount > 0 ? `${kbCount.toLocaleString()} chunks indexed · Click any doc to open it` : "No docs indexed yet"}
            </p>
            {/* Group catalog by category */}
            {Object.entries(
              KB_CATALOG.reduce<Record<string, typeof KB_CATALOG>>((acc, doc) => {
                if (!acc[doc.category]) acc[doc.category] = [];
                acc[doc.category].push(doc);
                return acc;
              }, {})
            ).map(([cat, docs]) => (
              <div key={cat}>
                <div className="text-[9px] font-bold uppercase tracking-wider text-gray-400 dark:text-gray-600 mb-1">
                  {cat}
                </div>
                <div className="space-y-0.5">
                  {docs.map((doc) => (
                    <a
                      key={doc.key}
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 py-0.5 text-[11px] text-gray-600 dark:text-gray-400
                        hover:text-aws-orange transition-colors group"
                    >
                      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                        kbCount > 0 ? "bg-green-400" : "bg-gray-300 dark:bg-gray-600"
                      }`} />
                      <span className="truncate group-hover:underline">{doc.name}</span>
                      <span className="text-gray-300 dark:text-gray-700 text-[9px] flex-shrink-0">↗</span>
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Compliance reference */}
      <div className="border-t border-gray-100 dark:border-gray-800">
        <button
          onClick={() => setComplianceOpen(!complianceOpen)}
          className="w-full flex items-center justify-between px-4 py-2.5
            text-xs font-semibold text-gray-500 dark:text-gray-400
            hover:text-gray-700 dark:hover:text-gray-200
            hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <span>⚖️ Compliance Reference</span>
          <span className="text-gray-400 dark:text-gray-600">{complianceOpen ? "▲" : "▼"}</span>
        </button>

        {complianceOpen && (
          <div className="px-4 pb-3 space-y-2 max-h-72 overflow-y-auto">
            {COMPLIANCE_REFS.map((ref) => (
              <a
                key={ref.name}
                href={ref.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block accent-border pl-2 py-1 text-xs hover:bg-gray-50 dark:hover:bg-gray-800 rounded-r transition-colors group"
              >
                <div className="font-semibold text-gray-800 dark:text-gray-200 group-hover:text-aws-orange transition-colors">
                  {ref.name} ↗
                </div>
                <div className="text-gray-500 dark:text-gray-400">{ref.year}</div>
                <div className="text-gray-500 dark:text-gray-400 mt-0.5">{ref.note}</div>
              </a>
            ))}
          </div>
        )}
      </div>
    </aside>

    {claudeChatOpen && (
      <GeneralChatModal onClose={() => setClaudeChatOpen(false)} />
    )}
    </>
  );
}
