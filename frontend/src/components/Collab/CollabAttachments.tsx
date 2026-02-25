import clsx from "clsx";

interface Attachment {
  filename: string;
  type: string;
  size?: number;
  url?: string;
  mime_type?: string;
}

interface CollabAttachmentsProps {
  attachments: Attachment[];
  onPreview?: (attachment: Attachment) => void;
  onDownload?: (attachment: Attachment) => void;
  compact?: boolean;
}

const FILE_TYPE_ICONS: Record<string, JSX.Element> = {
  image: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
      />
    </svg>
  ),
  log: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
      />
    </svg>
  ),
  pcap: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
      />
    </svg>
  ),
  screenshot: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  ),
  file: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
      />
    </svg>
  ),
};

const TYPE_COLORS: Record<string, string> = {
  image: "bg-green-500/20 text-green-400",
  screenshot: "bg-green-500/20 text-green-400",
  log: "bg-blue-500/20 text-blue-400",
  pcap: "bg-purple-500/20 text-purple-400",
  file: "bg-gray-500/20 text-secondary",
};

function formatFileSize(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileExtension(filename: string): string {
  const parts = filename.split(".");
  return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : "";
}

export function CollabAttachments({
  attachments,
  onPreview,
  onDownload,
  compact = false,
}: CollabAttachmentsProps) {
  if (attachments.length === 0) return null;

  if (compact) {
    return (
      <div className="flex flex-wrap gap-1">
        {attachments.map((attachment, index) => (
          <button
            key={index}
            onClick={() => onPreview?.(attachment)}
            className="flex items-center gap-1 bg-tertiary/50 px-2 py-1 rounded text-sm hover:bg-tertiary transition-colors"
          >
            <span className={TYPE_COLORS[attachment.type] || TYPE_COLORS.file}>
              {FILE_TYPE_ICONS[attachment.type] || FILE_TYPE_ICONS.file}
            </span>
            <span className="text-secondary max-w-[100px] truncate">{attachment.filename}</span>
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {attachments.map((attachment, index) => (
        <div
          key={index}
          className="flex items-center gap-3 bg-secondary/50 border border-primary rounded-lg p-3 group hover:border-primary transition-colors"
        >
          {/* File icon */}
          <div
            className={clsx(
              "w-10 h-10 rounded-lg flex items-center justify-center",
              TYPE_COLORS[attachment.type] || TYPE_COLORS.file,
            )}
          >
            {FILE_TYPE_ICONS[attachment.type] || FILE_TYPE_ICONS.file}
          </div>

          {/* File info */}
          <div className="flex-1 min-w-0">
            <div className="text-primary font-medium truncate">{attachment.filename}</div>
            <div className="text-tertiary text-sm flex items-center gap-2">
              <span className="uppercase">{getFileExtension(attachment.filename)}</span>
              {attachment.size && (
                <>
                  <span>|</span>
                  <span>{formatFileSize(attachment.size)}</span>
                </>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {(attachment.type === "image" || attachment.type === "screenshot") && (
              <button
                onClick={() => onPreview?.(attachment)}
                className="p-2 text-secondary hover:text-primary hover:bg-tertiary rounded transition-colors"
                title="Preview"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            )}
            <button
              onClick={() => onDownload?.(attachment)}
              className="p-2 text-secondary hover:text-primary hover:bg-tertiary rounded transition-colors"
              title="Download"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// Image preview modal component
interface ImagePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  attachment: Attachment | null;
}

export function ImagePreviewModal({ isOpen, onClose, attachment }: ImagePreviewModalProps) {
  if (!isOpen || !attachment) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      onClick={onClose}
    >
      <div className="relative max-w-4xl max-h-[90vh] p-4" onClick={(e) => e.stopPropagation()}>
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-2 right-2 p-2 bg-secondary rounded-full text-primary hover:bg-tertiary transition-colors z-10"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Image */}
        {attachment.url ? (
          <img
            src={attachment.url}
            alt={attachment.filename}
            className="max-w-full max-h-[80vh] object-contain rounded-lg"
          />
        ) : (
          <div className="bg-secondary rounded-lg p-8 text-center">
            <div className="text-secondary mb-2">Preview not available</div>
            <div className="text-tertiary text-sm">{attachment.filename}</div>
          </div>
        )}

        {/* File info */}
        <div className="mt-2 text-center text-secondary text-sm">
          {attachment.filename}
          {attachment.size && <span className="ml-2">({formatFileSize(attachment.size)})</span>}
        </div>
      </div>
    </div>
  );
}
