"""
Jarwin Blueprint Agent
Assembles final architecture blueprint with cost projections and roadmap.
"""


def calculate_cost_summary(recommendations: list, context: dict) -> dict:
    """Calculate total cost projections for OSS and Licensed paths."""
    oss_total_monthly = 0
    lic_total_monthly = 0
    recommended_total_monthly = 0
    
    # Use the last phase (target) for cost calculation
    if not recommendations:
        return {"oss_monthly": 0, "licensed_monthly": 0, "recommended_monthly": 0}
    
    target_phase = recommendations[-1]
    
    for component in target_phase["components"]:
        oss_rec = component.get("oss_recommendation", {})
        lic_rec = component.get("licensed_recommendation", {})
        verdict = component.get("verdict", "EITHER")
        
        oss_cost = oss_rec.get("tco", {}).get("total_monthly", 0) if oss_rec else 0
        lic_cost = lic_rec.get("tco", {}).get("total_monthly", 0) if lic_rec else 0
        
        oss_total_monthly += oss_cost
        lic_total_monthly += lic_cost
        
        if verdict == "OSS":
            recommended_total_monthly += oss_cost
        elif verdict == "LICENSED":
            recommended_total_monthly += lic_cost
        else:
            recommended_total_monthly += min(oss_cost, lic_cost)
    
    return {
        "oss_path": {
            "monthly": round(oss_total_monthly, 2),
            "annual": round(oss_total_monthly * 12, 2),
            "three_year": round(oss_total_monthly * 36, 2),
        },
        "licensed_path": {
            "monthly": round(lic_total_monthly, 2),
            "annual": round(lic_total_monthly * 12, 2),
            "three_year": round(lic_total_monthly * 36, 2),
        },
        "recommended_path": {
            "monthly": round(recommended_total_monthly, 2),
            "annual": round(recommended_total_monthly * 12, 2),
            "three_year": round(recommended_total_monthly * 36, 2),
        },
        "savings_vs_licensed": {
            "monthly": round(lic_total_monthly - recommended_total_monthly, 2),
            "annual": round((lic_total_monthly - recommended_total_monthly) * 12, 2),
        }
    }


def generate_blueprint(context: dict, maturity: dict, recommendations: list, compliance: dict) -> dict:
    """
    Generate the final architecture blueprint combining all agent outputs.
    """
    cost_summary = calculate_cost_summary(recommendations, context)
    
    blueprint = {
        "metadata": {
            "generated_for": context["organization"]["industry"],
            "team_size": context["organization"]["team_size"],
            "growth_stage": context["organization"]["growth_stage"],
        },
        "executive_summary": {
            "current_level": f"Level {maturity['current_level']}",
            "current_name": maturity['current_name'],
            "target_level": f"Level {maturity['target_level']}",
            "target_name": maturity['target_name'],
            "timeline": f"{maturity['timeline_months']} months",
            "total_phases": maturity["total_phases"],
            "compliance_status": compliance["overall_status"],
            "recommended_monthly_cost": f"${int(cost_summary['recommended_path']['monthly']):,}/mo",
        },
        "maturity_assessment": maturity,
        "architecture_recommendations": recommendations,
        "compliance_report": compliance,
        "cost_projection": cost_summary,
        "next_steps": generate_next_steps(maturity, compliance),
    }
    
    return blueprint


def generate_next_steps(maturity: dict, compliance: dict) -> list:
    """Generate actionable next steps."""
    steps = []
    
    # Phase 1 focus
    if maturity["phases"]:
        phase1 = maturity["phases"][0]
        steps.append(f"Implement Phase 1 ({phase1['name']}) architecture with the recommended tools.")
    
    # Compliance gaps
    if compliance.get("gaps"):
        steps.append(f"Address {len(compliance['gaps'])} compliance gap(s) before production deployment.")
    
    # General guidance
    steps.extend([
        "Set up monitoring and alerting from day 1 to track transition triggers.",
        "Document architecture decisions (ADRs) for team alignment.",
        "Plan quarterly reviews to assess if transition triggers are being met.",
    ])
    
    return steps
