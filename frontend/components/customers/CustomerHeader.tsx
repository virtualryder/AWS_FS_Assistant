"use client";

import { useState } from "react";
import type { Customer } from "@/lib/types";
import { customersApi } from "@/lib/api";
import { FS_ENTITY_TYPES, STAGE_OPTIONS } from "@/lib/constants";
import StageBadge from "@/components/common/StageBadge";

interface Props {
  customer: Customer;
  onUpdated: (c: Customer) => void;
  onDeleted: () => void;
}

export default function CustomerHeader({ customer, onUpdated, onDeleted }: Props) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    name: customer.name,
    industry: customer.industry,
    arch_context: customer.arch_context,
    stage: customer.stage,
  });
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await customersApi.update(customer.id, form);
      onUpdated(updated);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    await customersApi.delete(customer.id);
    onDeleted();
  }

  if (editing) {
    return (
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm
                focus:outline-none focus:ring-2 focus:ring-aws-orange"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Entity Type</label>
            <select
              value={form.industry}
              onChange={(e) => setForm({ ...form, industry: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm
                focus:outline-none focus:ring-2 focus:ring-aws-orange"
            >
              <option value="">Select…</option>
              {FS_ENTITY_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mb-3">
          <label className="block text-xs font-medium text-gray-600 mb-1">Stage</label>
          <select
            value={form.stage}
            onChange={(e) => setForm({ ...form, stage: e.target.value as Customer["stage"] })}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm
              focus:outline-none focus:ring-2 focus:ring-aws-orange"
          >
            {STAGE_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div className="mb-3">
          <label className="block text-xs font-medium text-gray-600 mb-1">Architecture Context</label>
          <textarea
            value={form.arch_context}
            onChange={(e) => setForm({ ...form, arch_context: e.target.value })}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm
              focus:outline-none focus:ring-2 focus:ring-aws-orange resize-none"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-1.5 text-sm font-semibold text-white bg-aws-orange
              hover:bg-aws-orange-dk rounded-lg disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save"}
          </button>
          <button
            onClick={() => setEditing(false)}
            className="px-4 py-1.5 text-sm text-gray-600 hover:text-gray-900"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-start justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-gray-900">{customer.name}</h1>
          <StageBadge stage={customer.stage} />
        </div>
        {customer.industry && (
          <div className="text-sm text-gray-500 mt-0.5">{customer.industry}</div>
        )}
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => setEditing(true)}
          className="text-xs text-gray-500 hover:text-gray-700 px-3 py-1.5
            border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Edit
        </button>
        {confirmDelete ? (
          <div className="flex items-center gap-1">
            <span className="text-xs text-red-600">Delete customer?</span>
            <button
              onClick={handleDelete}
              className="text-xs text-white bg-red-600 hover:bg-red-700
                px-2 py-1 rounded"
            >
              Yes
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="text-xs text-gray-600 hover:text-gray-900 px-2 py-1"
            >
              No
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="text-xs text-red-500 hover:text-red-700 px-3 py-1.5
              border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
