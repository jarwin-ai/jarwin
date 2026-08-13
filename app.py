"""
Jarwin - Adaptive Architecture Blueprint System
"""

import streamlit as st
import json
from agents.context_agent import analyze_context, INDUSTRY_MAP, GROWTH_STAGES
from agents.maturity_agent import assess_maturity
from agents.tool_agent import recommend_tools
from agents.compliance_agent import check_compliance
from agents.blueprint_agent import generate_blueprint
from agents.chat_agent import generate_chat_response
from agents.collaboration import validate_recommendations
from agents.memory import save_company, list_companies, save_session
from agents.llm_engine import get_llm
from agents.analytics import track_event, get_stats

# Page config
st.set_page_config(
    page_title="Jarwin - Architecture Advisor",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get help': None,
        'Report a Bug': None,
        'About': None
    }
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .phase-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .oss-badge {
        background-color: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    .lic-badge {
        background-color: #6366f1;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)


def show_pro_upgrade():
    """Show the Pro upgrade screen."""
    st.markdown("---")
    st.markdown("## ⭐ Upgrade to Jarwin Pro")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Free Plan")
        st.write("- 1 blueprint/month")
        st.write("- Basic recommendations")
        st.write("- Community support")
        st.markdown("**$0/month**")
    
    with col2:
        st.markdown("### Pro Plan")
        st.write("- Unlimited blueprints")
        st.write("- Detailed TCO analysis")
        st.write("- PDF export")
        st.write("- All compliance frameworks")
        st.write("- Priority support")
        st.markdown("**$29/month**")
        st.link_button("🚀 Upgrade to Pro", "mailto:krishnask921@gmail.com?subject=Jarwin Pro Access&body=Hi, I want to upgrade to Jarwin Pro plan.", type="primary")
    
    st.markdown("---")
    
    pro_key = st.text_input("Have a Pro key? Enter it here:", type="password")
    if pro_key and pro_key == "JARWIN-PRO-2024":
        st.session_state["is_pro"] = True
        st.success("Pro activated! Refreshing...")
        st.rerun()


def show_admin_dashboard():
    """Admin dashboard."""
    st.markdown("## Jarwin Admin Dashboard")
    st.markdown("---")
    
    stats = get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Blueprints", stats["total_blueprints"])
    col2.metric("Today", stats["today_blueprints"])
    col3.metric("This Week", stats["weekly_blueprints"])
    col4.metric("Total Visits", stats["total_visits"])
    
    st.markdown("---")
    
    st.markdown("### Top Industries")
    if stats["top_industries"]:
        for ind in stats["top_industries"]:
            st.write(f"• **{ind['industry'].replace('_',' ').title()}**: {ind['count']} blueprints")
    else:
        st.write("No data yet")
    
    st.markdown("### Mode Split")
    st.write(f"• Chat Mode: {stats['mode_split']['chat']}")
    st.write(f"• Form Mode: {stats['mode_split']['form']}")


def main():
    # Track page visit
    if "visited" not in st.session_state:
        track_event("page_visit")
        st.session_state["visited"] = True
    
    # Check for admin mode
    query_params = st.query_params
    if query_params.get("admin") == "jarwin2024":
        show_admin_dashboard()
        return
    
    # Check Pro status
    if "is_pro" not in st.session_state:
        st.session_state["is_pro"] = False
    if "usage_count" not in st.session_state:
        st.session_state["usage_count"] = 0
    
    # Header
    st.markdown('<p class="main-header">Jarwin</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Adaptive Architecture Blueprint System — Your AI Architecture Advisor</p>', unsafe_allow_html=True)
    
    # LLM Status (hidden from users - not relevant)
    llm = get_llm()
    
    # Pro badge
    if st.session_state["is_pro"]:
        st.caption("⭐ Pro Plan Active")
    else:
        free_left = max(0, 1 - st.session_state["usage_count"])
        if free_left > 0:
            st.caption(f"Free Plan — {free_left} blueprint remaining")
        else:
            st.warning("⚠️ Free limit reached (1 blueprint). Upgrade to Pro for unlimited access.")
            show_pro_upgrade()
            return
    
    # Mode selection
    mode = st.radio("Mode", ["💬 Chat Mode", "📋 Quick Mode (Form)"], horizontal=True, label_visibility="collapsed")
    
    if mode == "💬 Chat Mode":
        run_chat_mode()
        return
    
    # Sidebar - Input Form
    with st.sidebar:
        st.header("Tell Us About Your Company")
        st.markdown("---")
        
        industry = st.selectbox(
            "Industry",
            options=list(INDUSTRY_MAP.keys()),
            format_func=lambda x: x.replace("_", " ").title(),
        )
        
        growth_stage = st.selectbox(
            "Growth Stage",
            options=GROWTH_STAGES,
            format_func=lambda x: x.replace("_", " ").title(),
            index=1,
        )
        
        team_size = st.slider("Engineering Team Size", min_value=1, max_value=500, value=10)
        monthly_users = st.number_input("Expected Monthly Active Users", min_value=100, max_value=100_000_000, value=10000, step=1000)
        budget_monthly = st.number_input("Monthly Tech Budget (USD)", min_value=0, max_value=1_000_000, value=2000, step=500)
        
        st.markdown("---")
        st.subheader("Technical Preferences")
        
        cloud_pref = st.selectbox("Cloud Preference", ["any", "aws", "gcp", "azure", "multi-cloud"])
        
        oss_pref = st.select_slider(
            "Open Source Preference",
            options=["oss_first", "balanced", "licensed_first"],
            value="balanced",
            format_func=lambda x: {"oss_first": "Prefer OSS", "balanced": "Balanced", "licensed_first": "Prefer Licensed"}[x],
        )
        
        regions = st.multiselect(
            "Deployment Regions",
            ["us", "eu", "uk", "asia", "australia", "india", "global"],
            default=["us"],
        )
        
        uptime_sla = st.select_slider(
            "Uptime Requirement",
            options=[99.0, 99.5, 99.9, 99.95, 99.99],
            value=99.9,
            format_func=lambda x: f"{x}%",
        )
        
        st.markdown("---")
        generate_btn = st.button("🚀 Generate Architecture Blueprint", type="primary", use_container_width=True)
    
    # Main content
    if generate_btn:
        with st.spinner("Jarwin is analyzing your requirements..."):
            # Step 1: Context Analysis
            user_inputs = {
                "industry": industry,
                "team_size": team_size,
                "monthly_users": monthly_users,
                "budget_monthly": budget_monthly,
                "growth_stage": growth_stage,
                "cloud_preference": cloud_pref,
                "oss_preference": oss_pref,
                "regions": regions,
                "uptime_sla": uptime_sla,
            }
            
            context = analyze_context(user_inputs)
        
        with st.spinner("Assessing maturity level..."):
            maturity = assess_maturity(context)
        
        with st.spinner("Selecting optimal tools (dual-path analysis)..."):
            recommendations = recommend_tools(context, maturity)
        
        with st.spinner("Validating compliance..."):
            compliance = check_compliance(context, recommendations)
        
        with st.spinner("Generating blueprint..."):
            blueprint = generate_blueprint(context, maturity, recommendations, compliance)
        
        # Track usage
        st.session_state["usage_count"] += 1
        track_event("blueprint_generated", industry=industry, mode="form", details={"level": maturity["current_level"], "target": maturity["target_level"]})
        
        # Store in session
        st.session_state["blueprint"] = blueprint
        st.session_state["generated"] = True
        st.session_state["last_context"] = context
        st.session_state.pop("validation", None)  # Reset validation for new run
        
        # Save to memory
        company_id = f"{industry}_{growth_stage}_{team_size}"
        save_company(company_id, f"{industry.title()} ({team_size} engineers)", context)
        save_session(company_id, blueprint, [])
    
    # Display results
    if st.session_state.get("generated"):
        blueprint = st.session_state["blueprint"]
        
        # Run validation (hidden from user - internal quality check)
        if "validation" not in st.session_state:
            context = st.session_state.get("last_context", {})
            recommendations = blueprint.get("architecture_recommendations", [])
            compliance = blueprint.get("compliance_report", {})
            validation = validate_recommendations(context, recommendations, compliance)
            st.session_state["validation"] = validation
        
        display_results(blueprint)
        
        # Show validation only if issues exist (user-friendly language)
        validation = st.session_state.get("validation", {})
        if validation.get("issues_found", 0) > 0:
            with st.expander(f"💡 Optimization Notes ({validation['issues_found']} suggestion(s))", expanded=False):
                for issue in validation.get("issues", []):
                    severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(issue["severity"], "⚪")
                    st.write(f"{severity_icon} **{issue['type'].replace('_', ' ').title()}**: {issue['message']}")
                if validation.get("improvements"):
                    st.markdown("**Suggestions:**")
                    for imp in validation["improvements"]:
                        st.write(f"→ {imp}")
    else:
        display_landing()


def display_landing():
    """Show landing page when no blueprint generated yet."""

    # Show saved companies
    companies = list_companies()
    if companies:
        st.markdown("### 📂 Previous Sessions")
        for comp in companies[:3]:
            st.caption(f"• {comp['name']} (last: {comp['updated_at'][:10]})")
        st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Maturity Assessment")
        st.write("Understand where you are and where you should be headed.")
    
    with col2:
        st.markdown("### ⚖️ OSS vs Licensed")
        st.write("Get dual-path recommendations with TCO comparison for every component.")
    
    with col3:
        st.markdown("### ✅ Compliance Mapping")
        st.write("Auto-validate against HIPAA, PCI-DSS, SOC2, GDPR, ISO27001.")
    
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
    1. **Fill in your company details** in the sidebar (Quick Mode) OR **chat with Jarwin** (Chat Mode)
    2. **Get a complete E2E architecture** with phased roadmap, tool recommendations, and compliance report
    3. **Download the report** or ask follow-up questions
    
    Powered by verified tool data, real pricing, and compliance frameworks.
    """)


def run_chat_mode():
    """Chat mode — conversational interface with Jarwin."""
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_context" not in st.session_state:
        st.session_state.chat_context = None
    
    # Display chat messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🏗️" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])
    
    # Welcome message
    if not st.session_state.chat_messages:
        welcome = """Hey! I'm **Jarwin**, your AI Architecture Advisor. 👋

I help companies design their complete technology stack — from databases to deployment.

**To get started, tell me about your company:**
- What **industry** are you in?
- How big is your **engineering team**?
- What's your **monthly tech budget**?
- Any **compliance** requirements (HIPAA, PCI-DSS, SOC2)?

Or just describe what you're building and I'll figure out the rest!

💡 *Say "generate" or "recommend" when you want me to create your architecture blueprint.*"""
        
        with st.chat_message("assistant", avatar="🏗️"):
            st.markdown(welcome)
        st.session_state.chat_messages.append({"role": "assistant", "content": welcome})
    
    # Chat input
    if user_input := st.chat_input("Tell me about your company or ask anything..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant", avatar="🏗️"):
            with st.spinner("Thinking..."):
                result = generate_chat_response(
                    st.session_state.chat_messages,
                    st.session_state.chat_context
                )
                
                response = result["response"]
                st.markdown(response)
                
                # Update context if extracted
                if result.get("context"):
                    st.session_state.chat_context = result["context"]
                
                # Store blueprint if generated
                if result.get("blueprint"):
                    st.session_state["blueprint"] = result["blueprint"]
                    st.session_state["generated"] = True
        
        st.session_state.chat_messages.append({"role": "assistant", "content": response})


def display_results(blueprint):
    """Display the generated blueprint."""
    
    # Executive Summary
    st.header("Executive Summary")
    summary = blueprint["executive_summary"]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Level", summary["current_level"])
    col2.metric("Target Level", summary["target_level"])
    col3.metric("Timeline", summary["timeline"])
    col4.metric("Monthly Cost", summary["recommended_monthly_cost"])
    
    # Compliance status
    compliance_color = "🟢" if blueprint["compliance_report"]["overall_status"] == "COMPLIANT" else "🟡" if blueprint["compliance_report"]["overall_status"] == "GAPS_FOUND" else "⚪"
    st.info(f"{compliance_color} Compliance Status: **{blueprint['compliance_report']['overall_status']}** | Frameworks: {', '.join(blueprint['compliance_report']['applicable_frameworks'])}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Roadmap", "🛠️ Tool Recommendations", "✅ Compliance", "💰 Cost Analysis", "📋 Full Report"])
    
    with tab1:
        display_roadmap(blueprint)
    
    with tab2:
        display_tools(blueprint)
    
    with tab3:
        display_compliance(blueprint)
    
    with tab4:
        display_costs(blueprint)
    
    with tab5:
        display_full_report(blueprint)


def display_roadmap(blueprint):
    """Display the maturity roadmap."""
    st.subheader("Progressive Architecture Roadmap")
    
    maturity = blueprint["maturity_assessment"]
    
    # Timeline visualization
    phases = maturity["phases"]
    cols = st.columns(len(phases))
    
    for i, (col, phase) in enumerate(zip(cols, phases)):
        with col:
            is_current = (phase["level"] == maturity["current_level"])
            emoji = "📍" if is_current else "🎯" if i == len(phases) - 1 else "➡️"
            
            st.markdown(f"### {emoji} Phase {phase['phase']}")
            st.markdown(f"**Level {phase['level']}: {phase['name']}**")
            st.caption(phase["subtitle"])
            st.write(phase["description"])
            
            with st.expander("Architecture Details"):
                for key, value in phase["characteristics"].items():
                    st.write(f"• **{key.replace('_', ' ').title()}**: {value}")
            
            if phase.get("transition_triggers"):
                with st.expander("Transition Triggers"):
                    for trigger, value in phase["transition_triggers"].items():
                        st.write(f"• {trigger.replace('_', ' ')}: **{value}**")


def display_tools(blueprint):
    """Display tool recommendations."""
    st.subheader("Tool Recommendations (Dual-Path)")
    
    recommendations = blueprint["architecture_recommendations"]
    
    for phase in recommendations:
        with st.expander(f"Phase {phase['phase']}: Level {phase['level']} - {phase['name']}", expanded=(phase["phase"] == 1)):
            for comp in phase["components"]:
                st.markdown(f"#### {comp['component'].replace('_', ' ').title()}")
                st.caption(comp.get("description", ""))
                
                col1, col2 = st.columns(2)
                
                # OSS Recommendation
                with col1:
                    oss = comp.get("oss_recommendation")
                    if oss:
                        verdict_icon = "⭐" if comp.get("verdict") == "OSS" else ""
                        st.markdown(f"**🟢 Open Source {verdict_icon}**")
                        st.markdown(f"**{oss['name']}** (Score: {oss['score']:.2f})")
                        st.caption(f"License: {oss.get('license', 'N/A')}")
                        st.write(f"💰 TCO: **${oss['tco']['total_monthly']:.0f}/mo** (${oss['tco']['total_36_months']:.0f}/3yr)")
                        for pro in oss.get("pros", []):
                            st.write(f"✅ {pro}")
                        for con in oss.get("cons", []):
                            st.write(f"⚠️ {con}")
                        if oss.get("alternatives"):
                            st.caption(f"Alternatives: {', '.join(oss['alternatives'])}")
                    else:
                        st.write("No OSS option available")
                
                # Licensed Recommendation
                with col2:
                    lic = comp.get("licensed_recommendation")
                    if lic:
                        verdict_icon = "⭐" if comp.get("verdict") == "LICENSED" else ""
                        st.markdown(f"**🔵 Licensed {verdict_icon}**")
                        st.markdown(f"**{lic['name']}** (Score: {lic['score']:.2f})")
                        st.write(f"💰 TCO: **${lic['tco']['total_monthly']:.0f}/mo** (${lic['tco']['total_36_months']:.0f}/3yr)")
                        for pro in lic.get("pros", []):
                            st.write(f"✅ {pro}")
                        for con in lic.get("cons", []):
                            st.write(f"⚠️ {con}")
                        if lic.get("alternatives"):
                            st.caption(f"Alternatives: {', '.join(lic['alternatives'])}")
                    else:
                        st.write("No licensed option available")
                
                # Verdict
                verdict = comp.get("verdict", "")
                rationale = comp.get("rationale", "")
                if verdict:
                    verdict_color = {"OSS": "green", "LICENSED": "blue", "EITHER": "orange"}
                    st.success(f"**Recommendation: {verdict}** — {rationale}")
                
                st.markdown("---")


def display_compliance(blueprint):
    """Display compliance report."""
    st.subheader("Compliance Report")
    
    report = blueprint["compliance_report"]
    
    if report["overall_status"] == "NO_COMPLIANCE_REQUIRED":
        st.info("No specific compliance frameworks detected for your configuration.")
        return
    
    # Framework scores
    st.markdown("### Framework Coverage")
    for fw, scores in report.get("framework_scores", {}).items():
        score_pct = int(scores["score"] * 100)
        status_icon = "✅" if scores["status"] == "COMPLIANT" else "⚠️"
        st.write(f"{status_icon} **{fw}**: {score_pct}% ({scores['controls_met']}/{scores['controls_total']} controls)")
        st.progress(scores["score"])
    
    # Gaps
    if report.get("gaps"):
        st.markdown("### ⚠️ Compliance Gaps")
        for gap in report["gaps"]:
            st.warning(f"**{gap['framework']} - {gap['control']}** ({gap['severity']})\n\n{gap['description']}\n\n*Remediation:* {gap['remediation']}")
    
    # Attestation
    if report.get("attestation_matrix"):
        st.markdown("### ✅ Controls Satisfied")
        for att in report["attestation_matrix"]:
            st.write(f"✅ **{att['framework']}** - {att['control']}: {att['description']}")
    
    # Recommendations
    if report.get("recommendations"):
        st.markdown("### Recommendations")
        for rec in report["recommendations"]:
            st.write(f"→ {rec}")


def display_costs(blueprint):
    """Display cost analysis."""
    st.subheader("Cost Projection")
    
    costs = blueprint["cost_projection"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🟢 Full OSS Path")
        st.metric("Monthly", f"${costs['oss_path']['monthly']:,.0f}")
        st.metric("Annual", f"${costs['oss_path']['annual']:,.0f}")
        st.metric("3-Year Total", f"${costs['oss_path']['three_year']:,.0f}")
    
    with col2:
        st.markdown("### 🔵 Full Licensed Path")
        st.metric("Monthly", f"${costs['licensed_path']['monthly']:,.0f}")
        st.metric("Annual", f"${costs['licensed_path']['annual']:,.0f}")
        st.metric("3-Year Total", f"${costs['licensed_path']['three_year']:,.0f}")
    
    with col3:
        st.markdown("### ⭐ Recommended (Mixed)")
        st.metric("Monthly", f"${costs['recommended_path']['monthly']:,.0f}")
        st.metric("Annual", f"${costs['recommended_path']['annual']:,.0f}")
        st.metric("3-Year Total", f"${costs['recommended_path']['three_year']:,.0f}")
    
    st.markdown("---")
    savings = costs.get("savings_vs_licensed", {})
    if savings.get("annual", 0) > 0:
        st.success(f"💰 **You save ${savings['annual']:,.0f}/year** with the recommended path vs. all-licensed")


def display_full_report(blueprint):
    """Display full JSON report for download."""
    st.subheader("Full Architecture Report")
    
    # Next steps
    st.markdown("### Next Steps")
    for i, step in enumerate(blueprint.get("next_steps", []), 1):
        st.write(f"{i}. {step}")
    
    st.markdown("---")
    st.markdown("### Download Report")
    
    report_json = json.dumps(blueprint, indent=2)
    st.download_button(
        "📥 Download Full Report (JSON)",
        report_json,
        file_name="jarwin_architecture_blueprint.json",
        mime="application/json",
    )
    
    with st.expander("View Detailed Data"):
        st.json(blueprint)


if __name__ == "__main__":
    main()
