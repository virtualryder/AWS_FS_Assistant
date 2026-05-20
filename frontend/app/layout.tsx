import type { Metadata } from "next";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { ThemeProvider } from "@/lib/theme";
import AuthTokenSync from "@/components/auth/AuthTokenSync";

export const metadata: Metadata = {
  title: "AWS Financial Services Assistant",
  description:
    "AWS Financial Services Assistant — Compliance-Validated Architecture Design " +
    "powered by dual AI agents (AWS Architect + GenAI/ML Expert).",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // className="dark" sets dark mode server-side so the first paint is always dark.
    // ThemeProvider's useEffect will switch to "light" if the user stored that preference.
    // suppressHydrationWarning silences React when the client overrides the class attribute.
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        {/* Blocking script runs synchronously before React hydration.
            Reads localStorage so returning users get their saved preference immediately. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){var t=localStorage.getItem('theme');if(t==='light'){document.documentElement.classList.remove('dark');}})();`,
          }}
        />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-gray-300 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen">
        <ClerkProvider>
          <ThemeProvider>
            <AuthTokenSync />
            {children}
          </ThemeProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
