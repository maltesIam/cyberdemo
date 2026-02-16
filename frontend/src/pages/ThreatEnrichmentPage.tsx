/**
 * ThreatEnrichmentPage - Comprehensive Threat Intelligence Dashboard
 *
 * Features:
 * - Interactive world map with animated threat lines
 * - IOC enrichment with multiple sources
 * - MITRE ATT&CK technique visualization
 * - Malware families and threat actors
 * - Detailed IOC inspection
 */

import { useState, useEffect, useCallback } from "react";
import clsx from "clsx";
import { ThreatMap } from "../components/ThreatMap";
import { useToast } from "../utils/toast";

// Types
interface EnrichedThreat {
  id: string;
  type: string;
  value: string;
  risk_score: number;
  risk_level: string;
  confidence: number;
  geo?: {
    country: string;
    country_name: string;
    city: string;
    latitude: number;
    longitude: number;
  };
  network?: {
    asn: number;
    asn_org: string;
    is_vpn: boolean;
    is_proxy: boolean;
    is_tor: boolean;
    is_datacenter: boolean;
  };
  reputation: {
    abuseipdb?: {
      confidence_score: number;
      total_reports: number;
      abuse_categories: string[];
    };
    greynoise?: {
      classification: string;
      noise: boolean;
    };
    virustotal?: {
      malicious_count: number;
      suspicious_count: number;
      harmless_count: number;
      community_score: number;
    };
  };
  threat_intel: {
    malware_families: string[];
    threat_actors: string[];
    campaigns: string[];
    tags: string[];
  };
  mitre_attack: {
    techniques: {
      id: string;
      name: string;
      tactic?: string;
    }[];
  };
  intel_feeds: {
    source: string;
    feed_name: string;
    author: string;
    tlp: string;
  }[];
  enrichment_meta: {
    enriched_at: string;
    sources_successful: string[];
    sources_failed: string[];
  };
}

// MITRE ATT&CK Tactics
const MITRE_TACTICS = [
  { id: "TA0001", name: "Initial Access", color: "bg-red-600" },
  { id: "TA0002", name: "Execution", color: "bg-orange-600" },
  { id: "TA0003", name: "Persistence", color: "bg-amber-600" },
  { id: "TA0004", name: "Privilege Escalation", color: "bg-yellow-600" },
  { id: "TA0005", name: "Defense Evasion", color: "bg-lime-600" },
  { id: "TA0006", name: "Credential Access", color: "bg-green-600" },
  { id: "TA0007", name: "Discovery", color: "bg-emerald-600" },
  { id: "TA0008", name: "Lateral Movement", color: "bg-teal-600" },
  { id: "TA0009", name: "Collection", color: "bg-cyan-600" },
  { id: "TA0011", name: "Command and Control", color: "bg-blue-600" },
  { id: "TA0010", name: "Exfiltration", color: "bg-indigo-600" },
  { id: "TA0040", name: "Impact", color: "bg-purple-600" },
];

