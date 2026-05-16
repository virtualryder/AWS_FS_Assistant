import { redirect } from "next/navigation";

/**
 * Root route — redirect immediately to /customers so the URL is always
 * scoped to a customer context.
 */
export default function RootPage() {
  redirect("/customers");
}
