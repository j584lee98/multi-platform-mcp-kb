"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function GoogleDriveConnectorPage() {
  const [user, setUser] = useState<string | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
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
    } catch (error) {
      console.error("Failed to check status", error);
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
    } catch (error) {
      console.error("Failed to disconnect", error);
    }
  };

  if (!user || loading) {
    return <div className="page-container"><div className="card text-center">Loading...</div></div>;
  }

  return (
    <div className="page-container">
      <div className="card max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold m-0 text-left">Google Drive Connector</h1>
          <button onClick={() => router.push("/home")} className="text-blue-600 hover:underline">
            Back to Home
          </button>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 mb-8">
          <div className="flex items-center gap-3">
            <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-8 h-8" />
            <div>
              <h3 className="font-semibold">Google Drive</h3>
              <p className="text-sm text-gray-500">
                {connected ? "Connected" : "Not connected"}
              </p>
            </div>
          </div>
          
          {connected ? (
            <button 
              onClick={handleDisconnect}
              className="px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 font-medium transition-colors"
            >
              Disconnect
            </button>
          ) : (
            <button 
              onClick={handleConnect}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium transition-colors"
            >
              Connect
            </button>
          )}
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold border-b pb-2">Available Tools</h2>
          
          {connected ? (
            <div className="grid gap-4">
              <div className="p-4 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium text-blue-600 mb-1">list_files</h3>
                    <p className="text-sm text-gray-600">List files from your Google Drive.</p>
                  </div>
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Ready</span>
                </div>
              </div>
              {/* Add more tools here as they become available */}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
              Connect to Google Drive to see available tools.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
