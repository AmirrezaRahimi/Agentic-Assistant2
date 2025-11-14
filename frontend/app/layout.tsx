import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vardast | AI Assistant Builder",
  description: "Create and manage AI assistants with knowledge grounding.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-6 py-10">
          <header className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Vardast</h1>
              <p className="text-sm text-slate-300">Build assistants, ground them with knowledge, and chat instantly.</p>
            </div>
            <a
              className="text-sm font-semibold text-brand hover:text-brand-dark"
              href="https://openai.com"
              target="_blank"
              rel="noreferrer"
            >
              Powered by GPT-4o mini
            </a>
          </header>
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
