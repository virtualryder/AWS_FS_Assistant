"use client";

import { useState } from "react";
import Link from "next/link";
import type { Customer } from "@/lib/types";
import { STAGE_EMOJI } from "@/lib/constants";
import { timeAgo } from "@/lib/utils";
import NewCustomerModal from "./NewCustomerModal";

interface Props {
  customers: Customer[];
  onCreated: () => void;
  activePath: string;
}

export default function CustomerList({ customers, onCreated, activePath }: Props) {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="py-2">
      {/* Section header */}
      <div className="flex items-center justify-between px-4 py-1.5">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Customers
        </span>
        <button
          onClick={() => setShowModal(true)}
          className="text-xs text-aws-orange hover:text-aws-orange-dk font-semibold
            w-5 h-5 flex items-center justify-center rounded hover:bg-orange-50"
          title="New customer"
        >
          +
        </button>
      </div>

      {/* List */}
      {customers.length === 0 ? (
        <div className="px-4 py-6 text-center text-xs text-gray-400">
          No customers yet.
          <button
            onClick={() => setShowModal(true)}
            className="block mx-auto mt-2 text-aws-orange hover:underline"
          >
            Add your first customer
          </button>
        </div>
      ) : (
        <ul className="space-y-0.5">
          {customers.map((c) => {
            const isActive = activePath.startsWith(`/customers/${c.id}`);
            const lastActive = c.last_active_at ?? c.updated_at;
            return (
              <li key={c.id}>
                <Link
                  href={`/customers/${c.id}`}
                  className={`flex flex-col px-4 py-2.5 text-sm transition-colors
                    ${isActive
                      ? "bg-orange-50 border-r-2 border-aws-orange"
                      : "hover:bg-gray-50"
                    }`}
                >
                  <span className="font-medium text-gray-900 truncate">
                    {STAGE_EMOJI[c.stage]} {c.name}
                  </span>
                  <span className="text-xs text-gray-400 mt-0.5 truncate">
                    {c.industry || c.stage}
                    {lastActive ? ` · ${timeAgo(lastActive)}` : ""}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}

      {showModal && (
        <NewCustomerModal
          onClose={() => setShowModal(false)}
          onCreated={() => { onCreated(); setShowModal(false); }}
        />
      )}
    </div>
  );
}
