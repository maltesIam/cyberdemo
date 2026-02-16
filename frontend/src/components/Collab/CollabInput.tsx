import {
  useState,
  useRef,
  useCallback,
  useEffect,
  type KeyboardEvent,
  type ChangeEvent,
} from "react";
import clsx from "clsx";

interface Suggestion {
  type: "user" | "asset";
  value: string;
  label: string;
}

interface CollabInputProps {
  onSend: (content: string, attachments?: File[]) => void;
  onTyping?: () => void;
  placeholder?: string;
  disabled?: boolean;
  replyingTo?: string;
  onCancelReply?: () => void;
}

// Mock data for autocomplete suggestions
const MOCK_USERS = [
  { value: "john", label: "John Smith" },
  { value: "jane", label: "Jane Doe" },
  { value: "analyst1", label: "SOC Analyst 1" },
  { value: "analyst2", label: "SOC Analyst 2" },
  { value: "lead", label: "Team Lead" },
];

const MOCK_ASSETS = [
  { value: "ASSET-001", label: "ASSET-001 (Web Server)" },
  { value: "ASSET-002", label: "ASSET-002 (Database)" },
  { value: "HOST-PROD-WEB-01", label: "HOST-PROD-WEB-01" },
  { value: "HOST-DEV-01", label: "HOST-DEV-01" },
];

export function CollabInput({
  onSend,
  onTyping,
  placeholder = "Type a message...",
  disabled = false,
  replyingTo,
  onCancelReply,
}: CollabInputProps) {
  const [content, setContent] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
  const [mentionStart, setMentionStart] = useState<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  // Handle mention autocomplete
  const updateSuggestions = useCallback((text: string, cursorPos: number) => {
    // Find @ symbol before cursor
    const textBeforeCursor = text.substring(0, cursorPos);
    const mentionMatch = textBeforeCursor.match(/@(\w*)$/);

    if (mentionMatch) {
      const query = mentionMatch[1].toLowerCase();
      const start = cursorPos - mentionMatch[0].length;
      setMentionStart(start);

      // Filter suggestions
      const userSuggestions: Suggestion[] = MOCK_USERS.filter(
        (u) => u.value.toLowerCase().includes(query) || u.label.toLowerCase().includes(query),
      ).map((u) => ({ type: "user", value: u.value, label: u.label }));

      const assetSuggestions: Suggestion[] = MOCK_ASSETS.filter(
        (a) => a.value.toLowerCase().includes(query) || a.label.toLowerCase().includes(query),
      ).map((a) => ({ type: "asset", value: a.value, label: a.label }));

      setSuggestions([...userSuggestions, ...assetSuggestions].slice(0, 8));
      setSelectedSuggestion(0);
    } else {
      setSuggestions([]);
      setMentionStart(null);
    }
  }, []);

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value;
    setContent(newContent);
    updateSuggestions(newContent, e.target.selectionStart || 0);
    onTyping?.();
  };

  const insertMention = useCallback(
    (suggestion: Suggestion) => {
      if (mentionStart === null) return;

      const before = content.substring(0, mentionStart);
      const after = content.substring(textareaRef.current?.selectionStart || content.length);
      const newContent = `${before}@${suggestion.value} ${after}`;

      setContent(newContent);
      setSuggestions([]);
      setMentionStart(null);

      // Focus and move cursor
      setTimeout(() => {
        if (textareaRef.current) {
          const newPos = mentionStart + suggestion.value.length + 2;
          textareaRef.current.focus();
          textareaRef.current.setSelectionRange(newPos, newPos);
        }
      }, 0);
    },
    [content, mentionStart],
  );

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle suggestions navigation
    if (suggestions.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedSuggestion((prev) => (prev + 1) % suggestions.length);
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedSuggestion((prev) => (prev - 1 + suggestions.length) % suggestions.length);
        return;
      }
      if (e.key === "Tab" || e.key === "Enter") {
        e.preventDefault();
        insertMention(suggestions[selectedSuggestion]);
        return;
      }
      if (e.key === "Escape") {
        setSuggestions([]);
        return;
      }
    }

    // Send on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmedContent = content.trim();
    if (!trimmedContent && attachments.length === 0) return;

    onSend(trimmedContent, attachments.length > 0 ? attachments : undefined);
    setContent("");
    setAttachments([]);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setAttachments((prev) => [...prev, ...files]);
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="border-t border-gray-700 p-4">
      {/* Reply indicator */}
      {replyingTo && (
        <div className="flex items-center justify-between bg-gray-800/50 px-3 py-2 rounded-t-lg mb-1">
          <span className="text-sm text-gray-400">
            Replying to message <span className="text-cyan-400">{replyingTo}</span>
          </span>
          <button onClick={onCancelReply} className="text-gray-500 hover:text-white">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      )}

      {/* Attachments preview */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-gray-700/50 px-3 py-2 rounded-lg group"
            >
              <svg
                className="w-4 h-4 text-gray-400"
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
              <span className="text-sm text-gray-300 max-w-[150px] truncate">{file.name}</span>
              <span className="text-xs text-gray-500">({Math.round(file.size / 1024)}KB)</span>
              <button
                onClick={() => removeAttachment(index)}
                className="text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input area */}
      <div className="relative">
        <div className="flex items-end gap-2 bg-gray-800 rounded-lg border border-gray-700 focus-within:border-cyan-500 transition-colors">
          {/* Attachment button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            className="p-3 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
            title="Attach file"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
              />
            </svg>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileSelect}
            className="hidden"
            accept=".txt,.log,.json,.csv,.png,.jpg,.jpeg,.gif,.pdf,.pcap"
          />

          {/* Text input */}
          <textarea
            ref={textareaRef}
            value={content}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="flex-1 bg-transparent text-gray-200 placeholder-gray-500 py-3 resize-none focus:outline-none disabled:opacity-50"
          />

          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={disabled || (!content.trim() && attachments.length === 0)}
            className={clsx(
              "p-3 rounded-r-lg transition-colors",
              content.trim() || attachments.length > 0
                ? "text-cyan-400 hover:text-cyan-300"
                : "text-gray-600 cursor-not-allowed",
            )}
            title="Send message"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>

        {/* Autocomplete suggestions */}
        {suggestions.length > 0 && (
          <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-800 border border-gray-700 rounded-lg shadow-lg overflow-hidden z-10">
            {suggestions.map((suggestion, index) => (
              <button
                key={`${suggestion.type}-${suggestion.value}`}
                onClick={() => insertMention(suggestion)}
                className={clsx(
                  "w-full flex items-center gap-3 px-3 py-2 text-left transition-colors",
                  index === selectedSuggestion ? "bg-gray-700" : "hover:bg-gray-700/50",
                )}
              >
                <div
                  className={clsx(
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs",
                    suggestion.type === "user"
                      ? "bg-cyan-500/20 text-cyan-400"
                      : "bg-yellow-500/20 text-yellow-400",
                  )}
                >
                  {suggestion.type === "user" ? (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  ) : (
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                  )}
                </div>
                <div>
                  <div className="text-gray-200 font-medium">@{suggestion.value}</div>
                  <div className="text-gray-500 text-sm">{suggestion.label}</div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Help text */}
      <div className="mt-2 text-xs text-gray-500 flex items-center gap-4">
        <span>
          <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-400">@</kbd> to mention
        </span>
        <span>
          <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-400">Enter</kbd> to send
        </span>
        <span>
          <kbd className="px-1 py-0.5 bg-gray-700 rounded text-gray-400">Shift + Enter</kbd> for new
          line
        </span>
      </div>
    </div>
  );
}
