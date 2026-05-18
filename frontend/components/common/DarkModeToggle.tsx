"use client";

import { useTheme } from "@/lib/theme";

export default function DarkModeToggle() {
  const { theme, toggle } = useTheme();

  return (
    <button
      onClick={toggle}
      title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      className="fixed bottom-5 right-5 z-50
        w-10 h-10 flex items-center justify-center
        rounded-full shadow-lg border
        bg-white dark:bg-gray-800
        border-gray-200 dark:border-gray-600
        text-gray-700 dark:text-gray-200
        hover:bg-gray-100 dark:hover:bg-gray-700
        transition-colors text-lg"
    >
      {theme === "dark" ? "☀️" : "🌙"}
    </button>
  );
}
