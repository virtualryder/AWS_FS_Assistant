"use client";

import { useEffect, useState } from "react";

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const dark = stored ? stored === "dark" : prefersDark;
    setIsDark(dark);
    setMounted(true);
    document.documentElement.classList.toggle("dark", dark);
  }, []);

  function toggle() {
    const next = !isDark;
    setIsDark(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    document.documentElement.classList.toggle("dark", next);
  }

  // Always render the button; show a neutral icon until mounted
  return (
    <button
      onClick={toggle}
      title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      aria-label="Toggle dark mode"
      className="fixed bottom-5 right-5 z-[9999]
        w-11 h-11 flex items-center justify-center text-lg
        rounded-full shadow-xl
        bg-white dark:bg-gray-800
        border-2 border-gray-300 dark:border-gray-600
        text-gray-800 dark:text-gray-100
        hover:border-aws-orange hover:scale-110
        transition-all duration-200"
    >
      {mounted ? (isDark ? "☀️" : "🌙") : "🌙"}
    </button>
  );
}
