"use client";

import { useCallback, useEffect, useState } from "react";

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

interface Repo {
  id: number;
  name: string;
  full_name: string;
  private: boolean;
  html_url: string;
  description: string;
  updated_at: string;
}

interface Issue {
  number: number;
  title: string;
  state: string;
  html_url: string;
  created_at: string;
  user: string | null;
}

type ViewMode = 'repos' | 'issues';

export default function GitHubConnectorPage() {
  const [connected, setConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [repos, setRepos] = useState<Repo[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('repos');
  const [searchQuery, setSearchQuery] = useState<string>("");

  const fetchRepos = useCallback(async (username: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/mcp/github/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          tool_name: "list_repos",
          arguments: {}
        })
      });
      const data = await res.json();
      try {
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setRepos([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setRepos(parsedResponse);
        } else {
          setRepos([]);
        }
      } catch (e) {
        console.error("Failed to parse repos response", e);
        setRepos([]);
      }
    } catch (error) {
      console.error("Failed to fetch repos", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const checkStatus = useCallback(async (username: string) => {
    try {
      const res = await fetch(`http://localhost:8000/auth/github/status?username=${username}`);
      const data = await res.json();
      setConnected(data.connected);
      if (data.connected) {
        fetchRepos(username);
      }
    } catch (error) {
      console.error("Failed to check status", error);
    } finally {
      setLoading(false);
    }
  }, [fetchRepos]);

  useEffect(() => {
    const user = getUsernameFromStoredAuth();
    if (user) {
      checkStatus(user);
    }
  }, [checkStatus]);

  const searchRepos = async (e: React.FormEvent) => {
    if (e && e.preventDefault) e.preventDefault();
    const user = getUsernameFromStoredAuth();
    if (!user) return;
    if (!searchQuery.trim()) {
      fetchRepos(user);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/mcp/github/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "search_repos",
          arguments: { query: searchQuery }
        })
      });
      const data = await res.json();
      try {
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setRepos([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setRepos(parsedResponse);
        } else {
          setRepos([]);
        }
      } catch (e) {
        console.error("Failed to parse search results", e);
        setRepos([]);
      }
    } catch (error) {
      console.error("Failed to search", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIssues = async (repoFullName: string) => {
    const user = getUsernameFromStoredAuth();
    if (!user) return;
    setLoading(true);
    setSelectedRepo(repoFullName);
    setViewMode('issues');
    
    try {
      const res = await fetch("http://localhost:8000/mcp/github/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "list_issues",
          arguments: { repo_full_name: repoFullName }
        })
      });
      const data = await res.json();
      try {
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setIssues([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setIssues(parsedResponse);
        } else {
          setIssues([]);
        }
      } catch (e) {
        console.error("Failed to parse issues response", e);
        setIssues([]);
      }
    } catch (error) {
      console.error("Failed to fetch issues", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    const user = getUsernameFromStoredAuth();
    try {
      const res = await fetch(`http://localhost:8000/auth/github/login?username=${user}`);
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error("Failed to initiate GitHub login", error);
    }
  };

  const handleDisconnect = async () => {
    const user = getUsernameFromStoredAuth();
    try {
      await fetch(`http://localhost:8000/auth/github/disconnect?username=${user}`, {
        method: "DELETE",
      });
      setConnected(false);
      setRepos([]);
      setIssues([]);
      setSelectedRepo(null);
    } catch (error) {
      console.error("Failed to disconnect", error);
    }
  };

  const handleBackToRepos = () => {
    setViewMode('repos');
    setSelectedRepo(null);
    setIssues([]);
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Connection Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8 flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-gray-50 rounded-full mb-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="https://www.svgrepo.com/show/475654/github-color.svg" alt="GitHub" className="w-12 h-12" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">GitHub</h1>
        
        {connected ? (
          <button 
            onClick={handleDisconnect}
            className="w-64 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors border border-red-100"
          >
            Disconnect
          </button>
        ) : (
          <button 
            onClick={handleConnect}
            className="w-64 px-4 py-2 text-sm font-medium text-white bg-gray-900 hover:bg-gray-800 rounded-lg transition-colors shadow-sm"
          >
            Connect
          </button>
        )}
      </div>

      {connected && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {/* Toolbar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {viewMode === 'repos' ? (
              <form onSubmit={searchRepos} className="relative w-full sm:w-72">
                <input
                  type="text"
                  placeholder="Search repositories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all"
                />
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
              </form>
            ) : (
              <div className="flex items-center gap-4">
                <button 
                  onClick={handleBackToRepos}
                  className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                >
                  ← Back to Repositories
                </button>
                <span className="text-sm font-semibold text-gray-900">{selectedRepo}</span>
              </div>
            )}
          </div>

          {/* Content Area */}
          <div className="min-h-[400px] relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                <div className="flex flex-col items-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                  <p className="text-sm text-gray-500">Loading...</p>
                </div>
              </div>
            ) : null}

            {viewMode === 'repos' ? (
              repos.length === 0 && !loading ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
                  <div className="text-4xl mb-4">📦</div>
                  <p className="text-lg font-medium text-gray-900">No repositories found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-100 bg-gray-50/50">
                        <th className="px-6 py-3 font-medium text-gray-500">Name</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Description</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Last Updated</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {repos.map((repo) => (
                        <tr key={repo.id} className="group hover:bg-gray-50/50 transition-colors">
                          <td className="px-6 py-3">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{repo.private ? '🔒' : '📖'}</span>
                              <a href={repo.html_url} target="_blank" rel="noopener noreferrer" className="font-medium text-gray-900 hover:underline">
                                {repo.full_name}
                              </a>
                            </div>
                          </td>
                          <td className="px-6 py-3 text-gray-500 max-w-xs truncate">
                            {repo.description || '-'}
                          </td>
                          <td className="px-6 py-3 text-gray-500">
                            {new Date(repo.updated_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-3">
                            <button
                              onClick={() => fetchIssues(repo.full_name)}
                              className="text-blue-600 hover:text-blue-800 font-medium"
                            >
                              View Issues
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            ) : (
              // Issues View
              issues.length === 0 && !loading ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
                  <div className="text-4xl mb-4">✅</div>
                  <p className="text-lg font-medium text-gray-900">No open issues found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-100 bg-gray-50/50">
                        <th className="px-6 py-3 font-medium text-gray-500">#</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Title</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Author</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Created</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {issues.map((issue) => (
                        <tr key={issue.number} className="group hover:bg-gray-50/50 transition-colors">
                          <td className="px-6 py-3 text-gray-500">#{issue.number}</td>
                          <td className="px-6 py-3">
                            <a href={issue.html_url} target="_blank" rel="noopener noreferrer" className="font-medium text-gray-900 hover:underline">
                              {issue.title}
                            </a>
                          </td>
                          <td className="px-6 py-3 text-gray-500">{issue.user}</td>
                          <td className="px-6 py-3 text-gray-500">
                            {new Date(issue.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
