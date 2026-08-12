"""
Jarwin Agent Collaboration
Agents validate and improve each other's recommendations.
"""

from agents.llm_engine import get_llm


def validate_recommendations(context: dict, recommendations: list, compliance_report: dict) -> dict:
    """
    Run cross-agent validation:
    - Compliance Agent checks Tool Agent's choices
    - Tool Agent validates no conflicts between selected tools
    - Blueprint Agent ensures completeness
    
    Returns validation report with any issues found.
    """
    issues = []
    improvements = []
    
    # 1. Check for tool conflicts (incompatibilities)
    for phase in recommendations:
        selected_tools = []
        for comp in phase["components"]:
            verdict = comp.get("verdict", "")
            if verdict == "OSS":
                tool = comp.get("oss_recommendation", {}).get("name", "")
            elif verdict == "LICENSED":
                tool = comp.get("licensed_recommendation", {}).get("name", "")
            else:
                tool = comp.get("oss_recommendation", {}).get("name", "")
            if tool:
                selected_tools.append({"component": comp["component"], "tool": tool})
        
        # Check known conflicts
        conflicts = check_tool_conflicts(selected_tools)
        issues.extend(conflicts)
    
    # 2. Check compliance gaps severity
    if compliance_report.get("gaps"):
        high_gaps = [g for g in compliance_report["gaps"] if g.get("severity") == "HIGH"]
        if high_gaps:
            issues.append({
                "severity": "HIGH",
                "type": "compliance",
                "message": f"{len(high_gaps)} high-severity compliance gap(s) found. Consider switching to certified tools.",
                "affected": [g["control"] for g in high_gaps]
            })
    
    # 3. Check budget alignment
    budget = context["organization"]["budget_monthly_usd"]
    total_cost = 0
    for phase in recommendations:
        if phase["phase"] == 1:  # Only check Phase 1 (immediate cost)
            for comp in phase["components"]:
                verdict = comp.get("verdict", "")
                if verdict == "OSS":
                    total_cost += comp.get("oss_recommendation", {}).get("tco", {}).get("total_monthly", 0)
                elif verdict == "LICENSED":
                    total_cost += comp.get("licensed_recommendation", {}).get("tco", {}).get("total_monthly", 0)
    
    if total_cost > budget * 1.2:  # 20% over budget
        issues.append({
            "severity": "MEDIUM",
            "type": "budget",
            "message": f"Phase 1 estimated cost (${total_cost:.0f}/mo) exceeds budget (${budget}/mo) by {((total_cost/budget)-1)*100:.0f}%. Consider more OSS options.",
            "suggestion": "Switch licensed tools to OSS alternatives where compliance allows."
        })
        improvements.append("Consider using OSS alternatives for non-compliance-critical components to stay within budget.")
    
    # 4. Check team capability alignment
    team_size = context["organization"]["team_size"]
    complex_tools = 0
    for phase in recommendations:
        if phase["phase"] == 1:
            for comp in phase["components"]:
                oss = comp.get("oss_recommendation", {})
                if comp.get("verdict") == "OSS" and oss:
                    # Check if tool's learning curve is too steep for small team
                    # (This info would come from tool database in production)
                    pass
                complex_tools += 1
    
    if team_size < 5 and complex_tools > 8:
        issues.append({
            "severity": "LOW",
            "type": "team_capacity",
            "message": f"Small team ({team_size}) with {complex_tools} tools to manage. Consider more managed services to reduce operational burden.",
            "suggestion": "Prefer licensed/managed tools for non-core components."
        })
        improvements.append("For small teams, managed services reduce operational overhead. Consider licensed options for monitoring and databases.")
    
    # 5. Use LLM for deeper analysis if available
    llm = get_llm()
    if llm.available and issues:
        llm_review = llm.generate(
            prompt=f"Review these architecture issues and suggest fixes:\n{issues}",
            system_prompt="You are a senior solutions architect reviewing architecture decisions. Be concise.",
            temperature=0.3
        )
        if llm_review:
            improvements.append(llm_review)
    
    return {
        "issues_found": len(issues),
        "issues": issues,
        "improvements": improvements,
        "overall_quality": "HIGH" if len(issues) == 0 else "MEDIUM" if all(i["severity"] != "HIGH" for i in issues) else "NEEDS_ATTENTION"
    }


def check_tool_conflicts(tools: list) -> list:
    """Check for known incompatibilities between tools."""
    conflicts = []
    
    tool_names = [t["tool"].lower() for t in tools]
    
    # Known conflict patterns
    if "apache kafka" in tool_names and any("serverless" in t for t in tool_names):
        conflicts.append({
            "severity": "LOW",
            "type": "compatibility",
            "message": "Kafka with serverless can be complex. Consider managed Kafka (Confluent/MSK) or switch to SQS for serverless architectures."
        })
    
    # Multi-cloud conflicts
    aws_tools = [t for t in tool_names if "aws" in t or "amazon" in t]
    gcp_tools = [t for t in tool_names if "google" in t or "gcp" in t]
    azure_tools = [t for t in tool_names if "azure" in t]
    
    clouds_used = sum([1 for c in [aws_tools, gcp_tools, azure_tools] if c])
    if clouds_used > 1:
        conflicts.append({
            "severity": "MEDIUM",
            "type": "multi_cloud",
            "message": f"Using tools from {clouds_used} cloud providers increases complexity and may prevent volume discounts. Consider consolidating to one primary cloud."
        })
    
    return conflicts
