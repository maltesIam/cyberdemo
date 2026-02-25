/**
 * GraphControls Component
 *
 * Control buttons for graph manipulation:
 * - Zoom in/out
 * - Fit to screen
 * - Auto layout
 */

interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitToScreen: () => void;
  onAutoLayout: () => void;
  className?: string;
}

export function GraphControls({
  onZoomIn,
  onZoomOut,
  onFitToScreen,
  onAutoLayout,
  className = "",
}: GraphControlsProps) {
  const buttonClass = "p-2 bg-slate-700 hover:bg-slate-600 text-primary rounded-md transition-colors";

  return (
    <div
      className={`flex gap-2 p-2 bg-slate-800 rounded-lg ${className}`}
      role="toolbar"
      aria-label="Graph controls"
    >
      <button
        data-testid="zoom-in-btn"
        onClick={onZoomIn}
        className={buttonClass}
        title="Zoom In"
        aria-label="Zoom in"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      <button
        data-testid="zoom-out-btn"
        onClick={onZoomOut}
        className={buttonClass}
        title="Zoom Out"
        aria-label="Zoom out"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      <div className="w-px bg-slate-600" />

      <button
        data-testid="fit-screen-btn"
        onClick={onFitToScreen}
        className={buttonClass}
        title="Fit to Screen"
        aria-label="Fit to screen"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M3 4a1 1 0 011-1h4a1 1 0 010 2H5v3a1 1 0 01-2 0V4zm0 12a1 1 0 001 1h4a1 1 0 010-2H5v-3a1 1 0 00-2 0v4zm14-12a1 1 0 00-1-1h-4a1 1 0 000 2h3v3a1 1 0 002 0V4zm0 12a1 1 0 01-1 1h-4a1 1 0 010-2h3v-3a1 1 0 012 0v4z" />
        </svg>
      </button>

      <button
        data-testid="auto-layout-btn"
        onClick={onAutoLayout}
        className={buttonClass}
        title="Auto Layout"
        aria-label="Auto layout"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      </button>
    </div>
  );
}
