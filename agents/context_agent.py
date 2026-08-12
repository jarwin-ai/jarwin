"""
Jarwin Context Agent
Analyzes user inputs and structures them into a context profile.
"""

INDUSTRY_MAP = {
    "healthcare": {"compliance": ["HIPAA", "SOC2"], "priority": "security"},
    "health_tech": {"compliance": ["HIPAA", "SOC2", "GDPR"], "priority": "security"},
    "fintech": {"compliance": ["PCI-DSS", "SOC2", "GDPR"], "priority": "security"},
    "banking": {"compliance": ["PCI-DSS", "SOC2", "ISO27001"], "priority": "security"},
    "ecommerce": {"compliance": ["PCI-DSS", "GDPR", "SOC2"], "priority": "scalability"},
    "saas": {"compliance": ["SOC2", "GDPR"], "priority": "scalability"},
    "enterprise_software": {"compliance": ["SOC2", "ISO27001"], "priority": "reliability"},
    "edtech": {"compliance": ["GDPR", "SOC2"], "priority": "scalability"},
    "gaming": {"compliance": ["GDPR"], "priority": "performance"},
    "social_media": {"compliance": ["GDPR"], "priority": "scalability"},
    "logistics": {"compliance": ["SOC2"], "priority": "reliability"},
    "government": {"compliance": ["ISO27001", "SOC2"], "priority": "security"},
    "retail": {"compliance": ["PCI-DSS", "GDPR"], "priority": "scalability"},
    "media": {"compliance": ["GDPR"], "priority": "scalability"},
    "other": {"compliance": ["SOC2"], "priority": "balanced"},
}

GROWTH_STAGES = ["pre-seed", "seed", "series_a", "series_b", "series_c", "growth", "enterprise"]


def analyze_context(user_inputs: dict) -> dict:
    """
    Takes raw user inputs and produces a structured context profile.
    """
    industry = user_inputs.get("industry", "other").lower().replace(" ", "_")
    industry_info = INDUSTRY_MAP.get(industry, INDUSTRY_MAP["other"])

    team_size = user_inputs.get("team_size", 5)
    monthly_users = user_inputs.get("monthly_users", 1000)
    budget_monthly = user_inputs.get("budget_monthly", 1000)
    growth_stage = user_inputs.get("growth_stage", "seed")
    regions = user_inputs.get("regions", ["us"])
    
    # Auto-detect compliance requirements
    compliance_frameworks = list(set(
        user_inputs.get("compliance", []) + industry_info["compliance"]
    ))
    
    # Add GDPR if EU regions
    eu_regions = {"eu", "uk", "de", "fr", "nl", "es", "it"}
    if any(r.lower() in eu_regions for r in regions):
        if "GDPR" not in compliance_frameworks:
            compliance_frameworks.append("GDPR")

    context = {
        "organization": {
            "industry": industry,
            "team_size": team_size,
            "growth_stage": growth_stage,
            "monthly_users": monthly_users,
            "budget_monthly_usd": budget_monthly,
            "regions": regions,
        },
        "compliance": {
            "frameworks": compliance_frameworks,
            "priority": industry_info["priority"],
        },
        "technical": {
            "existing_stack": user_inputs.get("existing_stack", []),
            "language_preferences": user_inputs.get("languages", []),
            "cloud_preference": user_inputs.get("cloud_preference", "any"),
            "uptime_requirement": user_inputs.get("uptime_sla", 99.9),
        },
        "preferences": {
            "oss_preference": user_inputs.get("oss_preference", "balanced"),
            "build_vs_buy": user_inputs.get("build_vs_buy", "balanced"),
        },
    }
    
    return context
