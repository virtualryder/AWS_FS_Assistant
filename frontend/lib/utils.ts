import { clsx, type ClassValue } from "clsx";
import { formatDistanceToNow, parseISO } from "date-fns";

/** Tailwind class merge helper. */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/** Human-readable relative time, e.g. "3 hours ago". */
export function timeAgo(isoString: string | null | undefined): string {
  if (!isoString) return "";
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true });
  } catch {
    return "";
  }
}

/** Truncate text to maxLen characters with an ellipsis. */
export function truncate(text: string, maxLen = 58): string {
  if (text.length <= maxLen) return text;
  const cut = text.slice(0, maxLen).lastIndexOf(" ");
  return text.slice(0, cut > maxLen * 0.6 ? cut : maxLen) + "…";
}

/** Copy text to clipboard, returning true on success. */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

/** Trigger a browser download of text content as a file. */
export function downloadText(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
