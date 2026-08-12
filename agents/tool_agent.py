"""
Jarwin Tool Agent (Dual-Path Decision Engine)
Recommends OSS and Licensed tools for each component with TCO comparison.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_PATH = os.path.join(BASE_DIR, "knowledge_base", "tools", "tool_database.json")


def load_tools():
    with open(TOOLS_PATH, "r") as f:
        return json.load(f)


def calculate_tco_monthly(tool: dict, context: dict, months: int = 36) -> dict:
    """Calculate Total Cost of Ownership for a tool over given months."""
    team_size = context["organization"]["team_size"]
    
    # Direct costs
    direct_monthly = tool.get("min_cost_monthly", 0)
    
    # Operational cost (based on learning curve and team)
    learning_curve = tool.get("learning_curve", 0.5)
    ops_monthly = learning_curve * 500 * (team_size / 20)  # rough estimate
    
    # Infrastructure cost for self-hosted OSS
    if tool["type"] == "oss" and tool["pricing"] == "free":
        infra_monthly = 50 + (team_size * 5)  # server costs to run it
    else:
        infra_monthly = 0  # included in license
    
    total_monthly = direct_monthly + ops_monthly + infra_monthly
    total_over_period = total_monthly * months
    
    return {
        "direct_monthly": round(direct_monthly, 2),
        "operational_monthly": round(ops_monthly, 2),
        "infrastructure_monthly": round(infra_monthly, 2),
        "total_monthly": round(total_monthly, 2),
        "total_36_months": round(total_over_period, 2),
    }


def score_tool(tool: dict, context: dict, category: str) -> float:
    """Score a tool based on context fit (0-1)."""
    score = 0.0
    
    # Compliance fit (30% weight)
    required_compliance = context["compliance"]["frameworks"]
    tool_compliance = tool.get("compliance", [])
    if required_compliance:
        compliance_match = len(set(required_compliance) & set(tool_compliance)) / len(required_compliance)
    else:
        compliance_match = 1.0
    score += 0.30 * compliance_match
    
    # Scalability fit (20% weight)
    scalability_map = {"low": 0.25, "medium": 0.5, "high": 0.75, "very_high": 1.0}
    scalability = scalability_map.get(tool.get("scalability", "medium"), 0.5)
    score += 0.20 * scalability
    
    # Learning curve (inverse - easier = better) (15% weight)
    learning = 1.0 - tool.get("learning_curve", 0.5)
    score += 0.15 * learning
    
    # Community/Vendor health (20% weight)
    if tool["type"] == "oss":
        health = tool.get("community_health", 0.7)
    else:
        health = tool.get("vendor_health", 0.7)
    score += 0.20 * health
    
    # Cost efficiency (15% weight)
    budget = context["organization"]["budget_monthly_usd"]
    cost = tool.get("min_cost_monthly", 0)
    if budget > 0:
        cost_ratio = 1.0 - min(cost / budget, 1.0)
    else:
        cost_ratio = 1.0 if cost == 0 else 0.0
    score += 0.15 * cost_ratio
    
    return round(score, 3)


def get_pros_cons(tool: dict) -> tuple:
    """Generate pros and cons for a tool."""
    pros = []
    cons = []
    
    if tool["type"] == "oss":
        pros.append("No licensing costs")
        pros.append("Full source code access and customization")
        if tool.get("community_health", 0) > 0.85:
            pros.append("Strong community support")
        if tool.get("github_stars", 0) > 30000:
            pros.append("Widely adopted and battle-tested")
        cons.append("Self-managed: you handle updates, security patches")
        if tool.get("learning_curve", 0) > 0.6:
            cons.append("Steep learning curve")
        if not tool.get("compliance", []):
            cons.append("No built-in compliance certifications")
    else:
        if tool.get("compliance", []):
            pros.append(f"Certified: {', '.join(tool['compliance'])}")
        pros.append("Managed service: vendor handles operations")
        if tool.get("learning_curve", 0) < 0.4:
            pros.append("Easy to set up and use")
        cons.append(f"Ongoing cost: ${tool.get('min_cost_monthly', 0)}/month minimum")
        cons.append("Vendor lock-in risk")
        if tool.get("vendor_health", 0) < 0.85:
            cons.append("Smaller vendor - stability risk")
    
    return pros[:3], cons[:3]


def recommend_tools(context: dict, maturity_result: dict) -> list:
    """
    For each phase, recommend tools for required components.
    Returns dual-path recommendations (OSS vs Licensed).
    """
    db = load_tools()
    all_recommendations = []
    
    for phase in maturity_result["phases"]:
        phase_recommendations = {
            "phase": phase["phase"],
            "level": phase["level"],
            "name": phase["name"],
            "components": []
        }
        
        for component in phase["required_components"]:
            # Find the component in our database
            component_tools = None
            component_category = None
            for layer, categories in db["categories"].items():
                if component in categories:
                    component_tools = categories[component]["tools"]
                    component_category = categories[component]["description"]
                    break
            
            if not component_tools:
                continue
            
            # Filter tools by maturity level
            eligible_tools = [
                t for t in component_tools 
                if t.get("maturity_min", 1) <= phase["level"]
            ]
            
            # Split into OSS and Licensed
            oss_tools = [t for t in eligible_tools if t["type"] == "oss"]
            lic_tools = [t for t in eligible_tools if t["type"] == "licensed"]
            
            # Score and rank
            oss_scored = [(t, score_tool(t, context, component)) for t in oss_tools]
            lic_scored = [(t, score_tool(t, context, component)) for t in lic_tools]
            
            oss_scored.sort(key=lambda x: x[1], reverse=True)
            lic_scored.sort(key=lambda x: x[1], reverse=True)
            
            # Get top recommendations
            oss_primary = oss_scored[0] if oss_scored else None
            lic_primary = lic_scored[0] if lic_scored else None
            
            recommendation = {
                "component": component,
                "description": component_category,
            }
            
            if oss_primary:
                oss_pros, oss_cons = get_pros_cons(oss_primary[0])
                recommendation["oss_recommendation"] = {
                    "name": oss_primary[0]["name"],
                    "score": oss_primary[1],
                    "tco": calculate_tco_monthly(oss_primary[0], context),
                    "pros": oss_pros,
                    "cons": oss_cons,
                    "license": oss_primary[0].get("license", ""),
                    "alternatives": [t[0]["name"] for t in oss_scored[1:3]],
                }
            
            if lic_primary:
                lic_pros, lic_cons = get_pros_cons(lic_primary[0])
                recommendation["licensed_recommendation"] = {
                    "name": lic_primary[0]["name"],
                    "score": lic_primary[1],
                    "tco": calculate_tco_monthly(lic_primary[0], context),
                    "pros": lic_pros,
                    "cons": lic_cons,
                    "alternatives": [t[0]["name"] for t in lic_scored[1:3]],
                }
            
            # Overall recommendation
            if oss_primary and lic_primary:
                oss_score = oss_primary[1]
                lic_score = lic_primary[1]
                if oss_score > lic_score * 1.1:
                    recommendation["verdict"] = "OSS"
                    recommendation["rationale"] = f"{oss_primary[0]['name']} offers better value with strong community support and lower TCO for your context."
                elif lic_score > oss_score * 1.1:
                    recommendation["verdict"] = "LICENSED"
                    recommendation["rationale"] = f"{lic_primary[0]['name']} provides compliance certifications and managed operations that match your needs."
                else:
                    recommendation["verdict"] = "EITHER"
                    recommendation["rationale"] = "Both paths are viable. Choose based on team expertise and operational preference."
            elif oss_primary:
                recommendation["verdict"] = "OSS"
                recommendation["rationale"] = f"Only open-source options available. {oss_primary[0]['name']} is the best fit."
            elif lic_primary:
                recommendation["verdict"] = "LICENSED"
                recommendation["rationale"] = f"Only licensed options available. {lic_primary[0]['name']} is the best fit."
            
            phase_recommendations["components"].append(recommendation)
        
        all_recommendations.append(phase_recommendations)
    
    return all_recommendations
