import { useState, useEffect, useRef, useCallback } from "react";
import clsx from "clsx";
import { CollabMessage } from "./CollabMessage";
import { CollabInput } from "./CollabInput";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Mention {
  users: string[];
  assets: string[];
}

interface Attachment {
  filename: string;
  type: string;
  size?: number;
}

interface Message {
  id: string;
  channel_id: string;
  incident_id?: string;
  user: string;
  content: string;
  message_type: string;
  mentions: Mention;
  attachments: Attachment[];
  reactions: Record<string, string[]>;
  thread_id?: string;
  is_edited: boolean;
  created_at: string;
}

interface Channel {
  id: string;
  name: string;
  description?: string;
  incident_id?: string;
  channel_type: string;
}

interface CollabChatProps {
  incidentId?: string;
  channelId?: string;
  currentUser?: string;
  compact?: boolean;
  className?: string;
}

export function CollabChat({
  incidentId,
  channelId: propChannelId,
  currentUser = "soc-analyst",
  compact = false,
  className,
}: CollabChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [activeChannel, setActiveChannel] = useState<string>(propChannelId || "general");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyingTo, setReplyingTo] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState("");
  const [showSearch, setShowSearch] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Fetch channels
  const fetchChannels = useCallback(async () => {
    try {
      const url = incidentId
        ? `${API_BASE}/collab/channels?incident_id=${incidentId}`
        : `${API_BASE}/collab/channels`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setChannels(data);
        // Set active channel if incident-specific
        if (incidentId && data.length > 0) {
          setActiveChannel(data[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to fetch channels:", err);
    }
  }, [incidentId]);

  // Fetch messages
  const fetchMessages = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (incidentId) params.append("incident_id", incidentId);
      if (activeChannel) params.append("channel_id", activeChannel);
      params.append("limit", "100");

      const response = await fetch(`${API_BASE}/collab/messages?${params}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.data || []);
        setError(null);
      } else {
        setError("Failed to load messages");
      }
    } catch (err) {
      setError("Failed to connect to server");
      console.error("Failed to fetch messages:", err);
    } finally {
      setLoading(false);
    }
  }, [incidentId, activeChannel]);

  // Setup WebSocket connection
  useEffect(() => {
    const wsUrl = `${API_BASE.replace("http", "ws")}/collab/ws/${activeChannel}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "message_created") {
          setMessages((prev) => [...prev, data.data]);
        } else if (data.type === "message_deleted") {
          setMessages((prev) => prev.filter((m) => m.id !== data.data.message_id));
        } else if (data.type === "reaction_added" || data.type === "reaction_removed") {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === data.data.message_id ? { ...m, reactions: data.data.reactions } : m,
            ),
          );
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [activeChannel]);

  // Fetch data on mount and channel change
  useEffect(() => {
    fetchChannels();
  }, [fetchChannels]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Send message
  const handleSend = async (content: string, attachments?: File[]) => {
    try {
      const attachmentData = attachments?.map((f) => ({
        filename: f.name,
        type: f.type.startsWith("image/") ? "image" : "file",
        size: f.size,
      }));

      const response = await fetch(`${API_BASE}/collab/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content,
          user: currentUser,
          incident_id: incidentId,
          channel_id: activeChannel,
          attachments: attachmentData,
          thread_id: replyingTo,
        }),
      });

      if (response.ok) {
        setReplyingTo(undefined);
        // Message will be added via WebSocket
      }
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  // Add reaction
  const handleReact = async (messageId: string, emoji: string) => {
    try {
      await fetch(`${API_BASE}/collab/messages/${messageId}/reactions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emoji, user: currentUser }),
      });
      // Reaction will be updated via WebSocket
    } catch (err) {
      console.error("Failed to add reaction:", err);
    }
  };

  // Delete message
  const handleDelete = async (messageId: string) => {
    if (!confirm("Are you sure you want to delete this message?")) return;

    try {
      await fetch(`${API_BASE}/collab/messages/${messageId}?deleted_by=${currentUser}`, {
        method: "DELETE",
      });
      // Message will be removed via WebSocket
    } catch (err) {
      console.error("Failed to delete message:", err);
    }
  };

  // Search messages
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      fetchMessages();
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/collab/messages/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          incident_id: incidentId,
          channel_id: activeChannel,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.results || []);
      }
    } catch (err) {
      console.error("Failed to search messages:", err);
    }
  };

  if (compact) {
    return (
      <div className={clsx("flex flex-col bg-primary rounded-lg overflow-hidden", className)}>
        {/* Compact header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-primary">
          <div className="flex items-center gap-2">
            <svg
              className="w-4 h-4 text-cyan-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <span className="text-sm font-medium text-primary">Team Chat</span>
          </div>
          <div
            className={clsx("w-2 h-2 rounded-full", wsConnected ? "bg-green-500" : "bg-red-500")}
            title={wsConnected ? "Connected" : "Disconnected"}
          />
        </div>

        {/* Messages (compact) */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1 max-h-64">
          {messages.slice(-5).map((message) => (
            <div key={message.id} className="text-sm">
              <span className="font-medium text-cyan-400">{message.user}:</span>{" "}
              <span className="text-secondary">{message.content}</span>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Compact input */}
        <div className="border-t border-primary p-2">
          <CollabInput onSend={handleSend} placeholder="Quick message..." />
        </div>
      </div>
    );
  }

  return (
    <div className={clsx("flex flex-col bg-primary h-full", className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-primary">
        <div className="flex items-center gap-3">
          <svg
            className="w-5 h-5 text-cyan-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <div>
            <h2 className="font-semibold text-primary">
              {channels.find((c) => c.id === activeChannel)?.name || "Collaboration"}
            </h2>
            {incidentId && <p className="text-xs text-tertiary">Incident: {incidentId}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Connection status */}
          <div
            className={clsx(
              "flex items-center gap-1 px-2 py-1 rounded text-xs",
              wsConnected ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400",
            )}
          >
            <div
              className={clsx("w-2 h-2 rounded-full", wsConnected ? "bg-green-500" : "bg-red-500")}
            />
            {wsConnected ? "Live" : "Offline"}
          </div>

          {/* Search toggle */}
          <button
            onClick={() => setShowSearch(!showSearch)}
            className={clsx(
              "p-2 rounded transition-colors",
              showSearch
                ? "bg-tertiary text-cyan-400"
                : "text-secondary hover:text-primary hover:bg-secondary",
            )}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </button>

          {/* Channel selector */}
          {channels.length > 1 && (
            <select
              value={activeChannel}
              onChange={(e) => setActiveChannel(e.target.value)}
              className="bg-secondary text-primary text-sm rounded px-2 py-1 border border-primary"
            >
              {channels.map((channel) => (
                <option key={channel.id} value={channel.id}>
                  {channel.name}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Search bar */}
      {showSearch && (
        <div className="px-4 py-2 border-b border-primary flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search messages..."
            className="flex-1 bg-secondary text-primary px-3 py-2 rounded border border-primary focus:border-cyan-500 focus:outline-none"
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-cyan-600 text-primary rounded hover:bg-cyan-700 transition-colors"
          >
            Search
          </button>
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery("");
                fetchMessages();
              }}
              className="px-4 py-2 bg-tertiary text-secondary rounded hover:bg-tertiary transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-2">
        {loading ? (
          <div className="flex items-center justify-center h-full text-tertiary">
            <svg className="animate-spin w-6 h-6 mr-2" fill="none" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Loading messages...
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full text-tertiary">
            <svg
              className="w-12 h-12 mb-2 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p>{error}</p>
            <button onClick={fetchMessages} className="mt-2 text-cyan-400 hover:text-cyan-300">
              Retry
            </button>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-tertiary">
            <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p>No messages yet</p>
            <p className="text-sm">Start the conversation!</p>
          </div>
        ) : (
          <div className="py-2">
            {messages.map((message) => (
              <CollabMessage
                key={message.id}
                message={message}
                currentUser={currentUser}
                onReact={handleReact}
                onDelete={handleDelete}
                onReply={(id) => setReplyingTo(id)}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <CollabInput
        onSend={handleSend}
        replyingTo={replyingTo}
        onCancelReply={() => setReplyingTo(undefined)}
        disabled={!wsConnected}
      />
    </div>
  );
}
