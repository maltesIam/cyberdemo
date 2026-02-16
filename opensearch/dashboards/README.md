# CyberDemo OpenSearch Dashboards

This directory contains pre-configured OpenSearch Dashboards for the CyberDemo SOC Analyst PoC.

## Dashboard Files

| File                            | Description                                                  |
| ------------------------------- | ------------------------------------------------------------ |
| `index-patterns.ndjson`         | Index patterns for all 17 CyberDemo indices                  |
| `soc-overview.ndjson`           | SOC Overview dashboard with KPIs and incident trends         |
| `asset-risk.ndjson`             | Asset risk analysis with heatmaps and vulnerability tables   |
| `threat-intel.ndjson`           | Threat intelligence IOC tracking and timeline                |
| `incident-investigation.ndjson` | Incident investigation with event timeline and MITRE mapping |

## Prerequisites

1. OpenSearch Dashboards running (default: http://localhost:5601)
2. CyberDemo indices created and populated with data
3. Access to Stack Management in OpenSearch Dashboards

## Import Instructions

### Method 1: Via OpenSearch Dashboards UI

1. Open OpenSearch Dashboards (http://localhost:5601)
2. Navigate to **Stack Management** > **Saved Objects**
3. Click **Import**
4. Import files in this order:
   - `index-patterns.ndjson` (required first)
   - `soc-overview.ndjson`
   - `asset-risk.ndjson`
   - `threat-intel.ndjson`
   - `incident-investigation.ndjson`
5. Select **Automatically overwrite conflicts** if updating existing objects

### Method 2: Via API (curl)

```bash
# Set your OpenSearch Dashboards URL
DASHBOARDS_URL="http://localhost:5601"

# Import index patterns first
curl -X POST "$DASHBOARDS_URL/api/saved_objects/_import?overwrite=true" \
  -H "osd-xsrf: true" \
  --form file=@index-patterns.ndjson

# Import dashboards
for file in soc-overview.ndjson asset-risk.ndjson threat-intel.ndjson incident-investigation.ndjson; do
  curl -X POST "$DASHBOARDS_URL/api/saved_objects/_import?overwrite=true" \
    -H "osd-xsrf: true" \
    --form file=@$file
done
```

### Method 3: Docker Compose (Automated)

If using the CyberDemo docker-compose setup, dashboards can be imported automatically:

```bash
# From CyberDemo directory
docker-compose exec opensearch-dashboards bash -c '
  for file in /dashboards/*.ndjson; do
    curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
      -H "osd-xsrf: true" \
      --form file=@$file
  done
'
```

## Index Patterns

The following index patterns are included:

| Pattern               | Time Field      | Description                 |
| --------------------- | --------------- | --------------------------- |
| `assets-inventory-*`  | `last_seen`     | Asset inventory data        |
| `edr-detections-*`    | `detected_at`   | EDR detection events        |
| `edr-process-trees-*` | `created_at`    | Process tree analysis       |
| `edr-hunt-results-*`  | `started_at`    | Threat hunting results      |
| `edr-host-actions-*`  | `started_at`    | Host containment actions    |
| `siem-incidents-*`    | `created_at`    | SIEM incidents              |
| `siem-entities-*`     | `last_seen`     | Entity tracking             |
| `siem-comments-*`     | `created_at`    | Incident comments           |
| `ctem-findings-*`     | `discovered_at` | CTEM vulnerability findings |
| `ctem-asset-risk-*`   | `calculated_at` | Asset risk scores           |
| `threat-intel-*`      | `first_seen`    | Threat intelligence IOCs    |
| `collab-messages-*`   | `created_at`    | Collaboration messages      |
| `approvals-*`         | `requested_at`  | Approval workflow           |
| `soar-actions-*`      | `started_at`    | SOAR automation actions     |
| `tickets-sync-*`      | `last_sync_at`  | Ticket sync status          |
| `agent-events-*`      | `created_at`    | AI agent events             |
| `postmortems-*`       | `created_at`    | Incident postmortems        |

## Dashboard Details

### SOC Overview Dashboard

**Purpose**: High-level SOC operations view

**Visualizations**:

- Total Incidents (metric)
- Critical Alerts (metric)
- Hosts Contained (metric)
- MTTR in Minutes (metric)
- Severity Distribution (pie chart)
- Incidents Over Time (line chart)
- Top 10 Affected Hosts (table)

**Default Time Range**: Last 7 days

### Asset Risk Dashboard

**Purpose**: CTEM asset risk analysis

**Visualizations**:

- Risk by Asset Type (heatmap)
- Overall Risk Score (gauge)
- Risk Level Distribution (pie chart)
- Top Vulnerable Assets (table)
- CTEM Findings by Severity (histogram)

**Default Time Range**: Last 30 days

### Threat Intelligence Dashboard

**Purpose**: IOC tracking and analysis

**Visualizations**:

- Recent IOCs (table)
- Verdict Distribution (pie chart)
- IOC Severity Distribution (pie chart)
- IOC Matches Timeline (line chart)
- IOCs by Source (horizontal bar)
- Top Malware Families (tag cloud)

**Default Time Range**: Last 30 days

### Incident Investigation Dashboard

**Purpose**: Deep-dive incident analysis

**Components**:

- Event Sequence Timeline (line chart with MITRE tactics)
- MITRE Tactics Distribution (pie chart)
- Affected Hosts (table)
- Process Activity (table)
- Investigation Comments Timeline (line chart)
- SOAR Actions (table)
- Related Detections (saved search)
- Entity Graph Reference (markdown)

**Default Time Range**: Last 24 hours

## Customization

### Modifying Visualizations

1. Open the dashboard in OpenSearch Dashboards
2. Click **Edit** mode
3. Click the gear icon on any visualization
4. Modify aggregations, filters, or visualization settings
5. Save changes

### Adding Custom Filters

Each dashboard supports filtering by:

- Time range (global)
- Severity levels
- Hostnames
- Incident IDs
- Any indexed field

### Creating New Dashboards

1. Navigate to **Dashboards** > **Create new dashboard**
2. Add visualizations from existing saved objects
3. Create new visualizations using the index patterns
4. Export your dashboard: **Stack Management** > **Saved Objects** > **Export**

## Troubleshooting

### "Index pattern not found" error

Ensure indices exist before importing:

```bash
curl -X GET "http://localhost:9200/_cat/indices?v"
```

### Visualizations show "No data"

1. Check that data has been indexed
2. Verify the time range includes data timestamps
3. Check the index pattern time field configuration

### Import fails

1. Try importing index patterns first
2. Check for conflicting object IDs
3. Use `overwrite=true` parameter

## Related Documentation

- [OpenSearch Dashboards Documentation](https://opensearch.org/docs/latest/dashboards/)
- [CyberDemo Backend API](../backend/README.md)
- [Index Templates](../backend/src/opensearch/templates.py)
