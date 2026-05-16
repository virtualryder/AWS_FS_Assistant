"use client";

import { useState } from "react";
import { copyToClipboard } from "@/lib/utils";

interface Props {
  text: string;
  label?: string;
  className?: string;
}

export default function CopyButton({ text, label = "Copy", className = "" }: Props) {
  const [copied, setCopied] = useState(false);

  async function handleClick() {
    const ok = await copyToClipboard(text);
    if (ok) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded
        border border-gray-300 bg-white hover:bg-gray-50 transition-colors
        ${copied ? "text-green-600 border-green-300" : "text-gray-600"}
        ${className}`}
    >
      {copied ? "✓ Copied" : `📋 ${label}`}
    </button>
  );
}
