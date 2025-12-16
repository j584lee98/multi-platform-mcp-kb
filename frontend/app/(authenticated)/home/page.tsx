"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const [user, setUser] = useState<string | null>(null);
  const [files, setFiles] = useState<string>("");
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
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("auth");
    router.push("/login");
  };

  const handleListFiles = async () => {
    try {
      setFiles("Loading...");
      const res = await fetch("http://localhost:8000/chat/list-files", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user }),
      });
      const data = await res.json();
      setFiles(data.response);
    } catch (error) {
      console.error("Failed to list files", error);
      setFiles("Error listing files");
    }
  };

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div className="page-container">
      <div className="card text-center">
        <h1>Home</h1>
        <p className="text-lg mb-6">Welcome, <span className="font-semibold">{user}</span>!</p>
        
        <div className="mb-8 space-y-4">
          <button 
            onClick={() => router.push("/connectors/google-drive")}
            className="bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 flex items-center justify-center gap-2 w-full py-2 rounded-md"
          >
            <img src="https://www.svgrepo.com/show/475656/google-color.svg" alt="Google" className="w-5 h-5" />
            Manage Google Drive Connection
          </button>

          <button
            onClick={handleListFiles}
            className="bg-blue-600 text-white hover:bg-blue-700 flex items-center justify-center gap-2 w-full py-2 rounded-md"
          >
            List My Google Drive Files
          </button>
        </div>

        {files && (
          <div className="mb-8 p-4 bg-gray-100 rounded text-left whitespace-pre-wrap font-mono text-sm overflow-auto max-h-60 border border-gray-200">
            {files}
          </div>
        )}

        <button onClick={handleLogout} className="bg-red-500 hover:bg-red-600">Logout</button>
      </div>
    </div>
  );
}
