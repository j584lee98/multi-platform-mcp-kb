"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

function getUsernameFromStoredAuth(): string | null {
  if (typeof window === "undefined") return null;

  const auth = localStorage.getItem("auth");
  if (!auth) return null;

  try {
    const decoded = atob(auth);
    const username = decoded.split(":")[0];
    return username || null;
  } catch {
    return null;
  }
}

function subscribeToAuthChanges(onStoreChange: () => void): () => void {
  if (typeof window === "undefined") return () => {};

  window.addEventListener("storage", onStoreChange);
  window.addEventListener("auth", onStoreChange as EventListener);

  return () => {
    window.removeEventListener("storage", onStoreChange);
    window.removeEventListener("auth", onStoreChange as EventListener);
  };
}

export default function HomePage() {
  const router = useRouter();
  const user = useSyncExternalStore(
    subscribeToAuthChanges,
    getUsernameFromStoredAuth,
    () => null
  );
  const isHydrated = useSyncExternalStore(
    subscribeToAuthChanges,
    () => true,
    () => false
  );

  useEffect(() => {
    if (!isHydrated) return;

    if (!user) {
      router.replace("/login");
    }
  }, [isHydrated, user, router]);

  if (!user) {
    return null;
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="text-center mb-16 pt-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Multi-Platform MCP Knowledge Base
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          A unified interface for accessing and querying data across your favorite platforms using the Model Context Protocol.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {/* Google Drive Card */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
          <div className="h-14 w-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6 text-blue-600">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Google Drive</h2>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Connect your Google Drive to access, search, and manage your documents, spreadsheets, and presentations securely.
          </p>
          <Link 
            href="/connectors/google-drive"
            className="text-blue-600 font-semibold hover:text-blue-700 inline-flex items-center group"
          >
            Manage Connection 
            <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        </div>

        {/* GitHub Card */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
          <div className="h-14 w-14 bg-gray-50 rounded-xl flex items-center justify-center mb-6 text-gray-700">
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-3">GitHub</h2>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Link your GitHub account to explore repositories, search code, and track issues across your projects.
          </p>
          <Link 
            href="/connectors/github"
            className="text-blue-600 font-semibold hover:text-blue-700 inline-flex items-center group"
          >
            Manage Connection 
            <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        </div>

        {/* Slack Card */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
          <div className="h-14 w-14 bg-purple-50 rounded-xl flex items-center justify-center mb-6 text-purple-600">
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.52v-6.315zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.522 2.521 2.527 2.527 0 0 1-2.522-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.522 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.522 2.521A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.52h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.522 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-3">Slack</h2>
          <p className="text-gray-600 mb-6 leading-relaxed">
            Integrate Slack to search through channel history, find conversations, and access shared content.
          </p>
          <Link 
            href="/connectors/slack"
            className="text-blue-600 font-semibold hover:text-blue-700 inline-flex items-center group"
          >
            Manage Connection 
            <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        </div>
      </div>

      <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-10 text-center text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-4">
          Ready to start querying?
        </h2>
        <p className="text-blue-100 mb-8 max-w-2xl mx-auto text-lg">
          Use our AI-powered chat interface to ask questions across all your connected data sources. 
          The agent uses the Model Context Protocol (MCP) to securely access your information.
        </p>
        <Link 
          href="/chat"
          className="inline-block bg-white text-blue-600 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition-colors shadow-md"
        >
          Start Chatting Now
        </Link>
      </div>
    </div>
  );
}

