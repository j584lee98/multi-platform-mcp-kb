"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const isActive = (path: string) => pathname === path;

  const handleLogout = () => {
    localStorage.removeItem("auth");
    router.push("/login");
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col sticky top-0">
      <div className="p-6 border-b border-gray-100">
        <h1 className="text-xl font-bold text-blue-600">MCP KB</h1>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="px-4 mb-2">
          <Link 
            href="/" 
            className={`block px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isActive("/") 
                ? "bg-blue-50 text-blue-700" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            Home
          </Link>
          <Link 
            href="/chat" 
            className={`block px-4 py-2 rounded-md text-sm font-medium transition-colors mt-1 ${
              isActive("/chat") 
                ? "bg-blue-50 text-blue-700" 
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            Chat
          </Link>
        </div>

        <div className="px-4 mt-6">
          <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Connectors
          </h3>
          <div className="space-y-1">
            <Link 
              href="/connectors/google-drive" 
              className={`block px-4 py-2 rounded-md text-sm font-medium transition-colors ml-2 ${
                isActive("/connectors/google-drive") 
                  ? "bg-blue-50 text-blue-700" 
                  : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              Google Drive
            </Link>
            <Link 
              href="/connectors/github" 
              className={`block px-4 py-2 rounded-md text-sm font-medium transition-colors ml-2 ${
                isActive("/connectors/github") 
                  ? "bg-blue-50 text-blue-700" 
                  : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              GitHub
            </Link>
            <Link 
              href="/connectors/slack" 
              className={`block px-4 py-2 rounded-md text-sm font-medium transition-colors ml-2 ${
                isActive("/connectors/slack") 
                  ? "bg-blue-50 text-blue-700" 
                  : "text-gray-700 hover:bg-gray-50"
              }`}
            >
              Slack
            </Link>
          </div>
        </div>
      </nav>

      <div className="p-4 border-t border-gray-100">
        <button 
          onClick={handleLogout}
          className="w-full px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-md transition-colors mb-2"
        >
          Logout
        </button>
        <div className="text-xs text-gray-400 text-center">
          v0.1.0
        </div>
      </div>
    </aside>
  );
}
