"""
aIP Assist MCP Tools.

Tools for the aIP Assist system that provides proactive assistance to users:
- aip_get_suggestion: Get contextual suggestions (REQ-004-002-001)
- aip_explain_why: Explain why a suggestion is relevant (REQ-004-002-002)
- aip_auto_complete: Auto-complete inputs (REQ-004-002-003)

aIP = Artificial Intelligence Person

These tools enable the product to provide intelligent, context-aware
suggestions to users during their work (investigations, diagnoses, etc.).
"""

from typing import Any, Dict, List
from datetime import datetime, timezone


# =============================================================================
# Tool Definitions
# =============================================================================

AIP_ASSIST_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "aip_get_suggestion",
        "description": """Get contextual suggestions based on the user's current context.

Returns a list of suggested actions with descriptions, confidence scores,
and reasoning. Suggestions are ordered by relevance and confidence.

Use this to provide proactive assistance during user tasks.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "object",
                    "description": "Context including page, selected_entity, recent_actions",
                    "properties": {
                        "page": {
                            "type": "string",
                            "description": "Current page/view (alerts, dashboard, etc)"
                        },
                        "selected_entity": {
                            "type": "string",
                            "description": "Currently selected entity ID (optional)"
                        },
                        "recent_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of recent actions"
                        }
                    }
                }
            },
            "required": ["context"]
        }
    },
    {
        "name": "aip_explain_why",
        "description": """Explain why a specific action is being suggested.

Returns detailed explanation with evidence, confidence score,
and alternative actions that were considered.

