"use client";

interface Props {
  message: string;
  visible: boolean;
}

export default function StatusTicker({ message, visible }: Props) {
  if (!visible || !message) return null;

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-950 border border-blue-100 dark:border-blue-900 rounded-lg">
      {/* Spinner */}
      <svg
        className="animate-spin h-3.5 w-3.5 text-blue-500 flex-shrink-0"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12" cy="12" r="10"
          stroke="currentColor" strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
      <span className="status-ticker flex-1">{message}</span>
    </div>
  );
}
