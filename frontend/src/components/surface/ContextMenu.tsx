/**
 * ContextMenu - Right-click context menu for asset nodes
 *
 * Provides quick actions: Investigate, Contain, Create Ticket,
 * Copy Asset ID, Export Report, and navigation links.
 * Closes on click outside or Escape key.
 */

import { useEffect, useRef, useCallback } from "react";
import clsx from "clsx";

// ============================================================================
// Types
// ============================================================================

interface Props {
  x: number;
  y: number;
  node: any;
  onAction: (action: string) => void;
  onClose: () => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: JSX.Element;
  separator?: false;
}

interface MenuSeparator {
  separator: true;
}

type MenuEntry = MenuItem | MenuSeparator;

// ============================================================================
// Constants
// ============================================================================

const MENU_ITEMS: MenuEntry[] = [
  {
    id: "investigate",
    label: "Investigate",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    ),
  },
  {
    id: "contain",
    label: "Contain / Lift Containment",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
    ),
  },
  {
    id: "create_ticket",
    label: "Create Ticket",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
        />
      </svg>
    ),
  },
  {
    id: "copy_id",
    label: "Copy Asset ID",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
        />
      </svg>
    ),
  },
  {
    id: "export_report",
    label: "Export Report",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
        />
      </svg>
    ),
  },
  { separator: true },
  {
    id: "view_assets",
    label: "View in Assets page",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
        />
      </svg>
    ),
  },
  {
    id: "view_detections",
    label: "View Detections",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
        />
      </svg>
    ),
  },
];

// ============================================================================
// Main Component
// ============================================================================

export function ContextMenu({ x, y, node, onAction, onClose }: Props) {
  const menuRef = useRef<HTMLDivElement>(null);

  // Adjust position to keep menu within viewport
  const adjustedPosition = useCallback(() => {
    const menuWidth = 220;
    const menuHeight = MENU_ITEMS.length * 36 + 16; // Approximate
    const viewportW = window.innerWidth;
    const viewportH = window.innerHeight;

    let adjX = x;
    let adjY = y;

    if (x + menuWidth > viewportW) adjX = viewportW - menuWidth - 8;
    if (y + menuHeight > viewportH) adjY = viewportH - menuHeight - 8;
    if (adjX < 0) adjX = 8;
    if (adjY < 0) adjY = 8;

    return { x: adjX, y: adjY };
  }, [x, y]);

  const pos = adjustedPosition();

  // Close on Escape
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  // Close on click outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    // Use a small delay to avoid the opening right-click from immediately closing
    const timer = setTimeout(() => {
      document.addEventListener("mousedown", handleClick);
    }, 50);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handleClick);
    };
  }, [onClose]);

  const handleAction = useCallback(
    (actionId: string) => {
      if (actionId === "copy_id") {
        const id = node?.id ?? node?.hostname ?? "";
        navigator.clipboard?.writeText?.(id).catch(() => {
          // Clipboard API not available, silent fail
        });
      }
      onAction(actionId);
      onClose();
    },
    [node, onAction, onClose],
  );

  const hostname = node?.hostname ?? "Unknown Asset";
  const isContained = node?.layers?.containment?.isContained ?? false;

  return (
    <div
      ref={menuRef}
      className="fixed z-[100] bg-secondary border border-primary rounded-lg shadow-2xl py-1.5 min-w-[200px] animate-context-menu-in"
      style={{ left: pos.x, top: pos.y }}
    >
      {/* Header with asset info */}
      <div className="px-3 py-2 border-b border-primary mb-1">
        <div className="text-sm text-primary font-medium truncate">{hostname}</div>
        <div className="text-[10px] text-tertiary font-mono">{node?.ip ?? "N/A"}</div>
      </div>

      {/* Menu items */}
      {MENU_ITEMS.map((entry, idx) => {
        if ("separator" in entry && entry.separator) {
          return <div key={`sep-${idx}`} className="my-1 border-t border-primary" />;
        }

        const item = entry as MenuItem;

        // Dynamic label for contain action based on current state
        const label =
          item.id === "contain" ? (isContained ? "Lift Containment" : "Contain") : item.label;

        return (
          <button
            key={item.id}
            onClick={() => handleAction(item.id)}
            className={clsx(
              "w-full flex items-center gap-2.5 px-3 py-1.5 text-sm text-secondary transition-colors",
              "hover:bg-tertiary hover:text-primary",
              item.id === "contain" && isContained && "hover:bg-blue-900/30 hover:text-blue-300",
              item.id === "contain" &&
                !isContained &&
                "hover:bg-orange-900/30 hover:text-orange-300",
            )}
          >
            <span className="text-tertiary flex-shrink-0">{item.icon}</span>
            <span className="truncate">{label}</span>
          </button>
        );
      })}

      {/* Inline CSS for context menu animation */}
      <style>{`
        @keyframes contextMenuIn {
          from {
            opacity: 0;
            transform: scale(0.95) translateY(-4px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        .animate-context-menu-in {
          animation: contextMenuIn 0.12s ease-out;
        }
      `}</style>
    </div>
  );
}