Use this when the user wants to understand the reasoning behind a suggestion.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to explain"
                },
                "context": {
                    "type": "object",
                    "description": "Context in which the action was suggested"
                }
            },
            "required": ["action", "context"]
        }
    },
    {
        "name": "aip_auto_complete",
        "description": """Auto-complete partial input based on field type and context.

Returns possible completions with confidence scores and sources.
Supports IP addresses, hostnames, usernames, and hashes.

Use this to speed up data entry during user tasks.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "partial_input": {
                    "type": "string",
                    "description": "The partial text to complete"
                },
                "field_type": {
                    "type": "string",
                    "enum": ["ip_address", "hostname", "username", "hash", "domain"],
                    "description": "Type of field being completed"
                },
                "context": {
                    "type": "object",
                    "description": "Current context for relevance scoring"
                }
            },
            "required": ["partial_input", "field_type"]
        }
    },
]


# =============================================================================
# Mock Data Stores
# =============================================================================

# Known hostnames in the system
KNOWN_HOSTNAMES: List[str] = [
    "WS-FIN-001",
    "WS-FIN-042",
    "WS-FIN-050",
    "WS-HR-015",
    "WS-HR-022",
    "SRV-DC-01",
    "SRV-DB-01",
    "SRV-WEB-01",
    "SRV-DEV-03",
    "SRV-FILE-01",
]

# Known usernames in the system
KNOWN_USERNAMES: List[str] = [
    "DOMAIN\\admin",
    "DOMAIN\\admin_backup",
    "DOMAIN\\finance_user",
    "DOMAIN\\hr_user",
    "DOMAIN\\dev_user",
    "DOMAIN\\it_support",
    "DOMAIN\\security_analyst",
]

# Known IP addresses from recent events
KNOWN_IPS: List[str] = [
    "192.168.1.10",
    "192.168.1.42",
    "192.168.1.50",
    "192.168.100.50",
    "10.0.0.1",
    "10.0.0.100",
    "185.234.72.199",
    "185.234.72.200",
    "185.234.72.201",
]

# Known hashes from IOC database
KNOWN_HASHES: List[str] = [
    "abc123def456789abcdef123456789ab",
    "def456789abc123def456789abc123de",
    "abc123def456789",
    "1234567890abcdef1234567890abcdef",
]

# Suggestion templates based on page and context
SUGGESTION_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "alerts": [
        {
            "action": "analyze_alert",
            "description": "Run AI analysis on the selected alert",
            "base_confidence": 0.90,
            "reasoning": "The selected alert appears to require investigation"
        },
        {
            "action": "investigate_related_iocs",
            "description": "Investigate IOCs associated with this alert",
            "base_confidence": 0.85,
            "reasoning": "Alert contains indicators that can be enriched"
        },
        {
            "action": "correlate_with_similar",
            "description": "Find similar alerts in the last 24 hours",
            "base_confidence": 0.80,
            "reasoning": "There may be related activity to investigate"
        },
        {
            "action": "contain_host",
            "description": "Isolate the affected host from the network",
            "base_confidence": 0.70,
            "reasoning": "If confirmed malicious, containment prevents spread"
        },
    ],
    "dashboard": [
        {
            "action": "review_critical_alerts",
            "description": "Review the critical alerts requiring attention",
            "base_confidence": 0.85,
            "reasoning": "Critical alerts should be addressed first"
        },
        {
            "action": "check_threat_intel",
            "description": "Review latest threat intelligence updates",
            "base_confidence": 0.75,
            "reasoning": "Stay updated on emerging threats"
        },
    ],
    "ioc_search": [
        {
            "action": "enrich_ioc",
            "description": "Enrich the selected IOC with threat intelligence",
            "base_confidence": 0.90,
            "reasoning": "Additional context helps assess threat level"
        },
        {
            "action": "search_related",
            "description": "Search for related indicators",
            "base_confidence": 0.80,
            "reasoning": "IOCs are often part of larger campaigns"
        },
    ],
    "incident": [
        {
            "action": "generate_report",
            "description": "Generate an incident report for stakeholders",
            "base_confidence": 0.85,
            "reasoning": "Documentation is essential for compliance and learning"
        },
        {
            "action": "execute_playbook",
            "description": "Execute a response playbook for this incident type",
            "base_confidence": 0.80,
            "reasoning": "Standardized response ensures consistent handling"
        },
    ],
}

# Action explanation templates
ACTION_EXPLANATIONS: Dict[str, Dict[str, Any]] = {
    "analyze_alert": {
        "explanation": "Analyzing this alert will provide threat assessment, MITRE ATT&CK mapping, and recommended actions. The AI agent will examine the alert details, correlate with threat intelligence, and assess the risk level.",
        "evidence": [
            "Alert severity indicates potential threat",
            "Alert type matches known attack patterns",
            "Historical data shows similar alerts led to incidents"
        ],
        "confidence": 0.90,
        "alternatives": [
            {"action": "mark_as_false_positive", "reason": "If you're confident this is benign"},
            {"action": "escalate_to_tier2", "reason": "If you need additional expertise"}
        ]
    },
    "investigate_ioc": {
        "explanation": "Investigating this IOC will enrich it with threat intelligence data including reputation, geographic information, and related indicators. This helps determine if it's malicious.",
        "evidence": [
            "IOC appears in alert context",
            "Enrichment provides threat context",
            "Related indicators may reveal campaign"
        ],
        "confidence": 0.85,
        "alternatives": [
            {"action": "block_ioc", "reason": "If confirmed malicious"},
            {"action": "add_to_watchlist", "reason": "For ongoing monitoring"}
        ]
    },
    "contain_host": {
        "explanation": "Containing this host will isolate it from the network to prevent lateral movement and data exfiltration. This is recommended when malicious activity is confirmed or highly likely.",
        "evidence": [
            "Host shows signs of compromise",
            "Containment prevents spread",
            "Business impact is acceptable"
        ],
        "confidence": 0.75,
        "alternatives": [
            {"action": "monitor_closely", "reason": "If more investigation is needed"},
            {"action": "collect_forensics", "reason": "Before containment destroys evidence"}
        ]
    },
    "investigate_related_iocs": {
        "explanation": "Investigating related IOCs will help identify the full scope of the threat by examining associated indicators. This can reveal attack infrastructure and campaign details.",
        "evidence": [
            "IOCs often appear in clusters",
            "Campaign context improves response",
            "Related indicators may be blocking candidates"
        ],
        "confidence": 0.85,
        "alternatives": [
            {"action": "search_historical", "reason": "To find past occurrences"},
            {"action": "check_threat_feeds", "reason": "For external intelligence"}
        ]
    },
    "correlate_with_similar": {
        "explanation": "Correlating with similar alerts helps identify patterns and potential attack campaigns. This analysis can reveal coordinated activity across multiple hosts or time periods.",
        "evidence": [
            "Similar alerts may indicate campaign",
            "Correlation improves detection accuracy",
            "Pattern analysis aids investigation"
        ],
        "confidence": 0.80,
        "alternatives": [
            {"action": "expand_time_range", "reason": "To find older related activity"},
            {"action": "narrow_to_host", "reason": "To focus on single system"}
        ]
    },
}


# =============================================================================
# Tool Handlers
# =============================================================================

async def handle_aip_get_suggestion(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle aip_get_suggestion tool call (REQ-004-002-001).

    Returns contextual suggestions based on the user's current context
    including page, selected entity, and recent actions.

    Args:
        args: Dictionary with context object

    Returns:
        Dictionary with suggestions ordered by confidence

    Raises:
        ValueError: If context is not provided
    """
    context = args.get("context")

    if not context:
        raise ValueError("context is required")

    page = context.get("page", "dashboard")
    selected_entity = context.get("selected_entity")
    recent_actions = context.get("recent_actions", [])

    # Get suggestions based on current page
    templates = SUGGESTION_TEMPLATES.get(page, SUGGESTION_TEMPLATES["dashboard"])

    suggestions = []
    for template in templates:
        confidence = template["base_confidence"]

        # Adjust confidence based on context
        if selected_entity and "analyze" in template["action"]:
            confidence = min(confidence + 0.05, 1.0)

        if recent_actions:
            # Boost suggestions that follow recent actions logically
            if "view_alert" in recent_actions and "analyze" in template["action"]:
                confidence = min(confidence + 0.05, 1.0)
            if "analyze" in str(recent_actions) and "contain" in template["action"]:
                confidence = min(confidence + 0.03, 1.0)

        suggestions.append({
            "action": template["action"],
            "description": template["description"],
            "confidence": round(confidence, 2),
            "reasoning": template["reasoning"]
        })

    # Sort by confidence (highest first)
    suggestions.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "suggestions": suggestions,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


async def handle_aip_explain_why(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle aip_explain_why tool call (REQ-004-002-002).

    Returns detailed explanation for why a specific action is suggested
    including evidence, confidence, and alternatives.

    Args:
        args: Dictionary with action and context

    Returns:
        Dictionary with explanation details

    Raises:
        ValueError: If action or context is not provided
    """
    action = args.get("action")
    context = args.get("context")

    if not action:
        raise ValueError("action is required")
    if not context:
        raise ValueError("context is required")

    # Get explanation template for this action
    explanation_data = ACTION_EXPLANATIONS.get(action)

    if explanation_data:
        return {
            "explanation": explanation_data["explanation"],
            "evidence": explanation_data["evidence"],
            "confidence": explanation_data["confidence"],
            "alternatives": explanation_data["alternatives"]
        }

    # Generate generic explanation for unknown actions
    return {
        "explanation": f"The action '{action}' is suggested based on the current context. "
                       f"You are on the '{context.get('page', 'unknown')}' page "
                       f"and may benefit from this action to progress your task.",
        "evidence": [
            f"Current page context: {context.get('page', 'unknown')}",
            f"Selected entity: {context.get('selected_entity', 'none')}",
            "Action aligns with standard workflow"
        ],
        "confidence": 0.70,
        "alternatives": [
            {"action": "skip_suggestion", "reason": "If not applicable to current task"},
            {"action": "ask_for_help", "reason": "If you need guidance"}
        ]
    }


async def handle_aip_auto_complete(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle aip_auto_complete tool call (REQ-004-002-003).

    Returns auto-complete suggestions for partial input based on
    field type and context.

    Args:
        args: Dictionary with partial_input, field_type, and context

    Returns:
        Dictionary with completions ordered by confidence

    Raises:
        ValueError: If partial_input or field_type is not provided
    """
    partial_input = args.get("partial_input")
    field_type = args.get("field_type")
    context = args.get("context", {})

    if not partial_input:
        raise ValueError("partial_input is required")
    if not field_type:
        raise ValueError("field_type is required")

    completions = []

    # Get candidates based on field type
    if field_type == "ip_address":
        candidates = KNOWN_IPS
        source = "recent_events"
    elif field_type == "hostname":
        candidates = KNOWN_HOSTNAMES
        source = "asset_inventory"
    elif field_type == "username":
        candidates = KNOWN_USERNAMES
        source = "directory"
    elif field_type == "hash":
        candidates = KNOWN_HASHES
        source = "known_iocs"
    elif field_type == "domain":
        candidates = ["malware-c2.evil.com", "solarwinds-update.evil.com"]
        source = "threat_intel"
    else:
        candidates = []
        source = "unknown"

    # Filter candidates that start with partial input
    partial_lower = partial_input.lower()
    for candidate in candidates:
        if candidate.lower().startswith(partial_lower):
            # Calculate confidence based on match quality
            match_ratio = len(partial_input) / len(candidate)
            confidence = min(0.5 + (match_ratio * 0.5), 0.99)

            completions.append({
                "value": candidate,
                "confidence": round(confidence, 2),
                "source": source
            })

    # Sort by confidence (highest first)
    completions.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "completions": completions
    }


# =============================================================================
# Handler Mapping
# =============================================================================

aip_assist_handlers = {
    "aip_get_suggestion": handle_aip_get_suggestion,
    "aip_explain_why": handle_aip_explain_why,
    "aip_auto_complete": handle_aip_auto_complete,
}


# =============================================================================
# Backwards Compatibility Aliases
# =============================================================================

COPILOT_TOOLS = AIP_ASSIST_TOOLS
copilot_handlers = aip_assist_handlers
handle_copilot_get_suggestion = handle_aip_get_suggestion
handle_copilot_explain_why = handle_aip_explain_why
handle_copilot_auto_complete = handle_aip_auto_complete
