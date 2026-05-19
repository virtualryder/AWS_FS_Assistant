"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import type { Customer, Project, KnowledgeBaseStatus } from "@/lib/types";
import { customersApi, projectsApi, kbApi } from "@/lib/api";
import Sidebar from "@/components/sidebar/Sidebar";
import CustomerHeader from "@/components/customers/CustomerHeader";
import NewProjectModal from "@/components/projects/NewProjectModal";
import { timeAgo } from "@/lib/utils";

export default function CustomerPage() {
  const { customerId } = useParams<{ customerId: string }>();
  const router = useRouter();
  const [showNewProject, setShowNewProject] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const { data: customers = [], mutate: mutateCustomers } = useSWR<Customer[]>(
    "customers",
    () => customersApi.list(),
    { refreshInterval: 30_000 }
  );

  const { data: customer, mutate: mutateCustomer } = useSWR<Customer>(
    `customer-${customerId}`,
    () => customersApi.get(customerId)
  );

  const { data: projects = [], mutate: mutateProjects } = useSWR<Project[]>(
    `projects-${customerId}`,
    () => projectsApi.list(customerId),
    { refreshInterval: 30_000 }
  );

  const { data: kb } = useSWR<KnowledgeBaseStatus>("kb-status", () => kbApi.status(), {
    refreshInterval: 60_000,
  });

  async function handleDeleteProject(projectId: string) {
    await projectsApi.delete(projectId);
    mutateProjects(projects.filter((p) => p.id !== projectId), false);
    setConfirmDelete(null);
  }

  if (!customer) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-400 text-sm">
        Loading…
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        customers={customers}
        onCustomerCreated={() => mutateCustomers()}
        kbCount={kb?.chunk_count ?? 0}
      />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <CustomerHeader
          customer={customer}
          onUpdated={(updated) => {
            mutateCustomer(updated, false);
            mutateCustomers();
          }}
          onDeleted={() => {
            mutateCustomers();
            router.push("/customers");
          }}
        />

        <main className="flex-1 overflow-y-auto bg-gray-300 dark:bg-gray-950 px-8 py-6">
          <div className="max-w-3xl mx-auto space-y-5">
            {/* Header row */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">Projects</h2>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Each project has its own conversations, discovery brief, and documents.
                </p>
              </div>
              <button
                onClick={() => setShowNewProject(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold text-white
                  bg-aws-orange hover:bg-aws-orange-dk rounded-lg transition-colors"
              >
                + New Project
              </button>
            </div>

            {/* Project list */}
            {projects.length === 0 ? (
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-10 text-center">
                <div className="text-3xl mb-3">📁</div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">No projects yet</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">
                  Create a project to organise conversations, documents, and discovery briefs for a specific engagement.
                </p>
                <button
                  onClick={() => setShowNewProject(true)}
                  className="px-4 py-2 text-sm font-semibold text-white bg-aws-orange hover:bg-aws-orange-dk rounded-lg transition-colors"
                >
                  Create First Project
                </button>
              </div>
            ) : (
              <div className="grid gap-3">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    className="group bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700
                      hover:border-aws-orange/40 transition-colors"
                  >
                    <div className="p-5 flex items-start justify-between gap-4">
                      <Link
                        href={`/customers/${customerId}/projects/${project.id}`}
                        className="flex-1 min-w-0"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-base">📁</span>
                          <span className="font-semibold text-gray-900 dark:text-gray-100 hover:text-aws-orange transition-colors">
                            {project.name}
                          </span>
                        </div>
                        {project.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 line-clamp-2">
                            {project.description}
                          </p>
                        )}
                        <div className="flex items-center gap-3 text-[11px] text-gray-400 dark:text-gray-500">
                          <span>💬 {project.conversation_count} conversation{project.conversation_count !== 1 ? "s" : ""}</span>
                          <span>📄 {project.document_count} document{project.document_count !== 1 ? "s" : ""}</span>
                          <span>Updated {timeAgo(project.updated_at)}</span>
                        </div>
                      </Link>

                      {/* Actions */}
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <Link
                          href={`/customers/${customerId}/projects/${project.id}`}
                          className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700
                            text-gray-600 dark:text-gray-400 hover:border-aws-orange/50 hover:text-aws-orange
                            transition-colors"
                        >
                          Open →
                        </Link>
                        {confirmDelete === project.id ? (
                          <div className="flex items-center gap-1 ml-1">
                            <button
                              onClick={() => handleDeleteProject(project.id)}
                              className="text-xs text-white bg-red-500 hover:bg-red-600 px-2 py-1 rounded"
                            >
                              Delete
                            </button>
                            <button
                              onClick={() => setConfirmDelete(null)}
                              className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-1.5 py-1"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setConfirmDelete(project.id)}
                            className="opacity-0 group-hover:opacity-100 ml-1 text-gray-300 dark:text-gray-600 hover:text-red-500 transition-all text-lg leading-none"
                            title="Delete project"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {showNewProject && (
        <NewProjectModal
          customerId={customerId}
          onClose={() => setShowNewProject(false)}
          onCreated={() => {
            mutateProjects();
            setShowNewProject(false);
          }}
        />
      )}
    </div>
  );
}