export function ThreatEnrichmentPage() {
  const { showToast } = useToast();
  const [threats, setThreats] = useState<EnrichedThreat[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedThreat, setSelectedThreat] = useState<EnrichedThreat | null>(null);
  const [iocInput, setIocInput] = useState("");
  const [enrichmentProgress, setEnrichmentProgress] = useState(0);
  const [isEnriching, setIsEnriching] = useState(false);

  // Stats computed from threats
  const stats = {
    total: threats.length,
    critical: threats.filter((t) => t.risk_level === "critical").length,
    high: threats.filter((t) => t.risk_level === "high").length,
    medium: threats.filter((t) => t.risk_level === "medium").length,
    low: threats.filter((t) => t.risk_level === "low").length,
    countries: new Set(threats.map((t) => t.geo?.country).filter(Boolean)).size,
    malwareFamilies: [...new Set(threats.flatMap((t) => t.threat_intel.malware_families))],
    threatActors: [...new Set(threats.flatMap((t) => t.threat_intel.threat_actors))],
    techniques: [
      ...new Set(threats.flatMap((t) => t.mitre_attack.techniques.map((tech) => tech.id))),
    ],
  };

  // Enrich IOCs
  const handleEnrich = useCallback(async () => {
    if (!iocInput.trim()) {
      showToast("warning", "Please enter IOCs to enrich", 3000);
      return;
    }

    // Parse IOCs (one per line or comma-separated)
    const lines = iocInput
      .split(/[\n,]/)
      .map((s) => s.trim())
      .filter(Boolean);
    const indicators = lines.map((value) => {
      // Auto-detect type
      let type = "unknown";
      if (/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(value)) {
        type = "ip";
      } else if (
        /^[a-f0-9]{32}$/i.test(value) ||
        /^[a-f0-9]{40}$/i.test(value) ||
        /^[a-f0-9]{64}$/i.test(value)
      ) {
        type = "hash";
      } else if (/^https?:\/\//.test(value)) {
        type = "url";
      } else if (/^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) {
        type = "domain";
      } else if (/@/.test(value)) {
        type = "email";
      }
      return { type, value };
    });

    if (indicators.length === 0) {
      showToast("warning", "No valid IOCs found", 3000);
      return;
    }

    setIsEnriching(true);
    setEnrichmentProgress(0);

    try {
      // Call enrichment API
      const response = await fetch("/api/enrichment/threats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          indicators,
          sources: ["otx", "abuseipdb", "greynoise", "virustotal", "synthetic"],
          force_refresh: false,
        }),
      });

      if (!response.ok) {
        throw new Error("Enrichment request failed");
      }

      const data = await response.json();

      // Simulate progress for visual effect
      for (let i = 0; i <= 100; i += 10) {
        setEnrichmentProgress(i);
        await new Promise((r) => setTimeout(r, 100));
      }

      // Add enriched threats
      if (data.enriched_indicators) {
        setThreats((prev) => [...data.enriched_indicators, ...prev]);
        showToast(
          "success",
          `Enriched ${data.enriched_indicators.length} IOCs from ${data.successful_sources} sources`,
          4000,
        );
      }
    } catch (error) {
      showToast("error", "Enrichment failed. Please try again.", 5000);
      console.error("Enrichment error:", error);
    } finally {
      setIsEnriching(false);
      setEnrichmentProgress(0);
      setIocInput("");
    }
  }, [iocInput, showToast]);

  // Generate demo data
  const generateDemoData = useCallback(async () => {
    setLoading(true);
    try {
      // Call enrichment API with sample IPs
      const sampleIPs = [
        "45.33.32.156",
        "185.220.101.1",
        "91.219.236.166",
        "5.188.206.206",
        "194.169.175.35",
        "103.90.161.129",
        "193.22.96.85",
        "141.98.80.72",
        "45.146.164.110",
        "185.117.75.123",
        "193.169.255.78",
        "89.248.167.131",
        "92.63.197.48",
        "45.155.204.241",
        "185.56.80.65",
      ];

      const indicators = sampleIPs.map((ip) => ({ type: "ip", value: ip }));

      const response = await fetch("/api/enrichment/threats", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          indicators,
          sources: ["synthetic"],
          force_refresh: true,
        }),
      });

      const data = await response.json();

      if (data.enriched_indicators) {
        setThreats(data.enriched_indicators);
        showToast("success", `Loaded ${data.enriched_indicators.length} threat indicators`, 3000);
      }
    } catch (error) {
      showToast("error", "Failed to load demo data", 4000);
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  // Load demo data on mount
  useEffect(() => {
    generateDemoData();
  }, []);

  // Risk level colors
  const riskColors = {
    critical: "text-red-500 bg-red-500/20 border-red-500/50",
    high: "text-orange-500 bg-orange-500/20 border-orange-500/50",
    medium: "text-yellow-500 bg-yellow-500/20 border-yellow-500/50",
    low: "text-green-500 bg-green-500/20 border-green-500/50",
    unknown: "text-gray-500 bg-gray-500/20 border-gray-500/50",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <svg
              className="w-8 h-8 text-red-500"
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
            Threat Intelligence Enrichment
          </h1>
          <p className="text-gray-400 mt-1">
            Real-time IOC enrichment from 18+ threat intelligence sources
          </p>
        </div>
        <button
          onClick={generateDemoData}
          disabled={loading}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh Demo Data"}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-cyan-400">{stats.total}</div>
          <div className="text-sm text-gray-400">Total IOCs</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-red-500/30">
          <div className="text-3xl font-bold text-red-500">{stats.critical}</div>
          <div className="text-sm text-gray-400">Critical</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-orange-500/30">
          <div className="text-3xl font-bold text-orange-500">{stats.high}</div>
          <div className="text-sm text-gray-400">High</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-yellow-500/30">
          <div className="text-3xl font-bold text-yellow-500">{stats.medium}</div>
          <div className="text-sm text-gray-400">Medium</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-purple-400">{stats.countries}</div>
          <div className="text-sm text-gray-400">Countries</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="text-3xl font-bold text-blue-400">{stats.techniques.length}</div>
          <div className="text-sm text-gray-400">ATT&CK TTPs</div>
        </div>
      </div>

      {/* IOC Input */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <svg
            className="w-5 h-5 text-cyan-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Enrich IOCs
        </h3>
        <div className="flex gap-4">
          <textarea
            value={iocInput}
            onChange={(e) => setIocInput(e.target.value)}
            placeholder="Enter IOCs (one per line or comma-separated):
192.168.1.100
evil-domain.com
d41d8cd98f00b204e9800998ecf8427e
http://malware.com/payload.exe"
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 font-mono text-sm"
            rows={4}
          />
          <div className="flex flex-col gap-2">
            <button
              onClick={handleEnrich}
              disabled={isEnriching || !iocInput.trim()}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isEnriching ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
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
                  {enrichmentProgress}%
                </span>
              ) : (
                "Enrich Threats"
              )}
            </button>
            <div className="text-xs text-gray-500 text-center">
              Auto-detects: IP, Domain, Hash, URL, Email
            </div>
          </div>
        </div>
      </div>

      {/* World Map */}
      <ThreatMap
        threats={threats}
        onCountryClick={(country) => {
          showToast("info", `Filtering by ${country}`, 2000);
        }}
        onThreatClick={(id) => {
          const threat = threats.find((t) => t.id === id);
          if (threat) setSelectedThreat(threat);
        }}
      />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* IOC List */}
        <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h3 className="text-lg font-semibold text-white">Enriched IOCs</h3>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            {threats.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No threats enriched yet. Add IOCs above or load demo data.
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-900 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      IOC
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Risk
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Country
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Malware
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">
                      Sources
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {threats.map((threat) => (
                    <tr
                      key={threat.id}
                      onClick={() => setSelectedThreat(threat)}
                      className="hover:bg-gray-700/50 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3 font-mono text-sm text-white">
                        {threat.value.length > 20
                          ? `${threat.value.slice(0, 20)}...`
                          : threat.value}
                      </td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 text-xs rounded bg-gray-700 text-gray-300 uppercase">
                          {threat.type}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={clsx(
                            "px-2 py-1 text-xs font-bold rounded border",
                            riskColors[threat.risk_level as keyof typeof riskColors],
                          )}
                        >
                          {threat.risk_score}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-300">
                        {threat.geo?.country || "-"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {threat.threat_intel.malware_families.slice(0, 2).map((m) => (
                            <span
                              key={m}
                              className="px-1.5 py-0.5 text-xs bg-red-500/20 text-red-400 rounded"
                            >
                              {m}
                            </span>
                          ))}
                          {threat.threat_intel.malware_families.length > 2 && (
                            <span className="text-xs text-gray-500">
                              +{threat.threat_intel.malware_families.length - 2}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <span className="text-green-400 text-sm">
                            {threat.enrichment_meta.sources_successful.length}
                          </span>
                          <span className="text-gray-500">/</span>
                          <span className="text-gray-400 text-sm">
                            {threat.enrichment_meta.sources_successful.length +
                              threat.enrichment_meta.sources_failed.length}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Side Panels */}
        <div className="space-y-6">
          {/* Malware Families */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-red-400"
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
              Top Malware Families
            </h3>
            <div className="space-y-3">
              {stats.malwareFamilies.slice(0, 8).map((family) => {
                const count = threats.filter((t) =>
                  t.threat_intel.malware_families.includes(family),
                ).length;
                const percentage = (count / threats.length) * 100;

                return (
                  <div key={family}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300">{family}</span>
                      <span className="text-gray-500">{count}</span>
                    </div>
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-red-500 to-orange-500 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Threat Actors */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-purple-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              Threat Actors
            </h3>
            <div className="flex flex-wrap gap-2">
              {stats.threatActors.map((actor) => (
                <span
                  key={actor}
                  className="px-3 py-1.5 bg-purple-500/20 text-purple-300 rounded-full text-sm font-medium border border-purple-500/30 hover:bg-purple-500/30 cursor-pointer transition-colors"
                >
                  {actor}
                </span>
              ))}
              {stats.threatActors.length === 0 && (
                <span className="text-gray-500 text-sm">No actors identified</span>
              )}
            </div>
          </div>

          {/* MITRE ATT&CK */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <svg
                className="w-5 h-5 text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              MITRE ATT&CK Coverage
            </h3>
            <div className="space-y-2">
              {MITRE_TACTICS.slice(0, 6).map((tactic) => {
                const techniques = threats.flatMap((t) =>
                  t.mitre_attack.techniques.filter(
                    (tech) => tech.tactic === tactic.name.replace(" ", ""),
                  ),
                );
                const count = new Set(techniques.map((t) => t.id)).size;

                return (
                  <div key={tactic.id} className="flex items-center gap-3">
                    <div className={clsx("w-2 h-2 rounded-full", tactic.color)} />
                    <span className="text-sm text-gray-300 flex-1">{tactic.name}</span>
                    <span className="text-sm text-gray-500">{count || "-"}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* IOC Detail Modal */}
      {selectedThreat && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedThreat(null)}
        >
          <div
            className="bg-gray-800 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-gray-800 px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white font-mono">{selectedThreat.value}</h2>
                <p className="text-gray-400 text-sm">Type: {selectedThreat.type.toUpperCase()}</p>
              </div>
              <div className="flex items-center gap-4">
                <span
                  className={clsx(
                    "px-4 py-2 text-lg font-bold rounded-lg border",
                    riskColors[selectedThreat.risk_level as keyof typeof riskColors],
                  )}
                >
                  Risk: {selectedThreat.risk_score}
                </span>
                <button
                  onClick={() => setSelectedThreat(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Geo & Network */}
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-3">Geolocation</h4>
                  {selectedThreat.geo ? (
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Country</span>
                        <span className="text-white">
                          {selectedThreat.geo.country_name} ({selectedThreat.geo.country})
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">City</span>
                        <span className="text-white">{selectedThreat.geo.city}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Coordinates</span>
                        <span className="text-white">
                          {selectedThreat.geo.latitude?.toFixed(2)},{" "}
                          {selectedThreat.geo.longitude?.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <span className="text-gray-500">No geolocation data</span>
                  )}
                </div>

                <div className="bg-gray-900 rounded-lg p-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-3">Network</h4>
                  {selectedThreat.network ? (
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">ASN</span>
                        <span className="text-white">AS{selectedThreat.network.asn}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Organization</span>
                        <span className="text-white">{selectedThreat.network.asn_org}</span>
                      </div>
                      <div className="flex gap-2 mt-2">
                        {selectedThreat.network.is_vpn && (
                          <span className="px-2 py-1 text-xs bg-yellow-500/20 text-yellow-400 rounded">
                            VPN
                          </span>
                        )}
                        {selectedThreat.network.is_proxy && (
                          <span className="px-2 py-1 text-xs bg-orange-500/20 text-orange-400 rounded">
                            Proxy
                          </span>
                        )}
                        {selectedThreat.network.is_tor && (
                          <span className="px-2 py-1 text-xs bg-purple-500/20 text-purple-400 rounded">
                            Tor
                          </span>
                        )}
                        {selectedThreat.network.is_datacenter && (
                          <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
                            Datacenter
                          </span>
                        )}
                      </div>
                    </div>
                  ) : (
                    <span className="text-gray-500">No network data</span>
                  )}
                </div>
              </div>

              {/* Reputation Sources */}
              <div className="bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">Reputation Sources</h4>
                <div className="grid grid-cols-3 gap-4">
                  {selectedThreat.reputation.abuseipdb && (
                    <div className="bg-gray-800 rounded p-3">
                      <div className="text-xs text-gray-500 mb-1">AbuseIPDB</div>
                      <div className="text-2xl font-bold text-red-400">
                        {selectedThreat.reputation.abuseipdb.confidence_score}%
                      </div>
                      <div className="text-xs text-gray-400">
                        {selectedThreat.reputation.abuseipdb.total_reports} reports
                      </div>
                    </div>
                  )}
                  {selectedThreat.reputation.greynoise && (
                    <div className="bg-gray-800 rounded p-3">
                      <div className="text-xs text-gray-500 mb-1">GreyNoise</div>
                      <div
                        className={clsx(
                          "text-lg font-bold uppercase",
                          selectedThreat.reputation.greynoise.classification === "malicious"
                            ? "text-red-400"
                            : "text-gray-400",
                        )}
                      >
                        {selectedThreat.reputation.greynoise.classification}
                      </div>
                      <div className="text-xs text-gray-400">
                        {selectedThreat.reputation.greynoise.noise ? "Internet noise" : "Not noise"}
                      </div>
                    </div>
                  )}
                  {selectedThreat.reputation.virustotal && (
                    <div className="bg-gray-800 rounded p-3">
                      <div className="text-xs text-gray-500 mb-1">VirusTotal</div>
                      <div className="text-2xl font-bold text-orange-400">
                        {selectedThreat.reputation.virustotal.malicious_count}/
                        {selectedThreat.reputation.virustotal.malicious_count +
                          selectedThreat.reputation.virustotal.harmless_count}
                      </div>
                      <div className="text-xs text-gray-400">detections</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Threat Intel */}
              <div className="bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">Threat Intelligence</h4>
                <div className="space-y-3">
                  <div>
                    <span className="text-xs text-gray-500">Malware Families</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedThreat.threat_intel.malware_families.map((m) => (
                        <span
                          key={m}
                          className="px-2 py-1 text-sm bg-red-500/20 text-red-400 rounded"
                        >
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Threat Actors</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedThreat.threat_intel.threat_actors.map((a) => (
                        <span
                          key={a}
                          className="px-2 py-1 text-sm bg-purple-500/20 text-purple-400 rounded"
                        >
                          {a}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500">Tags</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedThreat.threat_intel.tags.map((t) => (
                        <span
                          key={t}
                          className="px-2 py-1 text-sm bg-gray-700 text-gray-300 rounded"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* MITRE ATT&CK */}
              <div className="bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">
                  MITRE ATT&CK Techniques
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedThreat.mitre_attack.techniques.map((tech) => (
                    <span
                      key={tech.id}
                      className="px-3 py-1.5 text-sm bg-blue-500/20 text-blue-300 rounded border border-blue-500/30"
                      title={tech.name}
                    >
                      {tech.id}
                    </span>
                  ))}
                </div>
              </div>

              {/* Intel Feeds */}
              <div className="bg-gray-900 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">Intelligence Feeds</h4>
                <div className="space-y-2">
                  {selectedThreat.intel_feeds.slice(0, 5).map((feed, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0"
                    >
                      <div>
                        <div className="text-white text-sm">{feed.feed_name}</div>
                        <div className="text-gray-500 text-xs">
                          {feed.source} · {feed.author}
                        </div>
                      </div>
                      <span
                        className={clsx(
                          "px-2 py-1 text-xs rounded uppercase",
                          feed.tlp === "red"
                            ? "bg-red-500/20 text-red-400"
                            : feed.tlp === "amber"
                              ? "bg-amber-500/20 text-amber-400"
                              : feed.tlp === "green"
                                ? "bg-green-500/20 text-green-400"
                                : "bg-gray-500/20 text-gray-400",
                        )}
                      >
                        TLP:{feed.tlp}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Enrichment Meta */}
              <div className="text-xs text-gray-500 flex items-center justify-between">
                <span>
                  Enriched: {new Date(selectedThreat.enrichment_meta.enriched_at).toLocaleString()}
                </span>
                <span>Sources: {selectedThreat.enrichment_meta.sources_successful.join(", ")}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
