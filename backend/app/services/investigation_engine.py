
# from typing import Any


# CATEGORY_LABELS = {
#     "auth": "Authentication Attack",
#     "network": "Network Incident",
#     "malware": "Malware",
#     "phishing": "Phishing / Social Engineering",
# }

# INDICATOR_RULES = {
#     "auth": {
#         "failed login": "Repeated failed login attempts",
#         "brute force": "Possible brute-force activity",
#         "unusual login": "Unusual login activity",
#         "unknown ip": "Login from an unfamiliar IP address",
#         "multiple login": "Multiple login attempts",
#         "password reset": "Password reset activity",
#         "mfa": "Multi-factor authentication is relevant",
#         "privilege": "Potential privilege-related activity",
#     },
#     "network": {
#         "port scan": "Possible port scanning",
#         "port scanning": "Possible port scanning",
#         "outbound traffic": "Unusual outbound network traffic",
#         "lateral movement": "Possible lateral movement",
#         "unknown connection": "Connection to an unfamiliar destination",
#         "suspicious connection": "Suspicious network connection",
#         "data exfiltration": "Possible data exfiltration",
#     },
#     "malware": {
#         "ransomware": "Possible ransomware activity",
#         "malware": "Malware-related indicator reported",
#         "suspicious process": "Suspicious process execution",
#         "unknown executable": "Unknown executable detected",
#         "file encryption": "Unusual file encryption activity",
#         "command and control": "Possible command-and-control communication",
#     },
#     "phishing": {
#         "phishing": "Phishing-related activity reported",
#         "malicious link": "Potentially malicious link",
#         "credential harvesting": "Possible credential harvesting",
#         "suspicious attachment": "Suspicious email attachment",
#         "spoofed email": "Possible email spoofing",
#         "impersonation": "Possible sender impersonation",
#     },
# }

# HIGH_RISK_TERMS = [
#     "successful login",
#     "account compromised",
#     "account takeover",
#     "data exfiltration",
#     "ransomware",
#     "file encryption",
#     "lateral movement",
#     "administrator access",
#     "privilege escalation",
#     "credential stolen",
# ]

# MEDIUM_RISK_TERMS = [
#     "failed login",
#     "brute force",
#     "port scan",
#     "suspicious connection",
#     "malicious link",
#     "suspicious attachment",
#     "unknown executable",
#     "unusual outbound traffic",
# ]


# def analyze_incident(
#     incident_type: str,
#     title: str,
#     description: str,
#     evidence: list[str],
#     historical_context: list[dict] | None = None,
# ) -> dict[str, Any]:
#     """Analyze current evidence and attach relevant historical context.

#     Historical memories provide investigation context only. They do not
#     increase or decrease the risk score of the current incident.
#     """

#     historical_context = historical_context or []

#     text = " ".join([title, description, *evidence]).lower()

#     indicators = []

#     for keyword, explanation in INDICATOR_RULES[incident_type].items():
#         if keyword in text:
#             indicators.append(explanation)

#     high_matches = [
#         term for term in HIGH_RISK_TERMS if term in text
#     ]

#     medium_matches = [
#         term for term in MEDIUM_RISK_TERMS if term in text
#     ]

#     if high_matches:
#         severity = "HIGH"
#         risk_score = min(95, 75 + len(high_matches) * 5)
#     elif medium_matches:
#         severity = "MEDIUM"
#         risk_score = min(70, 45 + len(medium_matches) * 5)
#     else:
#         severity = "LOW"
#         risk_score = 25

#     if not indicators:
#         indicators.append(
#             "No predefined indicators matched the submitted text"
#         )

#     recommendations = [
#         "Preserve relevant logs and evidence for investigation.",
#         "Record affected users, devices, systems and timestamps.",
#         "Validate each suspected indicator before taking action.",
#     ]

#     if incident_type == "authentication":
#         recommendations.extend([
#             "Review authentication logs and source IP addresses.",
#             "Check for successful logins following repeated failures.",
#             "Consider revoking suspicious sessions and resetting affected credentials after verification.",
#         ])

#     elif incident_type == "network":
#         recommendations.extend([
#             "Review firewall, DNS and network flow logs.",
#             "Identify the source and destination of suspicious connections.",
#             "Investigate possible lateral movement or data exfiltration.",
#         ])

#     elif incident_type == "malware":
#         recommendations.extend([
#             "Preserve suspicious files and process execution details.",
#             "Review endpoint security alerts and system activity.",
#             "Consider isolating affected systems after analyst verification.",
#         ])

#     elif incident_type == "phishing":
#         recommendations.extend([
#             "Preserve the original email, headers, links and attachments.",
#             "Check whether recipients clicked links or submitted credentials.",
#             "Review affected accounts for suspicious authentication activity.",
#         ])

#     return {
#         "incident_category": CATEGORY_LABELS[incident_type],
#         "severity": severity,
#         "risk_score": risk_score,
#         "indicators": indicators,
#         "risk_factors": high_matches + medium_matches,
#         "recommendations": recommendations,
#         "analysis_method": (
#             "Rule-based evidence assessment + Hindsight historical context"
#             if historical_context
#             else "Rule-based evidence assessment"
#         ),
#         "memory_used": bool(historical_context),
#         "historical_context": historical_context[:8],
#         "historical_context_note": (
#             "Historical memories are reference material from previous "
#             "investigations. They are not proof of the current incident."
#         ),
#         "disclaimer": (
#             "This is a preliminary assessment based on submitted text. "
#             "Verify findings with actual security evidence before responding."
#         ),
#     }



from typing import Any


