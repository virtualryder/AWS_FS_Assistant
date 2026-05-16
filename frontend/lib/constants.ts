import type { Stage } from "./types";

// ── Stage UI config ───────────────────────────────────────────────────────────

export const STAGE_OPTIONS: Stage[] = [
  "Prospect",
  "Active Opportunity",
  "POC / Pilot",
  "Closed Won",
  "Inactive",
];

export const STAGE_COLOR: Record<Stage, string> = {
  Prospect:            "stage-prospect",
  "Active Opportunity":"stage-active",
  "POC / Pilot":       "stage-poc",
  "Closed Won":        "stage-closed",
  Inactive:            "stage-inactive",
};

export const STAGE_EMOJI: Record<Stage, string> = {
  Prospect:            "⬜",
  "Active Opportunity":"🔵",
  "POC / Pilot":       "🟠",
  "Closed Won":        "🟢",
  Inactive:            "⚫",
};

// ── Financial services entity types ──────────────────────────────────────────

export const FS_ENTITY_TYPES = [
  "Regional Bank",
  "National Bank",
  "Credit Union",
  "Community Bank",
  "Investment Bank / Capital Markets",
  "Insurance Company",
  "Payment Processor / Fintech",
  "Mortgage Company",
  "Asset Manager / Wealth Management",
  "Securities Firm / Broker-Dealer",
  "Other Financial Services",
] as const;

// ── Compliance reference (sidebar) ────────────────────────────────────────────

export const COMPLIANCE_REFS = [
  {
    name: "GLBA / FTC Safeguards Rule",
    year: "2023",
    note: "MFA for all users, AES-256, 30-day FTC breach notification (500+ consumers)",
  },
  {
    name: "PCI DSS v4.0.1",
    year: "Mandatory Mar 31 2025",
    note: "Field-level PAN encryption, 12-char passwords, automated SIEM, DMARC",
  },
  {
    name: "SOX Section 404 (ITGC)",
    year: "PCAOB AS 2201",
    note: "Access management, change management, computer operations, SDLC",
  },
  {
    name: "FFIEC IT Handbook",
    year: "AIO Jun 2021 · DA&M Aug 2024",
    note: "Cloud governance, resilience, data architecture & management",
  },
  {
    name: "Interagency MRM Guidance",
    year: "Apr 17 2026",
    note: "Supersedes SR 11-7. Gen AI explicitly EXCLUDED — pending RFI",
  },
  {
    name: "NIST AI RMF 1.0 + AI 600-1",
    year: "Jul 2024",
    note: "GOVERN · MAP · MEASURE · MANAGE; confabulation risk; agentic AI profile",
  },
] as const;

// ── API base URL ──────────────────────────────────────────────────────────────
// In development Next.js rewrites /api/* to FastAPI via next.config.ts.
// In production set NEXT_PUBLIC_API_URL to the Railway API service URL.
export const API_BASE =
  typeof window !== "undefined"
    ? "" // browser: go through Next.js rewrite proxy
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");
