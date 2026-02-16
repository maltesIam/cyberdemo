/**
 * SSVCDashboard - Interactive SSVC Decision Dashboard
 *
 * Features:
 * - Interactive SSVC decision tree visualization
 * - Glow effects on hover
 * - Click to filter CVEs by decision path
 * - Decision statistics cards
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import clsx from "clsx";
import { useQuery } from "@tanstack/react-query";
import { Breadcrumbs } from "../../components/vuln-views/Breadcrumbs";
import * as api from "../../services/api";

interface SSVCDashboardData {
  decision_tree: {
    exploitation: Record<string, any>;
  };
  summary: {
    total_cves: number;
    act: number;
    attend: number;
    track_star: number;
    track: number;
  };
  decision_distribution: Array<{
    decision: string;
    count: number;
    percentage: number;
  }>;
}

export function SSVCDashboard() {
  const navigate = useNavigate();
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);

  const { data, isLoading, error } = useQuery<SSVCDashboardData>({
    queryKey: ["ssvc-dashboard"],
    queryFn: () => api.getSSVCDashboard(),
  });

  const decisionConfig = {
    Act: {
      color: "red",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/30",
      textColor: "text-red-400",
      glowColor: "shadow-red-500/40",
      description: "Immediate action required - critical vulnerabilities actively being exploited",
    },
    Attend: {
      color: "orange",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/30",
      textColor: "text-orange-400",
      glowColor: "shadow-orange-500/40",
      description: "Schedule remediation soon - high priority vulnerabilities with active threats",
    },
    "Track*": {
      color: "yellow",
      bgColor: "bg-yellow-500/10",
      borderColor: "border-yellow-500/30",
      textColor: "text-yellow-400",
      glowColor: "shadow-yellow-500/40",
      description: "Track closely - vulnerabilities that may require future attention",
    },
    Track: {
      color: "green",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/30",
      textColor: "text-green-400",
      glowColor: "shadow-green-500/40",
      description: "Monitor as part of regular vulnerability management",
    },
  };

  if (isLoading) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: "SSVC Dashboard" },
            ]}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <svg
              className="w-12 h-12 text-cyan-500 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
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
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span className="text-gray-400">Loading SSVC data...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex flex-col">
        <div className="mb-4">
          <Breadcrumbs
            items={[
              { label: "Vulnerabilities", href: "/vulnerabilities" },
              { label: "SSVC Dashboard" },
            ]}
          />
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-500 text-xl mb-2">Error</div>
            <p className="text-gray-400">
              {error instanceof Error ? error.message : "Failed to load SSVC data"}
            </p>
            <button
              onClick={() => navigate("/vulnerabilities")}
              className="mt-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg"
            >
              Back to Vulnerabilities
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleDecisionClick = (decision: string) => {
    setSelectedDecision(selectedDecision === decision ? null : decision);
  };

  return (
    <div className="h-full flex flex-col space-y-4 overflow-auto">
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={[
          { label: "Vulnerabilities", href: "/vulnerabilities" },
          { label: "SSVC Dashboard" },
        ]}
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            SSVC Decision Dashboard
          </h1>
          <p className="text-gray-400 mt-1">
            Stakeholder-Specific Vulnerability Categorization for prioritization
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-cyan-400">{data?.summary?.total_cves ?? 0}</div>
          <div className="text-sm text-gray-500">Total CVEs</div>
        </div>
      </div>

      {/* Decision Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {(["Act", "Attend", "Track*", "Track"] as const).map((decision) => {
          const config = decisionConfig[decision];
          const count = decision === "Act" ? data?.summary?.act :
                       decision === "Attend" ? data?.summary?.attend :
                       decision === "Track*" ? data?.summary?.track_star :
                       data?.summary?.track;
          const dist = data?.decision_distribution?.find(d => d.decision === decision);

          return (
            <button
              key={decision}
              data-testid={`ssvc-card-${decision.toLowerCase().replace("*", "-star")}`}
              onClick={() => handleDecisionClick(decision)}
              className={clsx(
                "p-4 rounded-lg border transition-all cursor-pointer text-left",
                config.bgColor,
                config.borderColor,
                selectedDecision === decision && `shadow-lg ${config.glowColor}`,
                "hover:shadow-lg",
                `hover:${config.glowColor}`
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={clsx("text-lg font-bold", config.textColor)}>
                  {decision}
                </span>
                <span className={clsx("text-2xl font-bold", config.textColor)}>
                  {count ?? 0}
                </span>
              </div>
              <div className="text-xs text-gray-400 mb-2">
                {dist?.percentage?.toFixed(1) ?? 0}% of total
              </div>
              <div className="text-xs text-gray-500">{config.description}</div>
            </button>
          );
        })}
      </div>

      {/* Decision Tree Visualization */}
      <div className="flex-1 bg-gray-800 rounded-lg p-6" data-testid="ssvc-decision-tree">
        <h3 className="text-lg font-semibold text-white mb-4">Decision Tree</h3>

        <div className="grid grid-cols-3 gap-8">
          {/* Exploitation Column */}
          <div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase mb-4">
              Exploitation Status
            </h4>
            <div className="space-y-3">
              {["Active", "PoC", "None"].map((status) => (
                <div
                  key={status}
                  data-testid={`tree-node-exploitation-${status.toLowerCase()}`}
                  className={clsx(
                    "p-3 rounded-lg border transition-all cursor-pointer",
                    status === "Active" && "bg-red-500/10 border-red-500/30 text-red-400 hover:shadow-lg hover:shadow-red-500/20",
                    status === "PoC" && "bg-orange-500/10 border-orange-500/30 text-orange-400 hover:shadow-lg hover:shadow-orange-500/20",
                    status === "None" && "bg-green-500/10 border-green-500/30 text-green-400 hover:shadow-lg hover:shadow-green-500/20"
                  )}
                >
                  <div className="font-medium">{status}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {status === "Active" && "Exploitation is confirmed in the wild"}
                    {status === "PoC" && "Proof of concept code exists"}
                    {status === "None" && "No known exploitation"}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Automatable Column */}
          <div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase mb-4">
              Automatable
            </h4>
            <div className="space-y-3">
              {["Yes", "No"].map((auto) => (
                <div
                  key={auto}
                  data-testid={`tree-node-automatable-${auto.toLowerCase()}`}
                  className={clsx(
                    "p-3 rounded-lg border transition-all cursor-pointer",
                    auto === "Yes" && "bg-red-500/10 border-red-500/30 text-red-400 hover:shadow-lg hover:shadow-red-500/20",
                    auto === "No" && "bg-yellow-500/10 border-yellow-500/30 text-yellow-400 hover:shadow-lg hover:shadow-yellow-500/20"
                  )}
                >
                  <div className="font-medium">{auto}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {auto === "Yes" && "Can be exploited automatically at scale"}
                    {auto === "No" && "Requires manual attacker action"}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Decision Outcomes Column */}
          <div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase mb-4">
              Decision Outcome
            </h4>
            <div className="space-y-3">
              {(["Act", "Attend", "Track*", "Track"] as const).map((decision) => {
                const config = decisionConfig[decision];
                return (
                  <div
                    key={decision}
                    data-testid={`decision-node-${decision.toLowerCase().replace("*", "-star")}`}
                    onClick={() => handleDecisionClick(decision)}
                    className={clsx(
                      "p-3 rounded-lg border transition-all cursor-pointer",
                      config.bgColor,
                      config.borderColor,
                      config.textColor,
                      selectedDecision === decision && `shadow-lg ${config.glowColor} ring-2 ring-offset-2 ring-offset-gray-800`,
                      selectedDecision === decision && decision === "Act" && "ring-red-500",
                      selectedDecision === decision && decision === "Attend" && "ring-orange-500",
                      selectedDecision === decision && decision === "Track*" && "ring-yellow-500",
                      selectedDecision === decision && decision === "Track" && "ring-green-500",
                      "hover:shadow-lg",
                      `hover:${config.glowColor}`
                    )}
                  >
                    <div className="font-medium">{decision}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {decision === "Act" && "Immediate remediation"}
                      {decision === "Attend" && "Schedule soon"}
                      {decision === "Track*" && "Monitor closely"}
                      {decision === "Track" && "Standard monitoring"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Selected Decision Info */}
      {selectedDecision && (
        <div
          className={clsx(
            "bg-gray-800 rounded-lg p-4 border",
            decisionConfig[selectedDecision as keyof typeof decisionConfig].borderColor
          )}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className={clsx(
              "text-lg font-semibold",
              decisionConfig[selectedDecision as keyof typeof decisionConfig].textColor
            )}>
              CVEs with "{selectedDecision}" Decision
            </h3>
            <Link
              to={`/vulnerabilities?ssvc_decision=${selectedDecision}`}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm"
            >
              View All CVEs
            </Link>
          </div>
          <p className="text-gray-400">
            {decisionConfig[selectedDecision as keyof typeof decisionConfig].description}
          </p>
        </div>
      )}

      {/* SSVC Framework Info */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">
          About SSVC
        </h3>
        <p className="text-gray-400 text-sm">
          The Stakeholder-Specific Vulnerability Categorization (SSVC) framework provides
          a systematic approach to vulnerability prioritization. Unlike CVSS which focuses
          on technical severity, SSVC considers exploitation status, automatable nature,
          and mission impact to determine the appropriate response action.
        </p>
      </div>
    </div>
  );
}
