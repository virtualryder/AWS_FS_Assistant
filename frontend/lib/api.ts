/**
 * API client — thin wrappers around fetch for all FastAPI endpoints.
 * SSE endpoints are handled separately in the useSSEStream hook.
 */

import type {
  Customer,
  Conversation,
  Message,
  CustomerDocument,
  KnowledgeBaseStatus,
  KBSource,
  Project,
} from "./types";

const BASE = "/api";

// ── Generic fetch helper ──────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse error
    }
    throw new Error(`API ${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Customers ─────────────────────────────────────────────────────────────────

export const customersApi = {
  list: (): Promise<Customer[]> =>
    apiFetch("/customers"),

  get: (id: string): Promise<Customer> =>
    apiFetch(`/customers/${id}`),

  create: (data: {
    name: string;
    industry?: string;
    arch_context?: string;
    stage?: string;
  }): Promise<Customer> =>
    apiFetch("/customers", { method: "POST", body: JSON.stringify(data) }),

  update: (
    id: string,
    data: { name: string; industry?: string; arch_context?: string; stage?: string }
  ): Promise<Customer> =>
    apiFetch(`/customers/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  delete: (id: string): Promise<void> =>
    apiFetch(`/customers/${id}`, { method: "DELETE" }),
};

// ── Conversations ─────────────────────────────────────────────────────────────

export const conversationsApi = {
  list: (customerId: string): Promise<Conversation[]> =>
    apiFetch(`/customers/${customerId}/conversations`),

  get: (convId: string): Promise<Conversation> =>
    apiFetch(`/conversations/${convId}`),

  create: (customerId: string): Promise<Conversation> =>
    apiFetch(`/customers/${customerId}/conversations`, { method: "POST" }),

  updateTitle: (convId: string, title: string): Promise<Conversation> =>
    apiFetch(`/conversations/${convId}/title`, {
      method: "PUT",
      body: JSON.stringify({ title }),
    }),

  delete: (convId: string): Promise<void> =>
    apiFetch(`/conversations/${convId}`, { method: "DELETE" }),

  getMessages: (convId: string): Promise<Message[]> =>
    apiFetch(`/conversations/${convId}/messages`),

  clearMessages: (convId: string): Promise<void> =>
    apiFetch(`/conversations/${convId}/messages`, { method: "DELETE" }),
};

// ── Documents ─────────────────────────────────────────────────────────────────

export const documentsApi = {
  list: (customerId: string): Promise<CustomerDocument[]> =>
    apiFetch(`/customers/${customerId}/documents`),

  upload: async (
    customerId: string,
    file: File
  ): Promise<CustomerDocument> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/customers/${customerId}/documents`, {
      method: "POST",
      body: form,
      // Don't set Content-Type — browser sets it with the boundary
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail ?? detail;
      } catch {
        // ignore
      }
      throw new Error(`Upload failed ${res.status}: ${detail}`);
    }
    return res.json();
  },

  toggle: (docId: string, isActive: boolean): Promise<{ id: string; is_active: boolean }> =>
    apiFetch(`/documents/${docId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: isActive }),
    }),

  delete: (docId: string): Promise<void> =>
    apiFetch(`/documents/${docId}`, { method: "DELETE" }),
};

// ── Projects ──────────────────────────────────────────────────────────────────

export const projectsApi = {
  list: (customerId: string): Promise<Project[]> =>
    apiFetch(`/customers/${customerId}/projects`),

  get: (projectId: string): Promise<Project> =>
    apiFetch(`/projects/${projectId}`),

  create: (customerId: string, data: { name: string; description?: string }): Promise<Project> =>
    apiFetch(`/customers/${customerId}/projects`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (projectId: string, data: { name: string; description?: string }): Promise<Project> =>
    apiFetch(`/projects/${projectId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (projectId: string): Promise<void> =>
    apiFetch(`/projects/${projectId}`, { method: "DELETE" }),

  listConversations: (projectId: string): Promise<Conversation[]> =>
    apiFetch(`/projects/${projectId}/conversations`),

  createConversation: (projectId: string): Promise<Conversation> =>
    apiFetch(`/projects/${projectId}/conversations`, { method: "POST" }),

  listDocuments: (projectId: string): Promise<CustomerDocument[]> =>
    apiFetch(`/projects/${projectId}/documents`),

  uploadDocument: async (projectId: string, file: File): Promise<CustomerDocument> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/projects/${projectId}/documents`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        detail = body.detail ?? detail;
      } catch { /* ignore */ }
      throw new Error(`Upload failed ${res.status}: ${detail}`);
    }
    return res.json();
  },
};

// ── Knowledge base ────────────────────────────────────────────────────────────

export const kbApi = {
  status: (): Promise<KnowledgeBaseStatus> =>
    apiFetch("/knowledge-base/status"),

  sources: (): Promise<{ sources: KBSource[] }> =>
    apiFetch("/knowledge-base/sources"),

  triggerIngest: (maxPages?: number): Promise<{ status: string; message: string; max_pages: number }> =>
    apiFetch("/knowledge-base/ingest", {
      method: "POST",
      body: JSON.stringify({ max_pages: maxPages ?? 75 }),
    }),
};
