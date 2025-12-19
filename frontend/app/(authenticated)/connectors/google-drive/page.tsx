"use client";

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

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

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  modifiedTime?: string;
  size?: string;
  webViewLink?: string;
  description?: string;
}

interface Breadcrumb {
  id: string;
  name: string;
}

type SortField = 'name' | 'modifiedTime';
type SortOrder = 'asc' | 'desc';

export default function GoogleDriveConnectorPage() {
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
  const [connected, setConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [files, setFiles] = useState<DriveFile[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string>("root");
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([{ id: "root", name: "My Drive" }]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const router = useRouter();

  const fetchFiles = useCallback(async (username: string, folderId: string) => {
    setLoading(true);
    try {
      const orderBy = sortField === 'name' 
        ? `folder,name ${sortOrder === 'desc' ? 'desc' : ''}`.trim()
        : `folder,modifiedTime ${sortOrder === 'desc' ? 'desc' : ''}`.trim();

      const args = { 
        folder_id: folderId,
        order_by: orderBy
      };
      
      const res = await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          tool_name: "list_files",
          arguments: args
        })
      });
      const data = await res.json();
      try {
        // Check if response is an error string
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setFiles([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setFiles(parsedResponse);
        } else {
          setFiles([]);
        }
      } catch (e) {
        console.error("Failed to parse files response", e);
        console.log("Raw response:", data.response);
        setFiles([]);
      }
    } catch (error) {
      console.error("Failed to fetch files", error);
    } finally {
      setLoading(false);
    }
  }, [sortField, sortOrder]);

  const checkStatus = useCallback(async (username: string) => {
    try {
      const res = await fetch(`http://localhost:8000/auth/google/status?username=${username}`);
      const data = await res.json();
      setConnected(data.connected);
      if (data.connected) {
        fetchFiles(username, "root");
      }
    } catch (error) {
      console.error("Failed to check status", error);
    } finally {
      setLoading(false);
    }
  }, [fetchFiles]);

  useEffect(() => {
    if (!isHydrated) return;

    if (!user) {
      router.replace("/login");
      return;
    }

    checkStatus(user);
  }, [checkStatus, isHydrated, router, user]);

  const handleConnect = async () => {
    try {
      const res = await fetch(`http://localhost:8000/auth/google/login?username=${user}`);
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error("Failed to initiate Google login", error);
    }
  };

  const handleDisconnect = async () => {
    try {
      await fetch(`http://localhost:8000/auth/google/disconnect?username=${user}`, {
        method: "DELETE",
      });
      setConnected(false);
      setFiles([]);
    } catch (error) {
      console.error("Failed to disconnect", error);
    }
  };

  const handleNavigate = (folderId: string, folderName: string) => {
    setCurrentFolder(folderId);
    setBreadcrumbs([...breadcrumbs, { id: folderId, name: folderName }]);
    if (user) fetchFiles(user, folderId);
  };

  const handleBreadcrumbClick = (index: number) => {
    const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
    setBreadcrumbs(newBreadcrumbs);
    const targetFolder = newBreadcrumbs[newBreadcrumbs.length - 1];
    setCurrentFolder(targetFolder.id);
    if (user) fetchFiles(user, targetFolder.id);
  };

  const handleSort = (field: SortField) => {
    const newOrder = field === sortField && sortOrder === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortOrder(newOrder);
  };

  useEffect(() => {
    if (user && connected) {
      fetchFiles(user, currentFolder);
    }
  }, [connected, currentFolder, fetchFiles, user]);

  const handleSearch = async (e: React.FormEvent) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!user) return;
    if (!searchQuery.trim()) {
      fetchFiles(user, currentFolder);
      return;
    }

    setLoading(true);
    try {
      const args = { 
        query: `name contains '${searchQuery}' and trashed = false`,
        order_by: sortField === 'name' 
          ? `folder,name ${sortOrder === 'desc' ? 'desc' : ''}`.trim()
          : `folder,modifiedTime ${sortOrder === 'desc' ? 'desc' : ''}`.trim()
      };
      
      const res = await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "search_files",
          arguments: args
        })
      });
      const data = await res.json();
      try {
        // Check if response is an error string
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setFiles([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setFiles(parsedResponse);
        } else {
          setFiles([]);
        }
      } catch (e) {
        console.error("Failed to parse search results", e);
        console.log("Raw response:", data.response);
        setFiles([]);
      }
    } catch (error) {
      console.error("Failed to search", error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Connection Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8 flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-blue-50 rounded-full mb-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-12 h-12" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Google Drive</h1>
        
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
            className="w-64 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
          >
            Connect
          </button>
        )}
      </div>

      {connected && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {/* Toolbar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <form onSubmit={handleSearch} className="relative w-full sm:w-72">
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            </form>
          </div>

          {/* Breadcrumbs */}
          <div className="px-4 py-3 border-b border-gray-200 bg-white flex items-center gap-2 text-sm overflow-x-auto">
            {breadcrumbs.map((crumb, index) => (
              <div key={crumb.id} className="flex items-center whitespace-nowrap">
                {index > 0 && <span className="mx-2 text-gray-400">/</span>}
                <button
                  onClick={() => handleBreadcrumbClick(index)}
                  className={`bg-transparent border-none hover:text-blue-600 transition-colors ${
                    index === breadcrumbs.length - 1 
                      ? "font-semibold text-gray-900 pointer-events-none" 
                      : "text-gray-600"
                  }`}
                >
                  {crumb.name}
                </button>
              </div>
            ))}
          </div>

          {/* File List */}
          <div className="min-h-[400px] relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                <div className="flex flex-col items-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="text-sm text-gray-500">Loading files...</p>
                </div>
              </div>
            ) : null}

            {files.length === 0 && !loading ? (
              <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
                <div className="text-4xl mb-4">📂</div>
                <p className="text-lg font-medium text-gray-900">No files found</p>
                <p className="text-sm">This folder is empty</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/50">
                      <th 
                        className="px-6 py-3 font-medium text-gray-500 w-[40%] cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort('name')}
                      >
                        Name {sortField === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                      <th className="px-6 py-3 font-medium text-gray-500 w-[15%]">Size</th>
                      <th className="px-6 py-3 font-medium text-gray-500 w-[15%]">Type</th>
                      <th 
                        className="px-6 py-3 font-medium text-gray-500 w-[30%] cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort('modifiedTime')}
                      >
                        Date Modified {sortField === 'modifiedTime' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {files.map((file) => (
                      <tr key={file.id} className="group hover:bg-blue-50/50 transition-colors">
                        <td className="px-6 py-3">
                          {file.mimeType === "application/vnd.google-apps.folder" ? (
                            <div
                              onClick={() => handleNavigate(file.id, file.name)}
                              className="flex items-center gap-3 text-gray-700 cursor-pointer"
                            >
                              <span className="text-xl">📁</span>
                              {file.name}
                            </div>
                          ) : (
                            <div 
                              onClick={() => file.webViewLink && window.open(file.webViewLink, '_blank')}
                              className="flex items-center gap-3 text-gray-700 cursor-pointer hover:text-blue-600"
                            >
                              <span className="text-xl">📄</span>
                              {file.name}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-3 text-gray-500 text-xs">
                          {file.size ? (parseInt(file.size) / 1024 / 1024).toFixed(2) + ' MB' : '-'}
                        </td>
                        <td className="px-6 py-3 text-gray-500 truncate max-w-[200px]" title={file.mimeType}>
                          {file.mimeType.split('.').pop()?.split('-').pop()}
                        </td>
                        <td className="px-6 py-3 text-gray-500">
                          {file.modifiedTime ? new Date(file.modifiedTime).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                
                {/* Pagination Controls Removed */}
                <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
                  <div className="text-sm text-gray-500">
                    Showing {files.length} items
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

