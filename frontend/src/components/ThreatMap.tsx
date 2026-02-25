/**
 * ThreatMap Component - Interactive World Map with Animated Threat Lines
 *
 * Features:
 * - SVG world map with country highlighting
 * - Animated lines showing attack origins to targets
 * - Pulsing markers for active threats
 * - Country heat map based on threat density
 */

import { useState, useEffect, useMemo } from "react";

// Simplified world map coordinates (major countries)
const COUNTRY_PATHS: Record<string, { path: string; center: [number, number] }> = {
  US: {
    path: "M -122 38 L -75 38 L -75 48 L -122 48 Z",
    center: [-98.5, 39.8],
  },
  RU: {
    path: "M 30 55 L 180 55 L 180 75 L 30 75 Z",
    center: [105.3, 61.5],
  },
  CN: {
    path: "M 75 22 L 135 22 L 135 45 L 75 45 Z",
    center: [104.2, 35.9],
  },
  DE: {
    path: "M 6 47 L 15 47 L 15 55 L 6 55 Z",
    center: [10.5, 51.2],
  },
  NL: {
    path: "M 3.5 51 L 7 51 L 7 54 L 3.5 54 Z",
    center: [5.3, 52.1],
  },
  KP: {
    path: "M 124 37 L 130 37 L 130 43 L 124 43 Z",
    center: [127.5, 40.3],
  },
  IR: {
    path: "M 44 25 L 63 25 L 63 40 L 44 40 Z",
    center: [53.7, 32.4],
  },
  BR: {
    path: "M -73 -33 L -35 -33 L -35 5 L -73 5 Z",
    center: [-51.9, -14.2],
  },
  IN: {
    path: "M 68 8 L 97 8 L 97 35 L 68 35 Z",
    center: [78.9, 20.6],
  },
  GB: {
    path: "M -8 50 L 2 50 L 2 59 L -8 59 Z",
    center: [-3.4, 55.4],
  },
  ES: {
    path: "M -9 36 L 4 36 L 4 44 L -9 44 Z",
    center: [-3.7, 40.5],
  },
  FR: {
    path: "M -5 42 L 8 42 L 8 51 L -5 51 Z",
    center: [2.2, 46.2],
  },
};

// Target location (your SOC)
const TARGET_LOCATION: [number, number] = [-3.7, 40.5]; // Madrid, Spain

interface ThreatLine {
  id: string;
  from: [number, number];
  to: [number, number];
  risk: "critical" | "high" | "medium" | "low";
  country: string;
  iocCount: number;
  active: boolean;
}

interface ThreatMapProps {
  threats: {
    id: string;
    geo?: {
      country: string;
      country_name: string;
      latitude: number;
      longitude: number;
    };
    risk_level: string;
  }[];
  onCountryClick?: (country: string) => void;
  onThreatClick?: (threatId: string) => void;
}

// Convert lat/lon to SVG coordinates (simple equirectangular projection)
function geoToSvg(lon: number, lat: number): [number, number] {
  const x = ((lon + 180) / 360) * 800;
  const y = ((90 - lat) / 180) * 400;
  return [x, y];
}

// Generate curved path between two points
function generateCurvedPath(from: [number, number], to: [number, number]): string {
  const [x1, y1] = geoToSvg(from[0], from[1]);
  const [x2, y2] = geoToSvg(to[0], to[1]);

  // Calculate control point for bezier curve
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Curve upward proportional to distance
  const curveHeight = Math.min(distance * 0.3, 80);
  const controlY = midY - curveHeight;

  return `M ${x1} ${y1} Q ${midX} ${controlY} ${x2} ${y2}`;
}

