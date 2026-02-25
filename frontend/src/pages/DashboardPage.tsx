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
  colorVar: string;
  trend?: { value: number; direction: "up" | "down" };
}

function KPICard({ title, value, subtitle, icon, colorVar, trend }: KPICardProps) {
  return (
    <div className="bg-secondary rounded-lg p-6 border border-primary">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-secondary text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2" style={{ color: `var(${colorVar})` }}>{value}</p>
          {subtitle && <p className="text-tertiary text-sm mt-1">{subtitle}</p>}
          {trend && (
            <div
              className="flex items-center mt-2 text-sm"
              style={{ color: trend.direction === "up" ? 'var(--color-error)' : 'var(--color-success)' }}
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
          className="p-3 rounded-lg"
          style={{ backgroundColor: `color-mix(in srgb, var(${colorVar}), transparent 80%)` }}
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
    critical: "bg-[var(--soc-red)]",
    high: "bg-[var(--soc-orange)]",
    medium: "bg-[var(--soc-yellow)]",
    low: "bg-[var(--color-success)]",
  };

  if (total === 0) {
    return (
      <div className="bg-secondary rounded-lg p-6 border border-primary">
        <h3 className="text-lg font-semibold text-primary mb-4">Severity Distribution</h3>
        <div className="h-64 flex items-center justify-center text-tertiary">
          No incident data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-secondary rounded-lg p-6 border border-primary">
      <h3 className="text-lg font-semibold text-primary mb-4">Severity Distribution</h3>
      <div className="space-y-4">
        {data.map((item) => (
          <div key={item.severity}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-secondary capitalize">{item.severity}</span>
              <span className="text-secondary">
                {item.count} ({((item.count / total) * 100).toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-tertiary rounded-full h-2">
              <div
                className={clsx(
                  "h-2 rounded-full transition-all duration-500",
                  severityColors[item.severity] || "bg-tertiary",
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
      <div className="bg-secondary rounded-lg p-6 border border-primary">
        <h3 className="text-lg font-semibold text-primary mb-4">Top Affected Hosts</h3>
        <div className="h-48 flex items-center justify-center text-tertiary">
          No host data available
        </div>
      </div>
    );
  }

  const maxCount = Math.max(...data.map((h) => h.incident_count));

  return (
    <div className="bg-secondary rounded-lg p-6 border border-primary">
      <h3 className="text-lg font-semibold text-primary mb-4">Top Affected Hosts</h3>
      <div className="space-y-3">
        {data.slice(0, 5).map((host, index) => (
          <div key={host.hostname} className="flex items-center space-x-3">
            <span className="text-tertiary w-6">{index + 1}.</span>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-secondary font-mono text-sm">{host.hostname}</span>
                <span className="text-secondary text-sm">{host.incident_count}</span>
              </div>
              <div className="w-full bg-tertiary rounded-full h-1.5">
                <div
                  className="bg-[var(--primary)] h-1.5 rounded-full"
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
            className="w-12 h-12 animate-spin text-[var(--primary)] mx-auto mb-4"
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
          <p className="text-secondary">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center rounded-lg p-8 border border-[var(--color-error)]" style={{ backgroundColor: 'color-mix(in srgb, var(--color-error-dark), transparent 80%)' }}>
          <svg
            className="w-12 h-12 mx-auto mb-4" style={{ color: 'var(--color-error)' }}
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
          <p className="font-medium" style={{ color: 'var(--color-error)' }}>Failed to load dashboard</p>
          <p className="text-tertiary text-sm mt-2">{error.message}</p>
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
          <h1 className="text-2xl font-bold text-primary">Dashboard</h1>
          <p className="text-secondary mt-1">Real-time security operations overview</p>
        </div>
        <EnrichmentButtons onEnrichmentComplete={() => window.location.reload()} />
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Incidents"
          value={data.total_incidents}
          subtitle="Active & resolved"
          colorVar="--color-info"
          icon={
            <svg
              className="w-6 h-6"
              style={{ color: 'var(--color-info)' }}
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
          colorVar="--color-error"
          trend={{ value: 12, direction: "up" }}
          icon={
            <svg
              className="w-6 h-6"
              style={{ color: 'var(--color-error)' }}
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
          colorVar="--color-warning"
          icon={
            <svg
              className="w-6 h-6"
              style={{ color: 'var(--color-warning)' }}
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
          colorVar="--color-success"
          trend={{ value: 8, direction: "down" }}
          icon={
            <svg
              className="w-6 h-6"
              style={{ color: 'var(--color-success)' }}
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