# Canonical category mapping.
# Supports both new frontend values and legacy database values.
CATEGORY_ALIASES = {
    "auth": "authentication",
    "authentication": "authentication",
    "network": "network",
    "malware": "malware",
    "phishing": "phishing",
}

CATEGORY_LABELS = {
    "authentication": "Authentication Attack",
    "network": "Network Incident",
    "malware": "Malware",
    "phishing": "Phishing / Social Engineering",
}

INDICATOR_RULES = {
    "authentication": {
        "failed login": "Repeated failed login attempts",
        "brute force": "Possible brute-force activity",
        "unusual login": "Unusual login activity",
        "unknown ip": "Login from an unfamiliar IP address",
        "multiple login": "Multiple login attempts",
        "password reset": "Password reset activity",
        "mfa": "Multi-factor authentication is relevant",
        "privilege": "Potential privilege-related activity",
        "impossible travel": "Impossible travel login pattern detected",
        "different countries": "Logins reported from different countries",
        "unfamiliar foreign ip": "Login from an unfamiliar foreign IP address",
    },
    "network": {
        "port scan": "Possible port scanning",
        "port scanning": "Possible port scanning",
        "outbound traffic": "Unusual outbound network traffic",
        "lateral movement": "Possible lateral movement",
        "unknown connection": "Connection to an unfamiliar destination",
        "suspicious connection": "Suspicious network connection",
        "data exfiltration": "Possible data exfiltration",
    },
    "malware": {
        "ransomware": "Possible ransomware activity",
        "malware": "Malware-related indicator reported",
        "suspicious process": "Suspicious process execution",
        "unknown executable": "Unknown executable detected",
        "file encryption": "Unusual file encryption activity",
        "command and control": "Possible command-and-control communication",
    },
    "phishing": {
        "phishing": "Phishing-related activity reported",
        "malicious link": "Potentially malicious link",
        "credential harvesting": "Possible credential harvesting",
        "suspicious attachment": "Suspicious email attachment",
        "spoofed email": "Possible email spoofing",
        "impersonation": "Possible sender impersonation",
    },
}

HIGH_RISK_TERMS = [
    "successful login",
    "account compromised",
    "account takeover",
    "data exfiltration",
    "ransomware",
    "file encryption",
    "lateral movement",
    "administrator access",
    "privilege escalation",
    "credential stolen",
    "impossible travel",
]

MEDIUM_RISK_TERMS = [
    "failed login",
    "brute force",
    "port scan",
    "suspicious connection",
    "malicious link",
    "suspicious attachment",
    "unknown executable",
    "unusual outbound traffic",
]


def analyze_incident(
    incident_type: str,
    title: str,
    description: str,
    evidence: list[str],
    historical_context: list[dict] | None = None,
) -> dict[str, Any]:

    historical_context = historical_context or []

    # Normalize category before any dictionary lookup.
    normalized_type = CATEGORY_ALIASES.get(
        incident_type.strip().lower()
    )

    if normalized_type is None:
        raise ValueError(
            f"Unsupported incident category: {incident_type}"
        )

    text = " ".join([title, description, *evidence]).lower()

    indicators = []

    for keyword, explanation in INDICATOR_RULES[normalized_type].items():
        if keyword in text:
            indicators.append(explanation)

    high_matches = [
        term for term in HIGH_RISK_TERMS if term in text
    ]

    medium_matches = [
        term for term in MEDIUM_RISK_TERMS if term in text
    ]

    if high_matches:
        severity = "HIGH"
        risk_score = min(95, 75 + len(high_matches) * 5)
    elif medium_matches:
        severity = "MEDIUM"
        risk_score = min(70, 45 + len(medium_matches) * 5)
    else:
        severity = "LOW"
        risk_score = 25

    if not indicators:
        indicators.append(
            "No predefined indicators matched the submitted text"
        )

    recommendations = [
        "Preserve relevant logs and evidence for investigation.",
        "Record affected users, devices, systems and timestamps.",
        "Validate each suspected indicator before taking action.",
    ]

    if normalized_type == "authentication":
        recommendations.extend([
            "Review authentication logs and source IP addresses.",
            "Check for successful logins following repeated failures.",
            "Consider revoking suspicious sessions and resetting affected credentials after verification.",
        ])

    elif normalized_type == "network":
        recommendations.extend([
            "Review firewall, DNS and network flow logs.",
            "Identify the source and destination of suspicious connections.",
            "Investigate possible lateral movement or data exfiltration.",
        ])

    elif normalized_type == "malware":
        recommendations.extend([
            "Preserve suspicious files and process execution details.",
            "Review endpoint security alerts and system activity.",
            "Consider isolating affected systems after analyst verification.",
        ])

    elif normalized_type == "phishing":
        recommendations.extend([
            "Preserve the original email, headers, links and attachments.",
            "Check whether recipients clicked links or submitted credentials.",
            "Review affected accounts for suspicious authentication activity.",
        ])

    return {
        "incident_category": CATEGORY_LABELS[normalized_type],
        "severity": severity,
        "risk_score": risk_score,
        "indicators": indicators,
        "risk_factors": high_matches + medium_matches,
        "recommendations": recommendations,
        "analysis_method": (
            "Rule-based evidence assessment + Hindsight historical context"
            if historical_context
            else "Rule-based evidence assessment"
        ),
        "memory_used": bool(historical_context),
        "historical_context": historical_context[:8],
        "historical_context_note": (
            "Historical memories are reference material from previous "
            "investigations. They are not proof of the current incident."
        ),
        "disclaimer": (
            "This is a preliminary assessment based on submitted text. "
            "Verify findings with actual security evidence before responding."
        ),
    }
