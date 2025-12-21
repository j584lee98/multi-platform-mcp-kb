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

interface Channel {
  id: string;
  name: string;
  is_channel: boolean;
  is_group: boolean;
  is_im: boolean;
  num_members: number;
  topic: string;
  purpose: string;
}

interface Message {
  ts: string;
  user: string;
  text: string;
  type: string;
  thread_ts?: string;
}

export default function SlackConnectorPage() {
  const [connected, setConnected] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

  const fetchChannels = useCallback(async (username: string) => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/mcp/slack/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          tool_name: "list_channels",
          arguments: {}
        })
      });
      const data = await res.json();
      try {
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setChannels([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setChannels(parsedResponse);
        } else {
          setChannels([]);
        }
      } catch (e) {
        console.error("Failed to parse channels response", e);
        setChannels([]);
      }
    } catch (error) {
      console.error("Failed to fetch channels", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const checkStatus = useCallback(async (username: string) => {
    try {
      const res = await fetch(`http://localhost:8000/auth/slack/status?username=${username}`);
      const data = await res.json();
      setConnected(data.connected);
      if (data.connected) {
        fetchChannels(username);
      }
    } catch (error) {
      console.error("Failed to check status", error);
    } finally {
      setLoading(false);
    }
  }, [fetchChannels]);

  useEffect(() => {
    const user = getUsernameFromStoredAuth();
    if (user) {
      checkStatus(user);
    }
  }, [checkStatus]);

  const fetchHistory = async (channelId: string) => {
    const user = getUsernameFromStoredAuth();
    if (!user) return;
    setLoading(true);
    
    try {
      const res = await fetch("http://localhost:8000/mcp/slack/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: user,
          tool_name: "get_channel_history",
          arguments: { channel_id: channelId }
        })
      });
      const data = await res.json();
      try {
        if (typeof data.response === 'string' && data.response.startsWith('Error')) {
          console.error("MCP Error:", data.response);
          setMessages([]);
          return;
        }

        const parsedResponse = JSON.parse(data.response);
        if (Array.isArray(parsedResponse)) {
          setMessages(parsedResponse);
        } else {
          setMessages([]);
        }
      } catch (e) {
        console.error("Failed to parse messages response", e);
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to fetch messages", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    const user = getUsernameFromStoredAuth();
    try {
      const res = await fetch(`http://localhost:8000/auth/slack/login?username=${user}`);
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error("Failed to initiate Slack login", error);
    }
  };

  const handleDisconnect = async () => {
    const user = getUsernameFromStoredAuth();
    try {
      await fetch(`http://localhost:8000/auth/slack/disconnect?username=${user}`, {
        method: "DELETE",
      });
      setConnected(false);
      setChannels([]);
      setMessages([]);
      setSelectedChannel(null);
    } catch (error) {
      console.error("Failed to disconnect", error);
    }
  };

  const handleChannelClick = (channel: Channel) => {
    setSelectedChannel(channel);
    fetchHistory(channel.id);
  };

  const handleBackToChannels = () => {
    setSelectedChannel(null);
    setMessages([]);
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Connection Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 mb-8 flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-purple-50 rounded-full mb-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="https://www.svgrepo.com/show/448248/slack.svg" alt="Slack" className="w-12 h-12" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Slack</h1>
        
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
            className="w-64 px-4 py-2 text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors shadow-sm"
          >
            Connect
          </button>
        )}
      </div>

      {connected && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          {/* Toolbar */}
          <div className="p-4 border-b border-gray-200 bg-gray-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {selectedChannel ? (
              <div className="flex items-center gap-4">
                <button 
                  onClick={handleBackToChannels}
                  className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                >
                  ← Back to Channels
                </button>
                <span className="text-sm font-semibold text-gray-900">#{selectedChannel.name}</span>
              </div>
            ) : (
              <div className="text-sm font-semibold text-gray-900">Channels</div>
            )}
          </div>

          {/* Content Area */}
          <div className="min-h-[400px] relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center bg-white/50 z-10">
                <div className="flex flex-col items-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                  <p className="text-sm text-gray-500">Loading...</p>
                </div>
              </div>
            ) : null}

            {!selectedChannel ? (
              channels.length === 0 && !loading ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
                  <div className="text-4xl mb-4">💬</div>
                  <p className="text-lg font-medium text-gray-900">No channels found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-gray-100 bg-gray-50/50">
                        <th className="px-6 py-3 font-medium text-gray-500">Name</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Members</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Topic</th>
                        <th className="px-6 py-3 font-medium text-gray-500">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {channels.map((channel) => (
                        <tr key={channel.id} className="group hover:bg-purple-50/50 transition-colors">
                          <td className="px-6 py-3">
                            <div className="flex items-center gap-2 font-medium text-gray-900">
                              <span className="text-gray-400">#</span>
                              {channel.name}
                            </div>
                          </td>
                          <td className="px-6 py-3 text-gray-500">
                            {channel.num_members}
                          </td>
                          <td className="px-6 py-3 text-gray-500 max-w-xs truncate">
                            {channel.topic || '-'}
                          </td>
                          <td className="px-6 py-3">
                            <button
                              onClick={() => handleChannelClick(channel)}
                              className="text-purple-600 hover:text-purple-800 font-medium"
                            >
                              View History
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            ) : (
              // Messages View
              messages.length === 0 && !loading ? (
                <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
                  <div className="text-4xl mb-4">📭</div>
                  <p className="text-lg font-medium text-gray-900">No messages found</p>
                </div>
              ) : (
                <div className="flex flex-col p-4 space-y-4">
                  {messages.map((msg) => (
                    <div key={msg.ts} className="flex gap-3 p-3 rounded-lg hover:bg-gray-50">
                      <div className="flex-shrink-0 w-10 h-10 bg-gray-200 rounded-md flex items-center justify-center text-gray-500 font-bold">
                        {msg.user ? msg.user.substring(0, 2).toUpperCase() : '?'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-gray-900">{msg.user || 'Unknown User'}</span>
                          <span className="text-xs text-gray-500">
                            {new Date(parseFloat(msg.ts) * 1000).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-gray-800 whitespace-pre-wrap break-words">{msg.text}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
