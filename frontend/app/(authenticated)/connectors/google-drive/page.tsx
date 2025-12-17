"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
}

interface Breadcrumb {
  id: string;
  name: string;
}

export default function GoogleDriveConnectorPage() {
  const [user, setUser] = useState<string | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [files, setFiles] = useState<DriveFile[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string>("root");
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([{ id: "root", name: "My Drive" }]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    const auth = localStorage.getItem("auth");
    if (!auth) {
      router.push("/login");
      return;
    }

    // Decode username from stored auth
    const decoded = atob(auth);
    const username = decoded.split(":")[0];
    setUser(username);

    // Check connection status
    checkStatus(username);
  }, [router]);

  const checkStatus = async (username: string) => {
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
  };

  const fetchFiles = async (username: string, folderId: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          tool_name: "list_files",
          arguments: { folder_id: folderId }
        })
      });
      const data = await res.json();
      try {
        const parsedFiles = JSON.parse(data.response);
        if (Array.isArray(parsedFiles)) {
          setFiles(parsedFiles);
        } else {
          setFiles([]);
        }
      } catch (e) {
        console.error("Failed to parse files", e);
        setFiles([]);
      }
    } catch (error) {
      console.error("Failed to fetch files", error);
    } finally {
      setLoading(false);
    }
  };

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

  const handleCreateFolder = async () => {
    const name = prompt("Enter folder name:");
    if (!name || !user) return;

    try {
      await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "create_folder",
          arguments: { name, parent_id: currentFolder }
        })
      });
      fetchFiles(user, currentFolder);
    } catch (error) {
      console.error("Failed to create folder", error);
    }
  };

  const handleCreateFile = async () => {
    const name = prompt("Enter file name:");
    if (!name || !user) return;
    const content = prompt("Enter file content:");
    if (content === null) return;

    try {
      await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "create_text_file",
          arguments: { name, content, parent_id: currentFolder }
        })
      });
      fetchFiles(user, currentFolder);
    } catch (error) {
      console.error("Failed to create file", error);
    }
  };

  const handleDelete = async (fileId: string) => {
    if (!confirm("Are you sure you want to delete this item?") || !user) return;

    try {
      await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "delete_file",
          arguments: { file_id: fileId }
        })
      });
      fetchFiles(user, currentFolder);
    } catch (error) {
      console.error("Failed to delete item", error);
    }
  };

  const handleRename = async (fileId: string, currentName: string) => {
    const newName = prompt("Enter new name:", currentName);
    if (!newName || !user || newName === currentName) return;

    try {
      await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "rename_file",
          arguments: { file_id: fileId, new_name: newName }
        })
      });
      fetchFiles(user, currentFolder);
    } catch (error) {
      console.error("Failed to rename item", error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    if (!searchQuery.trim()) {
      fetchFiles(user, currentFolder);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/mcp/google-drive/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "search_files",
          arguments: { query: `name contains '${searchQuery}' and trashed = false` }
        })
      });
      const data = await res.json();
      try {
        const parsedFiles = JSON.parse(data.response);
        if (Array.isArray(parsedFiles)) {
          setFiles(parsedFiles);
        } else {
          setFiles([]);
        }
      } catch (e) {
        console.error("Failed to parse search results", e);
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
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Google Drive</h1>
          <p className="text-gray-500 mt-1">Manage your files and folders directly from here.</p>
        </div>
        <button 
          onClick={() => router.push("/home")} 
          className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
        >
          ← Back to Home
        </button>
      </div>

      {/* Connection Status Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-lg">
              <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-8 h-8" />
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900">Connection Status</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                <p className="text-sm text-gray-600">
                  {connected ? "Connected to Google Drive" : "Not connected"}
                </p>
              </div>
            </div>
          </div>
          
          {connected ? (
            <button 
              onClick={handleDisconnect}
              className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors border border-red-100"
            >
              Disconnect
            </button>
          ) : (
            <button 
              onClick={handleConnect}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
            >
              Connect Account
            </button>
          )}
        </div>
      </div>

      {connected && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {/* Toolbar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <button 
                onClick={handleCreateFolder} 
                className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
              >
                <span className="text-lg leading-none">+</span> New Folder
              </button>
              <button 
                onClick={handleCreateFile} 
                className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
              >
                <span className="text-lg leading-none">+</span> New File
              </button>
            </div>
            
            <form onSubmit={handleSearch} className="relative w-full sm:w-72">
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
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
                  className={`hover:text-blue-600 transition-colors ${
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
                      <th className="px-6 py-3 font-medium text-gray-500 w-[50%]">Name</th>
                      <th className="px-6 py-3 font-medium text-gray-500 w-[30%]">Type</th>
                      <th className="px-6 py-3 font-medium text-gray-500 text-right w-[20%]">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {files.map((file) => (
                      <tr key={file.id} className="group hover:bg-blue-50/50 transition-colors">
                        <td className="px-6 py-3">
                          {file.mimeType === "application/vnd.google-apps.folder" ? (
                            <div
                              onClick={() => handleNavigate(file.id, file.name)}
                              className="flex items-center gap-3 text-gray-700"
                            >
                              <span className="text-xl">📁</span>
                              {file.name}
                            </div>
                          ) : (
                            <div className="flex items-center gap-3 text-gray-700">
                              <span className="text-xl">📄</span>
                              {file.name}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-3 text-gray-500 truncate max-w-[200px]" title={file.mimeType}>
                          {file.mimeType.split('.').pop()?.split('-').pop()}
                        </td>
                        <td className="px-6 py-3 text-right">
                          <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleRename(file.id, file.name)}
                              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-100 rounded-md transition-all"
                              title="Rename"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={() => handleDelete(file.id)}
                              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-100 rounded-md transition-all"
                              title="Delete"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

