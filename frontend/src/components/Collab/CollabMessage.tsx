import { useState } from "react";
import clsx from "clsx";

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

interface CollabMessageProps {
  message: Message;
  currentUser?: string;
  onReact?: (messageId: string, emoji: string) => void;
  onDelete?: (messageId: string) => void;
  onReply?: (messageId: string) => void;
}

const QUICK_REACTIONS = ["thumbsup", "heart", "eyes", "check", "warning"];

const EMOJI_MAP: Record<string, string> = {
  thumbsup: "\u{1F44D}",
  heart: "\u{2764}\u{FE0F}",
  eyes: "\u{1F440}",
  check: "\u{2705}",
  warning: "\u{26A0}\u{FE0F}",
  fire: "\u{1F525}",
  rocket: "\u{1F680}",
};

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function highlightMentions(content: string): JSX.Element {
  // Split by @mentions and highlight them
  const parts = content.split(/(@\w+|@[A-Z]+-[A-Z0-9-]+)/g);

  return (
    <>
      {parts.map((part, index) => {
        if (part.startsWith("@")) {
          return (
            <span
              key={index}
              className="bg-cyan-500/20 text-cyan-300 px-1 rounded font-medium cursor-pointer hover:bg-cyan-500/30"
            >
              {part}
            </span>
          );
        }
        return <span key={index}>{part}</span>;
      })}
    </>
  );
}

function getUserColor(user: string): string {
  // Generate consistent color based on username
  const colors = [
    "from-cyan-500 to-blue-500",
    "from-purple-500 to-pink-500",
    "from-green-500 to-teal-500",
    "from-orange-500 to-red-500",
    "from-yellow-500 to-orange-500",
  ];
  const hash = user.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

export function CollabMessage({
  message,
  currentUser = "soc-analyst",
  onReact,
  onDelete,
  onReply,
}: CollabMessageProps) {
  const [showReactions, setShowReactions] = useState(false);
  const isOwnMessage = message.user === currentUser;
  const isSystemMessage = message.message_type === "system";
  const isActionMessage = message.message_type === "action";

  if (isSystemMessage) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-tertiary/50 text-secondary text-sm px-4 py-1 rounded-full">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={clsx("group flex gap-3 p-3 rounded-lg hover:bg-secondary/50 transition-colors", {
        "bg-cyan-900/20 border-l-2 border-cyan-500": isActionMessage,
      })}
      onMouseEnter={() => setShowReactions(true)}
      onMouseLeave={() => setShowReactions(false)}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center text-primary font-medium text-sm bg-gradient-to-br",
          getUserColor(message.user),
        )}
      >
        {message.user.charAt(0).toUpperCase()}
      </div>

      {/* Message content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-primary">{message.user}</span>
          {isActionMessage && (
            <span className="bg-cyan-500/20 text-cyan-300 text-xs px-2 py-0.5 rounded">ACTION</span>
          )}
          {message.message_type === "evidence" && (
            <span className="bg-yellow-500/20 text-yellow-300 text-xs px-2 py-0.5 rounded">
              EVIDENCE
            </span>
          )}
          <span className="text-tertiary text-sm">{formatTimestamp(message.created_at)}</span>
          {message.is_edited && <span className="text-tertiary text-xs">(edited)</span>}
        </div>

        {/* Content */}
        <div className="text-secondary break-words">{highlightMentions(message.content)}</div>

        {/* Attachments */}
        {message.attachments.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {message.attachments.map((attachment, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-tertiary/50 px-3 py-2 rounded-lg"
              >
                <svg
                  className="w-4 h-4 text-secondary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
                  />
                </svg>
                <span className="text-sm text-secondary">{attachment.filename}</span>
                {attachment.size && (
                  <span className="text-xs text-tertiary">
                    ({Math.round(attachment.size / 1024)}KB)
                  </span>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Reactions */}
        {Object.keys(message.reactions).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {Object.entries(message.reactions).map(([emoji, users]) => (
              <button
                key={emoji}
                onClick={() => onReact?.(message.id, emoji)}
                className={clsx(
                  "flex items-center gap-1 px-2 py-0.5 rounded-full text-sm transition-colors",
                  users.includes(currentUser)
                    ? "bg-cyan-500/30 text-cyan-300"
                    : "bg-tertiary/50 text-secondary hover:bg-tertiary",
                )}
              >
                <span>{EMOJI_MAP[emoji] || emoji}</span>
                <span>{users.length}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div
        className={clsx(
          "flex items-start gap-1 transition-opacity",
          showReactions ? "opacity-100" : "opacity-0",
        )}
      >
        {/* Quick reactions */}
        <div className="flex items-center bg-secondary rounded-lg border border-primary overflow-hidden">
          {QUICK_REACTIONS.map((emoji) => (
            <button
              key={emoji}
              onClick={() => onReact?.(message.id, emoji)}
              className="p-1.5 hover:bg-tertiary transition-colors"
              title={emoji}
            >
              <span className="text-sm">{EMOJI_MAP[emoji]}</span>
            </button>
          ))}
        </div>

        {/* More actions */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => onReply?.(message.id)}
            className="p-1.5 text-secondary hover:text-primary hover:bg-tertiary rounded transition-colors"
            title="Reply"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
              />
            </svg>
          </button>

          {isOwnMessage && (
            <button
              onClick={() => onDelete?.(message.id)}
              className="p-1.5 text-secondary hover:text-red-400 hover:bg-tertiary rounded transition-colors"
              title="Delete"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
