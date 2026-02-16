import { useState } from "react";
import { useNavigate } from "react-router-dom";
import clsx from "clsx";
import {
  useGenerationStatus,
  useGenerateAll,
  useGenerateAssets,
  useGenerateEDR,
  useGenerateIncidents,
  useGeneratePostmortems,
  useGenerateTickets,
  useGenerateAgentActions,
  useResetData,
} from "../hooks/useApi";

interface CounterCardProps {
  label: string;
  count: number;
  icon: React.ReactNode;
  color: string;
  href?: string;
  onClick?: () => void;
}

function CounterCard({ label, count, icon, color, href, onClick }: CounterCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (href) {
      navigate(href);
    }
  };

  const isClickable = href || onClick;

  return (
    <div
      className={clsx(
        "bg-gray-800 rounded-lg p-4 border border-gray-700 transition-colors",
        isClickable && "cursor-pointer hover:bg-gray-700 hover:border-gray-600",
      )}
      onClick={isClickable ? handleClick : undefined}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={
        isClickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                handleClick();
              }
            }
          : undefined
      }
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{label}</p>
          <p className={clsx("text-2xl font-bold", color)}>{count.toLocaleString()}</p>
        </div>
        <div className={clsx("p-3 rounded-lg bg-opacity-20", color.replace("text-", "bg-"))}>
          {icon}
        </div>
      </div>
    </div>
  );
}

interface ActionButtonProps {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
  icon: React.ReactNode;
  label: string;
  loadingLabel: string;
  variant: "primary" | "secondary" | "danger";
}

function ActionButton({
  onClick,
  disabled,
  loading,
  icon,
  label,
  loadingLabel,
  variant,
}: ActionButtonProps) {
  const variants = {
    primary: "bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800",
    secondary: "bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700",
    danger: "bg-red-600 hover:bg-red-700 disabled:bg-red-800",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        "flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors disabled:cursor-not-allowed",
        variants[variant],
        "text-white",
      )}
    >
      {loading ? (
        <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
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
      ) : (
        icon
      )}
      <span>{loading ? loadingLabel : label}</span>
    </button>
  );
}

