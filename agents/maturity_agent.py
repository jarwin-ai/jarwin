"""
Jarwin Maturity Agent
Assesses current maturity level and determines target level with timeline.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS_PATH = os.path.join(BASE_DIR, "knowledge_base", "patterns", "maturity_patterns.json")


def load_patterns():
    with open(PATTERNS_PATH, "r") as f:
        return json.load(f)


def compute_maturity_score(context: dict) -> float:
    """Compute Current Maturity Score (CMS) from context. Returns 0.0 - 1.0"""
    org = context["organization"]
    
    # Normalize each factor to 0-1
    team_norm = min(org["team_size"] / 200, 1.0)
    users_norm = min(org["monthly_users"] / 5_000_000, 1.0) if org["monthly_users"] > 0 else 0
    
    stage_map = {
        "pre-seed": 0.05, "seed": 0.15, "series_a": 0.3,
        "series_b": 0.5, "series_c": 0.65, "growth": 0.8, "enterprise": 0.95
    }
    stage_norm = stage_map.get(org["growth_stage"], 0.15)
    
    compliance_count = len(context["compliance"]["frameworks"])
    compliance_norm = min(compliance_count / 5, 1.0)
    
    budget_norm = min(org["budget_monthly_usd"] / 100_000, 1.0)
    
    # Weighted combination
    cms = (
        0.15 * team_norm +
        0.25 * users_norm +
        0.25 * stage_norm +
        0.20 * compliance_norm +
        0.15 * budget_norm
    )
    
    return round(cms, 3)


def score_to_level(cms: float) -> int:
    """Map CMS score to maturity level 1-5"""
    if cms < 0.20:
        return 1
    elif cms < 0.40:
        return 2
    elif cms < 0.60:
        return 3
    elif cms < 0.80:
        return 4
    else:
        return 5


def determine_target_level(current_level: int, context: dict) -> int:
    """Determine appropriate target maturity level"""
    stage = context["organization"]["growth_stage"]
    
    # Based on growth stage, suggest how far to aim
    stage_targets = {
        "pre-seed": 2, "seed": 2, "series_a": 3,
        "series_b": 3, "series_c": 4, "growth": 4, "enterprise": 5
    }
    
    stage_target = stage_targets.get(stage, 2)
    target = max(current_level + 1, stage_target)  # Always at least 1 level above
    return min(target, 5)


def estimate_timeline(current_level: int, target_level: int, context: dict) -> int:
    """Estimate months to reach target level"""
    gap = target_level - current_level
    if gap == 0:
        return 0
    
    base_months = {1: 4, 2: 10, 3: 18, 4: 30}
    base = base_months.get(gap, 36)
    
    # Adjust for team size (smaller team = slower)
    team_size = context["organization"]["team_size"]
    if team_size < 5:
        base = int(base * 1.5)
    elif team_size > 50:
        base = int(base * 0.7)
    
    return base


def assess_maturity(context: dict) -> dict:
    """
    Main function: assess current maturity and generate roadmap info.
    """
    patterns = load_patterns()
    
    cms = compute_maturity_score(context)
    current_level = score_to_level(cms)
    target_level = determine_target_level(current_level, context)
    timeline_months = estimate_timeline(current_level, target_level, context)
    
    current_info = patterns["maturity_levels"][str(current_level)]
    target_info = patterns["maturity_levels"][str(target_level)]
    
    # Build phase plan
    phases = []
    for level in range(current_level, target_level + 1):
        level_info = patterns["maturity_levels"][str(level)]
        phase_num = level - current_level + 1
        phases.append({
            "phase": phase_num,
            "level": level,
            "name": level_info["name"],
            "subtitle": level_info["subtitle"],
            "description": level_info["description"],
            "required_components": level_info["required_components"],
            "characteristics": level_info["characteristics"],
            "transition_triggers": level_info.get("transition_triggers", {}),
            "typical_cost": level_info["typical_monthly_cost"],
        })
    
    return {
        "maturity_score": cms,
        "current_level": current_level,
        "current_name": current_info["name"],
        "target_level": target_level,
        "target_name": target_info["name"],
        "timeline_months": timeline_months,
        "total_phases": target_level - current_level + 1,
        "phases": phases,
    }
