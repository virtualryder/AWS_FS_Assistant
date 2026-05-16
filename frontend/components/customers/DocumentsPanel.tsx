"use client";

import { useRef, useState } from "react";
import type { CustomerDocument } from "@/lib/types";
import { documentsApi } from "@/lib/api";

interface Props {
  customerId: string;
  documents: CustomerDocument[];
  onChanged: () => void;
}

const ALLOWED_TYPES = ".pdf,.docx,.txt,.md";

export default function DocumentsPanel({ customerId, documents, onChanged }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError("");
    const errs: string[] = [];
    for (const file of Array.from(files)) {
      try {
        await documentsApi.upload(customerId, file);
      } catch (err: unknown) {
        errs.push(`${file.name}: ${(err as Error).message}`);
      }
    }
    setUploading(false);
    if (errs.length) setUploadError(errs.join("\n"));
    onChanged();
  }

  async function handleToggle(doc: CustomerDocument) {
    await documentsApi.toggle(doc.id, !doc.is_active);
    onChanged();
  }

  async function handleDelete(docId: string) {
    await documentsApi.delete(docId);
    onChanged();
  }

  return (
    <div className="px-1">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Documents</h3>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="text-xs text-aws-orange hover:text-aws-orange-dk font-semibold
            px-2 py-1 rounded hover:bg-orange-50 disabled:opacity-50"
        >
          {uploading ? "Uploading…" : "+ Upload"}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={ALLOWED_TYPES}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {uploadError && (
        <p className="text-xs text-red-600 bg-red-50 rounded px-2 py-1 mb-2 whitespace-pre-wrap">
          {uploadError}
        </p>
      )}

      {documents.length === 0 ? (
        <p className="text-xs text-gray-400 text-center py-3">
          No documents uploaded yet.
        </p>
      ) : (
        <ul className="space-y-1">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between gap-2 px-2 py-1.5
                rounded text-xs hover:bg-gray-50 group"
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <input
                  type="checkbox"
                  checked={doc.is_active}
                  onChange={() => handleToggle(doc)}
                  className="flex-shrink-0 accent-orange-500"
                  title={doc.is_active ? "Included in context" : "Excluded from context"}
                />
                <span className={`truncate ${!doc.is_active ? "text-gray-400 line-through" : "text-gray-700"}`}>
                  {doc.filename}
                </span>
                <span className="text-gray-400 flex-shrink-0">
                  {(doc.char_count / 1000).toFixed(1)}k chars
                </span>
              </div>
              <button
                onClick={() => handleDelete(doc.id)}
                className="opacity-0 group-hover:opacity-100 text-gray-300
                  hover:text-red-500 text-base leading-none flex-shrink-0"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