export function GenerationPage() {
  const [seed, setSeed] = useState<string>("");

  const { data: status, isLoading: statusLoading, error: statusError } = useGenerationStatus();
  const generateAll = useGenerateAll();
  const generateAssets = useGenerateAssets();
  const generateEDR = useGenerateEDR();
  const generateIncidents = useGenerateIncidents();
  const generatePostmortems = useGeneratePostmortems();
  const generateTickets = useGenerateTickets();
  const generateAgentActions = useGenerateAgentActions();
  const resetData = useResetData();

  const isAnyLoading =
    generateAll.isPending ||
    generateAssets.isPending ||
    generateEDR.isPending ||
    generateIncidents.isPending ||
    generatePostmortems.isPending ||
    generateTickets.isPending ||
    generateAgentActions.isPending ||
    resetData.isPending;

  const parsedSeed = seed ? parseInt(seed, 10) : undefined;

  const handleGenerateAll = () => {
    generateAll.mutate(parsedSeed);
  };

  const handleGenerateAssets = () => {
    generateAssets.mutate({ seed: parsedSeed });
  };

  const handleGenerateEDR = () => {
    generateEDR.mutate({ seed: parsedSeed });
  };

  const handleGenerateIncidents = () => {
    generateIncidents.mutate({ seed: parsedSeed });
  };

  const handleGeneratePostmortems = () => {
    generatePostmortems.mutate({ seed: parsedSeed });
  };

  const handleGenerateTickets = () => {
    generateTickets.mutate({ seed: parsedSeed });
  };

  const handleGenerateAgentActions = () => {
    generateAgentActions.mutate({ seed: parsedSeed });
  };

  const handleReset = () => {
    if (window.confirm("Are you sure you want to reset all data? This action cannot be undone.")) {
      resetData.mutate();
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Data Generation</h1>
        <p className="text-gray-400 mt-1">
          Generate synthetic SOC data for testing and demonstration
        </p>
      </div>

      {/* Seed Input */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Configuration</h2>
        <div className="flex items-end space-x-4">
          <div className="flex-1 max-w-xs">
            <label htmlFor="seed" className="block text-sm font-medium text-gray-400 mb-2">
              Random Seed (optional)
            </label>
            <input
              type="number"
              id="seed"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder="Enter seed for reproducible data"
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
          <p className="text-sm text-gray-500 pb-2">
            Using the same seed will generate identical data
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Actions</h2>
        <div className="flex flex-wrap gap-4">
          <ActionButton
            onClick={handleGenerateAll}
            disabled={isAnyLoading}
            loading={generateAll.isPending}
            variant="primary"
            label="Generate All"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGenerateAssets}
            disabled={isAnyLoading}
            loading={generateAssets.isPending}
            variant="secondary"
            label="Generate Assets"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGenerateEDR}
            disabled={isAnyLoading}
            loading={generateEDR.isPending}
            variant="secondary"
            label="Generate EDR"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGenerateIncidents}
            disabled={isAnyLoading}
            loading={generateIncidents.isPending}
            variant="secondary"
            label="Generate Incidents"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGeneratePostmortems}
            disabled={isAnyLoading}
            loading={generatePostmortems.isPending}
            variant="secondary"
            label="Generate Postmortems"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGenerateTickets}
            disabled={isAnyLoading}
            loading={generateTickets.isPending}
            variant="secondary"
            label="Generate Tickets"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleGenerateAgentActions}
            disabled={isAnyLoading}
            loading={generateAgentActions.isPending}
            variant="secondary"
            label="Generate Agent Actions"
            loadingLabel="Generating..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />
          <ActionButton
            onClick={handleReset}
            disabled={isAnyLoading}
            loading={resetData.isPending}
            variant="danger"
            label="Reset All Data"
            loadingLabel="Resetting..."
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            }
          />
        </div>

        {/* Progress Indicator */}
        {isAnyLoading && (
          <div className="mt-6">
            <div className="flex items-center space-x-3">
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-cyan-500 h-2 rounded-full animate-pulse"
                  style={{ width: "60%" }}
                />
              </div>
              <span className="text-sm text-gray-400 whitespace-nowrap">Processing...</span>
            </div>
          </div>
        )}

        {/* Success/Error Messages */}
        {generateAll.isSuccess && (
          <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
            <p className="text-green-400">Data generated successfully!</p>
          </div>
        )}
        {(generateAll.isError ||
          generateAssets.isError ||
          generateEDR.isError ||
          generateIncidents.isError ||
          generatePostmortems.isError ||
          generateTickets.isError ||
          generateAgentActions.isError ||
          resetData.isError) && (
          <div className="mt-4 p-4 bg-red-900/30 border border-red-700 rounded-lg">
            <p className="text-red-400">
              Error:{" "}
              {
                (
                  generateAll.error ||
                  generateAssets.error ||
                  generateEDR.error ||
                  generateIncidents.error ||
                  generatePostmortems.error ||
                  generateTickets.error ||
                  generateAgentActions.error ||
                  resetData.error
                )?.message
              }
            </p>
          </div>
        )}
      </div>

      {/* Record Counters */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Current Data Status</h2>

        {statusLoading && (
          <div className="flex items-center justify-center py-8">
            <svg className="w-8 h-8 animate-spin text-cyan-500" fill="none" viewBox="0 0 24 24">
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
          </div>
        )}

        {statusError && (
          <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg">
            <p className="text-red-400">Failed to load status: {statusError.message}</p>
          </div>
        )}

        {status && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <CounterCard
              label="Assets"
              count={status.assets}
              color="text-cyan-400"
              href="/assets"
              icon={
                <svg
                  className="w-6 h-6 text-cyan-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              }
            />
            <CounterCard
              label="Incidents"
              count={status.incidents}
              color="text-orange-400"
              href="/incidents"
              icon={
                <svg
                  className="w-6 h-6 text-orange-400"
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
              }
            />
            <CounterCard
              label="Detections"
              count={status.detections}
              color="text-red-400"
              href="/detections"
              icon={
                <svg
                  className="w-6 h-6 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              }
            />
            <CounterCard
              label="Postmortems"
              count={status.postmortems}
              color="text-purple-400"
              href="/postmortems"
              icon={
                <svg
                  className="w-6 h-6 text-purple-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              }
            />
            <CounterCard
              label="Tickets"
              count={status.tickets}
              color="text-green-400"
              href="/tickets"
              icon={
                <svg
                  className="w-6 h-6 text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"
                  />
                </svg>
              }
            />
            <CounterCard
              label="Agent Actions"
              count={status.agent_actions}
              color="text-yellow-400"
              href="/audit"
              icon={
                <svg
                  className="w-6 h-6 text-yellow-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              }
            />
          </div>
        )}
      </div>
    </div>
  );
}
