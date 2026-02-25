/**
 * FilesManagerPage - Renders the Files Manager UI preview
 * with SoulBot branding, ThemeToggle, and FontSizeButton.
 */
import { ThemeToggle } from "../components/ThemeToggle";
import { FontSizeButton } from "../components/FontSizeButton";

const MOCK_FILES = [
  { name: "project-config.yaml", size: "2.4 KB" },
  { name: "deployment-log.json", size: "156 KB" },
  { name: "threat-rules.sigma", size: "8.1 KB" },
  { name: "incident-report.pdf", size: "1.2 MB" },
  { name: "network-capture.pcap", size: "45 MB" },
];

export function FilesManagerPage() {
  return (
    <div style={{ backgroundColor: "var(--bg-primary)", minHeight: "100%" }}>
      {/* Header with branding and controls */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{
          backgroundColor: "var(--bg-secondary)",
          borderBottom: "1px solid var(--border-primary)",
        }}
      >
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-md">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
          </div>
          <h2 className="text-lg tracking-tight" style={{ fontWeight: 800 }}>
            <span className="text-primary">Soul</span>
            <span style={{ color: "var(--primary)" }}>Bot</span>
            <span className="text-secondary text-sm font-normal ml-2">Files Manager</span>
          </h2>
        </div>
        <div className="flex items-center space-x-3">
          <FontSizeButton />
          <ThemeToggle />
        </div>
      </div>

      {/* Toolbar */}
      <div
        className="flex items-center justify-between px-4 py-2"
        style={{
          backgroundColor: "var(--bg-secondary)",
          borderBottom: "1px solid var(--border-primary)",
        }}
      >
        <input
          type="text"
          placeholder="Search files..."
          className="rounded-md px-3 py-1 text-sm"
          style={{
            background: "var(--bg-input)",
            color: "var(--text-primary)",
            border: "1px solid var(--border-primary)",
            fontFamily: "var(--font-family-sans)",
          }}
        />
      </div>

      {/* File list */}
      <div className="p-6">
        <h2 className="text-lg font-semibold text-primary mb-4">File Browser</h2>
        <div className="space-y-2">
          {MOCK_FILES.map((file) => (
            <div
              key={file.name}
              className="flex items-center justify-between px-4 py-3 rounded-lg"
              style={{
                backgroundColor: "var(--bg-secondary)",
                border: "1px solid var(--border-primary)",
              }}
            >
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5" style={{ color: "var(--text-tertiary)" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-primary font-medium">{file.name}</span>
              </div>
              <span className="text-sm" style={{ color: "var(--text-tertiary)" }}>{file.size}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
