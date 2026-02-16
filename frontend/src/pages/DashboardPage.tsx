import clsx from "clsx";
import { useDashboardKPIs } from "../hooks/useApi";
import { EnrichmentButtons } from "../components/EnrichmentButtons";
import { IncidentsByHourChart } from "../components/IncidentsByHourChart";
import { DetectionTrendChart } from "../components/DetectionTrendChart";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
  trend?: { value: number; direction: "up" | "down" };
}

function KPICard({ title, value, subtitle, icon, color, trend }: KPICardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className={clsx("text-3xl font-bold mt-2", color)}>{value}</p>
          {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
          {trend && (
            <div
              className={clsx(
                "flex items-center mt-2 text-sm",
                trend.direction === "up" ? "text-red-400" : "text-green-400",
              )}
            >
              <svg
                className={clsx("w-4 h-4 mr-1", trend.direction === "down" && "rotate-180")}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
              <span>{trend.value}% from last week</span>
            </div>
          )}
        </div>
        <div
          className={clsx("p-3 rounded-lg", color.replace("text-", "bg-").replace("400", "900/50"))}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}

function SeverityDistribution({ data }: { data: { severity: string; count: number }[] }) {
  const total = data.reduce((sum, item) => sum + item.count, 0);
  const severityColors: Record<string, string> = {
    critical: "bg-red-500",
    high: "bg-orange-500",
    medium: "bg-yellow-500",
    low: "bg-green-500",
  };

  if (total === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Severity Distribution</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No incident data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Severity Distribution</h3>
      <div className="space-y-4">
        {data.map((item) => (
          <div key={item.severity}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-gray-300 capitalize">{item.severity}</span>
              <span className="text-gray-400">
                {item.count} ({((item.count / total) * 100).toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={clsx(
                  "h-2 rounded-full transition-all duration-500",
                  severityColors[item.severity] || "bg-gray-500",
                )}
                style={{ width: `${(item.count / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TopAffectedHosts({ data }: { data: { hostname: string; incident_count: number }[] }) {
  if (data.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4">Top Affected Hosts</h3>
        <div className="h-48 flex items-center justify-center text-gray-500">
          No host data available
        </div>
      </div>
    );
  }

  const maxCount = Math.max(...data.map((h) => h.incident_count));

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Top Affected Hosts</h3>
      <div className="space-y-3">
        {data.slice(0, 5).map((host, index) => (
          <div key={host.hostname} className="flex items-center space-x-3">
            <span className="text-gray-500 w-6">{index + 1}.</span>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-300 font-mono text-sm">{host.hostname}</span>
                <span className="text-gray-400 text-sm">{host.incident_count}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1.5">
                <div
                  className="bg-cyan-500 h-1.5 rounded-full"
                  style={{ width: `${(host.incident_count / maxCount) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { data: kpis, isLoading, error } = useDashboardKPIs();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <svg
            className="w-12 h-12 animate-spin text-cyan-500 mx-auto mb-4"
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
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center bg-red-900/20 border border-red-700 rounded-lg p-8">
          <svg
            className="w-12 h-12 text-red-500 mx-auto mb-4"
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
          <p className="text-red-400 font-medium">Failed to load dashboard</p>
          <p className="text-gray-500 text-sm mt-2">{error.message}</p>
        </div>
      </div>
    );
  }

  // Default values if no data
  const defaultKPIs = {
    total_incidents: 0,
    critical_open: 0,
    hosts_contained: 0,
    mttr_hours: 0,
    incidents_by_severity: [],
    incidents_by_hour: [],
    top_affected_hosts: [],
    detection_trend: [],
  };

  const data = kpis || defaultKPIs;

  return (
    <div className="space-y-6">
      {/* Header with Enrichment Buttons */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Real-time security operations overview</p>
        </div>
        <EnrichmentButtons onEnrichmentComplete={() => window.location.reload()} />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Incidents"
          value={data.total_incidents}
          subtitle="Active & resolved"
          color="text-cyan-400"
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
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          }
        />
        <KPICard
          title="Critical Open"
          value={data.critical_open}
          subtitle="Requires immediate attention"
          color="text-red-400"
          trend={{ value: 12, direction: "up" }}
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
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
        />
        <KPICard
          title="Hosts Contained"
          value={data.hosts_contained}
          subtitle="Network isolated"
          color="text-orange-400"
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
                d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
              />
            </svg>
          }
        />
        <KPICard
          title="MTTR"
          value={`${data.mttr_hours.toFixed(1)}h`}
          subtitle="Mean time to resolve"
          color="text-green-400"
          trend={{ value: 8, direction: "down" }}
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
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncidentsByHourChart data={data.incidents_by_hour} />
        <SeverityDistribution data={data.incidents_by_severity} />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopAffectedHosts data={data.top_affected_hosts} />
        <DetectionTrendChart data={data.detection_trend} />
      </div>
    </div>
  );
}