export function ThreatMap({ threats, onCountryClick, onThreatClick: _onThreatClick }: ThreatMapProps) {
  const [animationPhase, setAnimationPhase] = useState(0);

  // Animate the threat lines
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationPhase((prev) => (prev + 1) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Aggregate threats by country
  const threatsByCountry = useMemo(() => {
    const map: Record<string, { count: number; maxRisk: string }> = {};
    for (const threat of threats) {
      const country = threat.geo?.country || "UNKNOWN";
      if (!map[country]) {
        map[country] = { count: 0, maxRisk: "low" };
      }
      map[country].count += 1;

      // Update max risk
      const riskOrder = { critical: 4, high: 3, medium: 2, low: 1, unknown: 0 };
      if (
        riskOrder[threat.risk_level as keyof typeof riskOrder] >
        riskOrder[map[country].maxRisk as keyof typeof riskOrder]
      ) {
        map[country].maxRisk = threat.risk_level;
      }
    }
    return map;
  }, [threats]);

  // Generate threat lines
  const threatLines: ThreatLine[] = useMemo(() => {
    const lines: ThreatLine[] = [];

    for (const threat of threats) {
      if (threat.geo?.latitude && threat.geo?.longitude) {
        lines.push({
          id: threat.id,
          from: [threat.geo.longitude, threat.geo.latitude],
          to: TARGET_LOCATION,
          risk: threat.risk_level as "critical" | "high" | "medium" | "low",
          country: threat.geo.country,
          iocCount: 1,
          active: true,
        });
      }
    }

    return lines;
  }, [threats]);

  // Risk colors
  const riskColors = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#eab308",
    low: "#22c55e",
    unknown: "#6b7280",
  };

  return (
    <div className="relative bg-primary rounded-xl border border-primary overflow-hidden">
      {/* Header */}
      <div className="absolute top-4 left-4 z-10">
        <h3 className="text-lg font-bold text-primary flex items-center gap-2">
          <svg
            className="w-5 h-5 text-red-500 animate-pulse"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" />
          </svg>
          Threat Origins - Live Attack Map
        </h3>
        <p className="text-secondary text-sm mt-1">
          {threats.length} active threats from {Object.keys(threatsByCountry).length} countries
        </p>
      </div>

      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 bg-secondary/80 backdrop-blur rounded-lg p-3">
        <div className="text-xs text-secondary mb-2">Risk Level</div>
        <div className="space-y-1">
          {Object.entries(riskColors).map(([level, color]) => (
            <div key={level} className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-xs text-secondary capitalize">{level}</span>
            </div>
          ))}
        </div>
      </div>

      {/* SVG Map */}
      <svg
        viewBox="0 0 800 400"
        className="w-full h-[500px]"
        style={{ background: "linear-gradient(180deg, #0f172a 0%, #1e293b 100%)" }}
      >
        {/* Grid lines */}
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="#334155"
              strokeWidth="0.5"
              opacity="0.3"
            />
          </pattern>
          {/* Glow filter for lines */}
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          {/* Animated gradient for lines */}
          <linearGradient id="threatGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset={`${animationPhase}%`} stopColor="#ef4444" />
            <stop offset={`${Math.min(animationPhase + 20, 100)}%`} stopColor="#ef4444" />
            <stop offset="100%" stopColor="transparent" />
          </linearGradient>
        </defs>

        <rect width="100%" height="100%" fill="url(#grid)" />

        {/* Simplified world map outline */}
        <g className="world-map">
          {/* Continents simplified */}
          {/* North America */}
          <path
            d="M 50 80 Q 100 60 150 80 L 200 100 L 220 150 L 180 180 L 120 200 L 80 180 L 50 140 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
          {/* South America */}
          <path
            d="M 180 220 Q 200 200 220 220 L 240 280 L 220 360 L 180 340 L 160 280 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
          {/* Europe */}
          <path
            d="M 380 60 Q 420 50 460 60 L 480 100 L 440 130 L 380 120 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
          {/* Africa */}
          <path
            d="M 380 140 Q 420 130 460 150 L 480 250 L 440 320 L 380 300 L 360 220 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
          {/* Asia */}
          <path
            d="M 480 40 Q 600 30 720 60 L 760 120 L 720 180 L 600 200 L 500 160 L 480 100 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
          {/* Australia */}
          <path
            d="M 660 280 Q 700 260 740 280 L 760 320 L 720 360 L 660 340 Z"
            fill="#1e3a5f"
            stroke="#334155"
            strokeWidth="1"
            opacity="0.8"
          />
        </g>

        {/* Country markers with threat counts */}
        {Object.entries(threatsByCountry).map(([country, data]) => {
          const coords = COUNTRY_PATHS[country]?.center;
          if (!coords) return null;

          const [x, y] = geoToSvg(coords[0], coords[1]);
          const color = riskColors[data.maxRisk as keyof typeof riskColors];
          const size = Math.min(8 + data.count * 2, 20);

          return (
            <g
              key={country}
              className="cursor-pointer transition-transform hover:scale-125"
              onClick={() => onCountryClick?.(country)}
            >
              {/* Pulsing ring */}
              <circle
                cx={x}
                cy={y}
                r={size + 5}
                fill="none"
                stroke={color}
                strokeWidth="2"
                opacity={0.3 + (Math.sin(Date.now() / 500 + x) + 1) / 4}
              >
                <animate
                  attributeName="r"
                  values={`${size};${size + 10};${size}`}
                  dur="2s"
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="opacity"
                  values="0.5;0;0.5"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
              {/* Main marker */}
              <circle cx={x} cy={y} r={size} fill={color} opacity="0.8" filter="url(#glow)" />
              {/* Count label */}
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                fontSize="10"
                fill="white"
                fontWeight="bold"
              >
                {data.count}
              </text>
            </g>
          );
        })}

        {/* Animated threat lines */}
        {threatLines.map((line, index) => {
          const path = generateCurvedPath(line.from, line.to);
          const color = riskColors[line.risk];
          const delay = index * 0.2;

          return (
            <g key={line.id}>
              {/* Background line */}
              <path d={path} fill="none" stroke={color} strokeWidth="1" opacity="0.3" />
              {/* Animated dash */}
              <path
                d={path}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeDasharray="10,5"
                filter="url(#glow)"
                className="animate-pulse"
              >
                <animate
                  attributeName="stroke-dashoffset"
                  values="0;-30"
                  dur="1s"
                  repeatCount="indefinite"
                  begin={`${delay}s`}
                />
              </path>
              {/* Moving dot */}
              <circle r="4" fill={color} filter="url(#glow)">
                <animateMotion dur="3s" repeatCount="indefinite" begin={`${delay}s`}>
                  <mpath href={`#path-${line.id}`} />
                </animateMotion>
              </circle>
              <path id={`path-${line.id}`} d={path} fill="none" stroke="none" />
            </g>
          );
        })}

        {/* Target location (SOC) */}
        <g>
          {(() => {
            const [x, y] = geoToSvg(TARGET_LOCATION[0], TARGET_LOCATION[1]);
            return (
              <>
                <circle cx={x} cy={y} r="15" fill="none" stroke="#22c55e" strokeWidth="2">
                  <animate attributeName="r" values="15;25;15" dur="2s" repeatCount="indefinite" />
                  <animate
                    attributeName="opacity"
                    values="1;0.3;1"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
                <circle cx={x} cy={y} r="10" fill="#22c55e" />
                <text
                  x={x}
                  y={y + 25}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#22c55e"
                  fontWeight="bold"
                >
                  SOC
                </text>
              </>
            );
          })()}
        </g>
      </svg>

      {/* Stats overlay */}
      <div className="absolute bottom-4 left-4 right-4 flex gap-4">
        <div className="bg-secondary/90 backdrop-blur rounded-lg px-4 py-2 flex items-center gap-3">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <div>
            <div className="text-2xl font-bold text-primary">
              {threatsByCountry["RU"]?.count || 0}
            </div>
            <div className="text-xs text-secondary">Russia</div>
          </div>
        </div>
        <div className="bg-secondary/90 backdrop-blur rounded-lg px-4 py-2 flex items-center gap-3">
          <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
          <div>
            <div className="text-2xl font-bold text-primary">
              {threatsByCountry["CN"]?.count || 0}
            </div>
            <div className="text-xs text-secondary">China</div>
          </div>
        </div>
        <div className="bg-secondary/90 backdrop-blur rounded-lg px-4 py-2 flex items-center gap-3">
          <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse" />
          <div>
            <div className="text-2xl font-bold text-primary">
              {threatsByCountry["KP"]?.count || 0}
            </div>
            <div className="text-xs text-secondary">North Korea</div>
          </div>
        </div>
        <div className="bg-secondary/90 backdrop-blur rounded-lg px-4 py-2 flex items-center gap-3">
          <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse" />
          <div>
            <div className="text-2xl font-bold text-primary">
              {threatsByCountry["IR"]?.count || 0}
            </div>
            <div className="text-xs text-secondary">Iran</div>
          </div>
        </div>
      </div>
    </div>
  );
}
