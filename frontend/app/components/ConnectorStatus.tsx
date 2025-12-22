"use client";

import { useEffect, useState } from "react";

interface Statuses {
  google: boolean;
  github: boolean;
  slack: boolean;
}

export default function ConnectorStatus() {
  const [statuses, setStatuses] = useState<Statuses>({
    google: false,
    github: false,
    slack: false,
  });

  useEffect(() => {
    const fetchStatus = async () => {
      const auth = localStorage.getItem("auth");
      if (!auth) return;

      try {
        const res = await fetch("http://localhost:8000/auth/connectors/status", {
          headers: {
            Authorization: `Basic ${auth}`,
          },
        });
        if (res.ok) {
          const data = await res.json();
          setStatuses(data);
        }
      } catch (error) {
        console.error("Failed to fetch connector status:", error);
      }
    };

    fetchStatus();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-6 py-4 border-b border-gray-200 mb-4">
      <ConnectorIndicator label="Google Drive" connected={statuses.google} />
      <ConnectorIndicator label="GitHub" connected={statuses.github} />
      <ConnectorIndicator label="Slack" connected={statuses.slack} />
    </div>
  );
}

const ConnectorIndicator = ({ label, connected }: { label: string; connected: boolean }) => (
  <div className="flex items-center gap-2 group relative cursor-default">
    <div
      className={`w-2.5 h-2.5 rounded-full border-2 ${
        connected ? "bg-green-500 border-green-500" : "bg-transparent border-gray-400"
      }`}
    />
    <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</span>
    
    {/* Tooltip */}
    <div className="absolute top-full mt-1 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-800 text-white text-[11px] rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
      {connected ? "Connected" : "Not connected"}
    </div>
  </div>
);
