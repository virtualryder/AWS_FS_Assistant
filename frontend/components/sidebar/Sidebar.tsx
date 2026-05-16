"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { COMPLIANCE_REFS } from "@/lib/constants";
import type { Customer } from "@/lib/types";
import CustomerList from "@/components/customers/CustomerList";

interface Props {
  customers: Customer[];
  onCustomerCreated: () => void;
  kbCount: number;
}

export default function Sidebar({ customers, onCustomerCreated, kbCount }: Props) {
  const [complianceOpen, setComplianceOpen] = useState(false);
  const pathname = usePathname();

  return (
    <aside className="sidebar flex flex-col h-screen bg-white border-r border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-xl">🏦</span>
          <div>
            <div className="text-sm font-bold text-gray-900 leading-tight">
              AWS Financial Services
            </div>
            <div className="text-xs text-gray-500">Presidio Practice</div>
          </div>
        </div>
      </div>

      {/* Knowledge base chip */}
      <div className="px-4 py-2 border-b border-gray-100">
        <Link href="/" className="flex items-center justify-between group">
          <span className="text-xs text-gray-500">Knowledge Base</span>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            kbCount > 0
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}>
            {kbCount > 0 ? `${kbCount.toLocaleString()} chunks` : "Empty"}
          </span>
        </Link>
      </div>

      {/* Customer list */}
      <div className="flex-1 overflow-y-auto">
        <CustomerList
          customers={customers}
          onCreated={onCustomerCreated}
          activePath={pathname}
        />
      </div>

      {/* Compliance reference */}
      <div className="border-t border-gray-100">
        <button
          onClick={() => setComplianceOpen(!complianceOpen)}
          className="w-full flex items-center justify-between px-4 py-2.5
            text-xs font-semibold text-gray-500 hover:text-gray-700 hover:bg-gray-50
            transition-colors"
        >
          <span>⚖️ Compliance Reference</span>
          <span className="text-gray-400">{complianceOpen ? "▲" : "▼"}</span>
        </button>

        {complianceOpen && (
          <div className="px-4 pb-3 space-y-2 max-h-72 overflow-y-auto">
            {COMPLIANCE_REFS.map((ref) => (
              <div
                key={ref.name}
                className="accent-border pl-2 py-1 text-xs"
              >
                <div className="font-semibold text-gray-800">{ref.name}</div>
                <div className="text-gray-500">{ref.year}</div>
                <div className="text-gray-500 mt-0.5">{ref.note}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
