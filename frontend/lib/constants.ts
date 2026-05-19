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
    year: "2023 — 16 CFR Part 314",
    note: "MFA for all users, AES-256, 30-day FTC breach notification (500+ consumers)",
    url: "https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act/safeguards-rule",
  },
  {
    name: "PCI DSS v4.0.1",
    year: "Mandatory Mar 31 2025",
    note: "Field-level PAN encryption, 12-char passwords, automated SIEM, DMARC",
    url: "https://www.pcisecuritystandards.org/document_library/",
  },
  {
    name: "SOX Section 404 (ITGC)",
    year: "PCAOB AS 2201",
    note: "Access management, change management, computer operations, SDLC",
    url: "https://pcaobus.org/Standards/Auditing/Pages/AS2201.aspx",
  },
  {
    name: "FFIEC IT Handbook",
    year: "AIO Jun 2021 · DA&M Aug 2024",
    note: "Cloud governance, resilience, data architecture & management",
    url: "https://ithandbook.ffiec.gov/",
  },
  {
    name: "Interagency MRM Guidance",
    year: "Apr 17 2026",
    note: "Supersedes SR 11-7. Gen AI explicitly EXCLUDED — pending RFI",
    url: "https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm",
  },
  {
    name: "NIST AI RMF 1.0 + AI 600-1",
    year: "Jul 2024",
    note: "GOVERN · MAP · MEASURE · MANAGE; confabulation risk; agentic AI profile",
    url: "https://airc.nist.gov/RMF",
  },
] as const;

// ── AWS Documentation catalog (used by KnowledgeBasePanel) ───────────────────
// Key = source_label as stored in the DB. If indexed, the panel shows it green.
export const KB_CATALOG: { key: string; name: string; url: string; category: string }[] = [
  // Core Financial Services
  { key: "Bedrock",            name: "Amazon Bedrock",                        url: "https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html",             category: "AI / ML" },
  { key: "Bedrock AgentCore",  name: "Amazon Bedrock AgentCore",              url: "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-agentcore.html", category: "AI / ML" },
  { key: "SageMaker",          name: "Amazon SageMaker",                      url: "https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html",                          category: "AI / ML" },
  { key: "KMS",                name: "AWS KMS",                               url: "https://docs.aws.amazon.com/kms/latest/developerguide/overview.html",                  category: "Security" },
  { key: "GuardDuty",          name: "Amazon GuardDuty",                      url: "https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html",               category: "Security" },
  { key: "Security Hub",       name: "AWS Security Hub",                      url: "https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html",    category: "Security" },
  { key: "CloudTrail",         name: "AWS CloudTrail",                        url: "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html", category: "Security" },
  { key: "IAM",                name: "AWS IAM",                               url: "https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html",                   category: "Security" },
  { key: "IAM Identity Center",name: "AWS IAM Identity Center",               url: "https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html",               category: "Security" },
  { key: "Macie",              name: "Amazon Macie",                          url: "https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html",                     category: "Security" },
  { key: "Inspector",          name: "Amazon Inspector",                      url: "https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html",             category: "Security" },
  { key: "WAF",                name: "AWS WAF",                               url: "https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html",               category: "Security" },
  { key: "Network Firewall",   name: "AWS Network Firewall",                  url: "https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html", category: "Security" },
  { key: "Audit Manager",      name: "AWS Audit Manager",                     url: "https://docs.aws.amazon.com/audit-manager/latest/userguide/what-is.html",              category: "Security" },
  { key: "Config",             name: "AWS Config",                            url: "https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html",           category: "Security" },
  { key: "Secrets Manager",    name: "AWS Secrets Manager",                   url: "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html",               category: "Security" },
  { key: "RDS",                name: "Amazon RDS",                            url: "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html",                  category: "Database" },
  { key: "Aurora",             name: "Amazon Aurora",                         url: "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html", category: "Database" },
  { key: "DynamoDB",           name: "Amazon DynamoDB",                       url: "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html",   category: "Database" },
  { key: "VPC",                name: "Amazon VPC",                            url: "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",             category: "Networking" },
  { key: "PrivateLink",        name: "AWS PrivateLink",                       url: "https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html",          category: "Networking" },
  { key: "CloudFront",         name: "Amazon CloudFront",                     url: "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html", category: "Networking" },
  { key: "Lambda",             name: "AWS Lambda",                            url: "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",                            category: "Compute" },
  { key: "ECS",                name: "Amazon ECS",                            url: "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html",             category: "Compute" },
  { key: "EKS",                name: "Amazon EKS",                            url: "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html",                    category: "Compute" },
  { key: "S3",                 name: "Amazon S3",                             url: "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",                   category: "Storage" },
  { key: "Backup",             name: "AWS Backup",                            url: "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html",             category: "Storage" },
  { key: "CloudWatch",         name: "Amazon CloudWatch",                     url: "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html", category: "Observability" },
  { key: "Payment Cryptography", name: "AWS Payment Cryptography",            url: "https://docs.aws.amazon.com/payment-cryptography/latest/userguide/what-is-payment-cryptography.html", category: "Financial Services" },
  { key: "Prescriptive Guidance", name: "AWS Prescriptive Guidance (FinServ)", url: "https://aws.amazon.com/prescriptive-guidance/",                                      category: "Financial Services" },
  { key: "Well-Architected",   name: "Well-Architected Framework",            url: "https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html",            category: "Financial Services" },
];

// ── API base URL ──────────────────────────────────────────────────────────────
// In development Next.js rewrites /api/* to FastAPI via next.config.ts.
// In production set NEXT_PUBLIC_API_URL to the Railway API service URL.
export const API_BASE =
  typeof window !== "undefined"
    ? "" // browser: go through Next.js rewrite proxy
    : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");
