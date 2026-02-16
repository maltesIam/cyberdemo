"""Index templates for all 17 CyberDemo OpenSearch indices."""

from typing import Any

# List of all index names
ALL_INDICES = [
    "assets-inventory-v1",
    "edr-detections-v1",
    "edr-process-trees-v1",
    "edr-hunt-results-v1",
    "edr-host-actions-v1",
    "siem-incidents-v1",
    "siem-entities-v1",
    "siem-comments-v1",
    "ctem-findings-v1",
    "ctem-asset-risk-v1",
    "threat-intel-v1",
    "collab-messages-v1",
    "approvals-v1",
    "soar-actions-v1",
    "tickets-sync-v1",
    "agent-events-v1",
    "postmortems-v1",
]

# Index templates with mappings
INDEX_TEMPLATES: dict[str, dict[str, Any]] = {
    "assets-inventory-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "asset_id": {"type": "keyword"},
                "hostname": {"type": "keyword"},
                "ip_address": {"type": "ip"},
                "mac_address": {"type": "keyword"},
                "os": {"type": "keyword"},
                "os_version": {"type": "keyword"},
                "asset_type": {"type": "keyword"},
                "department": {"type": "keyword"},
                "owner": {"type": "keyword"},
                "location": {"type": "keyword"},
                "criticality": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "last_seen": {"type": "date"},
                "first_seen": {"type": "date"},
                "status": {"type": "keyword"},
                "agent_version": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "edr-detections-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "detection_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "hostname": {"type": "keyword"},
                "detection_type": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "confidence": {"type": "float"},
                "technique_id": {"type": "keyword"},
                "technique_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "tactic": {"type": "keyword"},
                "description": {"type": "text"},
                "process_name": {"type": "keyword"},
                "process_path": {"type": "keyword"},
                "process_hash": {"type": "keyword"},
                "parent_process": {"type": "keyword"},
                "command_line": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "user": {"type": "keyword"},
                "status": {"type": "keyword"},
                "assigned_to": {"type": "keyword"},
                "detected_at": {"type": "date"},
                "resolved_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "edr-process-trees-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "tree_id": {"type": "keyword"},
                "detection_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "root_process_id": {"type": "keyword"},
                "processes": {
                    "type": "nested",
                    "properties": {
                        "process_id": {"type": "keyword"},
                        "parent_id": {"type": "keyword"},
                        "name": {"type": "keyword"},
                        "path": {"type": "keyword"},
                        "command_line": {"type": "text"},
                        "user": {"type": "keyword"},
                        "start_time": {"type": "date"},
                        "end_time": {"type": "date"},
                        "hash_sha256": {"type": "keyword"},
                    }
                },
                "created_at": {"type": "date"},
            }
        },
    },
    "edr-hunt-results-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "hunt_id": {"type": "keyword"},
                "hunt_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "query": {"type": "text"},
                "status": {"type": "keyword"},
                "started_by": {"type": "keyword"},
                "started_at": {"type": "date"},
                "completed_at": {"type": "date"},
                "total_hosts_scanned": {"type": "integer"},
                "hosts_with_matches": {"type": "integer"},
                "matches": {
                    "type": "nested",
                    "properties": {
                        "asset_id": {"type": "keyword"},
                        "hostname": {"type": "keyword"},
                        "match_details": {"type": "text"},
                        "matched_at": {"type": "date"},
                    }
                },
                "created_at": {"type": "date"},
            }
        },
    },
    "edr-host-actions-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "action_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "hostname": {"type": "keyword"},
                "action_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "initiated_by": {"type": "keyword"},
                "reason": {"type": "text"},
                "detection_id": {"type": "keyword"},
                "parameters": {"type": "object", "enabled": False},
                "result": {"type": "object", "enabled": False},
                "started_at": {"type": "date"},
                "completed_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "siem-incidents-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "incident_id": {"type": "keyword"},
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "description": {"type": "text"},
                "severity": {"type": "keyword"},
                "status": {"type": "keyword"},
                "priority": {"type": "keyword"},
                "category": {"type": "keyword"},
                "source": {"type": "keyword"},
                "assigned_to": {"type": "keyword"},
                "detection_ids": {"type": "keyword"},
                "asset_ids": {"type": "keyword"},
                "entity_ids": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "ttd_minutes": {"type": "integer"},
                "ttr_minutes": {"type": "integer"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "resolved_at": {"type": "date"},
                "closed_at": {"type": "date"},
            }
        },
    },
    "siem-entities-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "entity_id": {"type": "keyword"},
                "entity_type": {"type": "keyword"},
                "entity_value": {"type": "keyword"},
                "risk_score": {"type": "float"},
                "first_seen": {"type": "date"},
                "last_seen": {"type": "date"},
                "incident_ids": {"type": "keyword"},
                "detection_ids": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "enrichment": {"type": "object", "enabled": False},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "siem-comments-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "comment_id": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "author": {"type": "keyword"},
                "author_type": {"type": "keyword"},
                "content": {"type": "text"},
                "attachments": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "ctem-findings-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "finding_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "hostname": {"type": "keyword"},
                "finding_type": {"type": "keyword"},
                "cve_id": {"type": "keyword"},
                "cvss_score": {"type": "float"},
                "severity": {"type": "keyword"},
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "description": {"type": "text"},
                "remediation": {"type": "text"},
                "status": {"type": "keyword"},
                "exploitable": {"type": "boolean"},
                "exploit_available": {"type": "boolean"},
                "discovered_at": {"type": "date"},
                "remediated_at": {"type": "date"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "ctem-asset-risk-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "risk_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "hostname": {"type": "keyword"},
                "risk_score": {"type": "float"},
                "risk_level": {"type": "keyword"},
                "vulnerability_count": {"type": "integer"},
                "critical_count": {"type": "integer"},
                "high_count": {"type": "integer"},
                "medium_count": {"type": "integer"},
                "low_count": {"type": "integer"},
                "exposure_score": {"type": "float"},
                "attack_surface_score": {"type": "float"},
                "compliance_score": {"type": "float"},
                "calculated_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "threat-intel-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "intel_id": {"type": "keyword"},
                "indicator_type": {"type": "keyword"},
                "indicator_value": {"type": "keyword"},
                "threat_type": {"type": "keyword"},
                "malware_family": {"type": "keyword"},
                "confidence": {"type": "float"},
                "severity": {"type": "keyword"},
                "source": {"type": "keyword"},
                "description": {"type": "text"},
                "tags": {"type": "keyword"},
                "ttl_days": {"type": "integer"},
                "first_seen": {"type": "date"},
                "last_seen": {"type": "date"},
                "expires_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "collab-messages-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "message_id": {"type": "keyword"},
                "channel": {"type": "keyword"},
                "channel_id": {"type": "keyword"},
                "thread_id": {"type": "keyword"},
                "author": {"type": "keyword"},
                "author_type": {"type": "keyword"},
                "content": {"type": "text"},
                "mentions": {"type": "keyword"},
                "incident_ids": {"type": "keyword"},
                "attachments": {"type": "keyword"},
                "reactions": {"type": "object", "enabled": False},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "approvals-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "approval_id": {"type": "keyword"},
                "request_type": {"type": "keyword"},
                "requestor": {"type": "keyword"},
                "approvers": {"type": "keyword"},
                "status": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "action_type": {"type": "keyword"},
                "reason": {"type": "text"},
                "decision": {"type": "keyword"},
                "decided_by": {"type": "keyword"},
                "decision_reason": {"type": "text"},
                "requested_at": {"type": "date"},
                "decided_at": {"type": "date"},
                "expires_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "soar-actions-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "action_id": {"type": "keyword"},
                "playbook_id": {"type": "keyword"},
                "playbook_name": {"type": "keyword"},
                "action_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "detection_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "input_params": {"type": "object", "enabled": False},
                "output_result": {"type": "object", "enabled": False},
                "error_message": {"type": "text"},
                "triggered_by": {"type": "keyword"},
                "started_at": {"type": "date"},
                "completed_at": {"type": "date"},
                "created_at": {"type": "date"},
            }
        },
    },
    "tickets-sync-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "sync_id": {"type": "keyword"},
                "ticket_system": {"type": "keyword"},
                "ticket_id": {"type": "keyword"},
                "ticket_key": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "status": {"type": "keyword"},
                "ticket_status": {"type": "keyword"},
                "sync_direction": {"type": "keyword"},
                "last_sync_at": {"type": "date"},
                "error_message": {"type": "text"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    },
    "agent-events-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "event_id": {"type": "keyword"},
                "agent_id": {"type": "keyword"},
                "event_type": {"type": "keyword"},
                "action": {"type": "keyword"},
                "status": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "detection_id": {"type": "keyword"},
                "asset_id": {"type": "keyword"},
                "input_summary": {"type": "text"},
                "output_summary": {"type": "text"},
                "reasoning": {"type": "text"},
                "confidence": {"type": "float"},
                "duration_ms": {"type": "integer"},
                "tokens_used": {"type": "integer"},
                "error_message": {"type": "text"},
                "created_at": {"type": "date"},
            }
        },
    },
    "postmortems-v1": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        },
        "mappings": {
            "properties": {
                "postmortem_id": {"type": "keyword"},
                "incident_id": {"type": "keyword"},
                "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "summary": {"type": "text"},
                "impact": {"type": "text"},
                "root_cause": {"type": "text"},
                "timeline": {
                    "type": "nested",
                    "properties": {
                        "timestamp": {"type": "date"},
                        "event": {"type": "text"},
                        "actor": {"type": "keyword"},
                    }
                },
                "lessons_learned": {"type": "text"},
                "action_items": {
                    "type": "nested",
                    "properties": {
                        "item_id": {"type": "keyword"},
                        "description": {"type": "text"},
                        "owner": {"type": "keyword"},
                        "due_date": {"type": "date"},
                        "status": {"type": "keyword"},
                    }
                },
                "participants": {"type": "keyword"},
                "status": {"type": "keyword"},
                "created_by": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
                "published_at": {"type": "date"},
            }
        },
    },
}
