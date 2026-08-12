"""
Jarwin Compliance Agent
Validates architecture recommendations against regulatory frameworks.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPLIANCE_PATH = os.path.join(BASE_DIR, "knowledge_base", "compliance", "frameworks.json")


def load_compliance():
    with open(COMPLIANCE_PATH, "r") as f:
        return json.load(f)


def check_compliance(context: dict, recommendations: list) -> dict:
    """
    Validate all tool recommendations against applicable compliance frameworks.
    Returns compliance report with gaps and attestation.
    """
    frameworks_db = load_compliance()
    required_frameworks = context["compliance"]["frameworks"]
    
    report = {
        "applicable_frameworks": required_frameworks,
        "overall_status": "COMPLIANT",
        "framework_scores": {},
        "attestation_matrix": [],
        "gaps": [],
        "recommendations": [],
    }
    
    if not required_frameworks:
        report["overall_status"] = "NO_COMPLIANCE_REQUIRED"
        return report
    
    # Check each framework
    for fw_name in required_frameworks:
        fw_data = frameworks_db["frameworks"].get(fw_name)
        if not fw_data:
            continue
        
        controls_met = 0
        controls_total = 0
        
        for control_id, control_info in fw_data["key_requirements"].items():
            controls_total += 1
            control_satisfied = False
            satisfied_by = []
            
            # Check if any recommended tool satisfies this control
            for phase in recommendations:
                for component in phase["components"]:
                    # Check OSS recommendation
                    oss_rec = component.get("oss_recommendation", {})
                    lic_rec = component.get("licensed_recommendation", {})
                    verdict = component.get("verdict", "")
                    
                    # Use the recommended path's tool
                    if verdict == "OSS" and oss_rec:
                        tool_name = oss_rec["name"]
                    elif verdict == "LICENSED" and lic_rec:
                        tool_name = lic_rec["name"]
                    elif lic_rec:
                        tool_name = lic_rec["name"]
                    elif oss_rec:
                        tool_name = oss_rec["name"]
                    else:
                        continue
                    
                    # Check if tool's compliance certifications cover this framework
                    if lic_rec and fw_name in lic_rec.get("pros", [""])[0] if lic_rec.get("pros") else False:
                        control_satisfied = True
                        satisfied_by.append({"tool": tool_name, "mechanism": "certification"})
                    
                    # Component-level compliance mapping
                    if control_id in ["encryption_at_rest", "encryption_in_transit"] and component["component"] in ["relational_database", "caching"]:
                        if lic_rec:
                            control_satisfied = True
                            satisfied_by.append({"tool": lic_rec["name"], "mechanism": "built-in encryption"})
                    
                    if control_id == "access_control" and component["component"] == "auth":
                        control_satisfied = True
                        satisfied_by.append({"tool": tool_name, "mechanism": "authentication service"})
                    
                    if control_id == "audit_logging" and component["component"] == "monitoring":
                        control_satisfied = True
                        satisfied_by.append({"tool": tool_name, "mechanism": "logging and monitoring"})
                    
                    if control_id == "vulnerability_scanning" and component["component"] == "vulnerability_scanning":
                        control_satisfied = True
                        satisfied_by.append({"tool": tool_name, "mechanism": "security scanning"})
            
            if control_satisfied:
                controls_met += 1
                report["attestation_matrix"].append({
                    "framework": fw_name,
                    "control": control_id,
                    "description": control_info["description"],
                    "status": "MET",
                    "satisfied_by": satisfied_by[:2],
                })
            else:
                report["gaps"].append({
                    "framework": fw_name,
                    "control": control_id,
                    "description": control_info["description"],
                    "severity": "HIGH" if control_info.get("mandatory") else "MEDIUM",
                    "remediation": f"Add a tool or configuration to address: {control_info['description']}",
                })
        
        # Framework score
        score = controls_met / controls_total if controls_total > 0 else 0
        report["framework_scores"][fw_name] = {
            "score": round(score, 2),
            "controls_met": controls_met,
            "controls_total": controls_total,
            "status": "COMPLIANT" if score >= 0.7 else "GAPS_FOUND",
        }
        
        if score < 0.7:
            report["overall_status"] = "GAPS_FOUND"
    
    # Generate remediation recommendations for gaps
    if report["gaps"]:
        report["recommendations"] = [
            f"Address {len(report['gaps'])} compliance gap(s) before production deployment.",
            "Consider using managed/licensed tools with built-in certifications for compliance-critical components.",
            "Implement additional security controls (WAF, SIEM, DLP) as needed by your compliance frameworks.",
        ]
    
    return report
