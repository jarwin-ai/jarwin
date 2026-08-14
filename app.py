"""
Jarwin - Adaptive Architecture Blueprint System
"""

import streamlit as st
import json
import os
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
from agents.e2e_architect import generate_full_e2e, E2E_SECTIONS

# Page config
st.set_page_config(
    page_title="Jarwin AI - Architecture Advisor",
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
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main header */
    .main-header {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
        letter-spacing: -1px;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    
    /* Cards */
    div[data-testid="stMetric"] {
        background: #1e293b;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button[kind="secondary"] {
        border-radius: 8px;
    }
    
    /* Feature cards */
    .feature-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(129,140,248,0.2);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #94a3b8;
    }
    
    /* Hero section */
    .hero-badge {
        display: inline-block;
        background: rgba(129,140,248,0.15);
        color: #a5b4fc;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        border: 1px solid rgba(129,140,248,0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1e293b;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)


def show_pro_upgrade():
    """Show the Pro upgrade screen."""
    st.markdown("---")
    st.markdown("## ⭐ Upgrade to Jarwin Pro")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Free")
        st.write("- 1 blueprint/month")
        st.write("- Top 5 tools")
        st.write("- 3 architecture sections")
        st.write("- Compliance status")
        st.write("- Total cost estimate")
        st.markdown("**$0**")
        st.caption("✅ Current plan")
    
    with col2:
        st.markdown("### 📄 Single Report")
        st.write("- 1 full blueprint (all 14 sections)")
        st.write("- All tools (200+)")
        st.write("- Full compliance report")
        st.write("- Per-service cost breakdown")
        st.write("- JSON download")
        st.write("- One-time, no subscription")
        st.markdown("**$99 one-time**")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;background:linear-gradient(135deg,#6366f1,#a855f7);color:white;padding:10px 20px;border-radius:8px;font-weight:600;">📄 Get Report</span>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("### ⭐ Pro Monthly")
        st.write("- Unlimited blueprints")
        st.write("- All 14 architecture sections")
        st.write("- All tools (200+)")
        st.write("- Full compliance report")
        st.write("- Direct links to docs & downloads")
        st.write("- Chat mode access")
        st.write("- Updated tools monthly")
        st.write("- Stack optimization: find where you're overspending")
        st.write("- Email support (48hr)")
        st.markdown("**$29/month**")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;background:linear-gradient(135deg,#6366f1,#a855f7);color:white;padding:10px 20px;border-radius:8px;font-weight:600;">⭐ Get Pro</span>', unsafe_allow_html=True)
    
    with col4:
        st.markdown("### 🚀 Enterprise")
        st.write("- Everything in Pro")
        st.write("- 30-min architecture call/month")
        st.write("- Quarterly architecture review")
        st.write("- Priority support (4hr)")
        st.write("- Audit-ready PDF reports")
        st.write("- Custom recommendations")
        st.markdown("**$99/month**")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;background:linear-gradient(135deg,#059669,#10b981);color:white;padding:10px 20px;border-radius:8px;font-weight:600;">🚀 Get Enterprise</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    pro_key = st.text_input("Have a Pro key? Enter it here:", type="password")
    if pro_key and pro_key == os.environ.get("PRO_KEY", "JP2024X"):
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
    if query_params.get("admin") == os.environ.get("ADMIN_KEY", "jrwn9210"):
        show_admin_dashboard()
        return
    
    # Check Pro status
    if "is_pro" not in st.session_state:
        st.session_state["is_pro"] = False
    if "usage_count" not in st.session_state:
        st.session_state["usage_count"] = 0
    
    # Hero badge
    st.markdown('<span class="hero-badge">AI-Powered Architecture Advisor</span>', unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">Jarwin AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Entire Tech Architecture In 30 Seconds — From Infrastructure To Operations, OSS To Enterprise</p>', unsafe_allow_html=True)
    
    # LLM Status (hidden from users - not relevant)
    llm = get_llm()
    
    # Pro badge
    if st.session_state["is_pro"]:
        st.caption("⭐ Pro Plan Active")
    else:
        free_left = max(0, 1 - st.session_state["usage_count"])
        if free_left > 0:
            st.markdown(f'<p style="font-size:0.85rem;color:#555;">Free Plan — {free_left} blueprint remaining | <span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;">⭐ Upgrade to Jarwin Pro</span></p>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Free limit reached.")
            st.markdown('<p style="font-size:0.85rem;"><span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;">⭐ Upgrade to Jarwin Pro</span> for unlimited access</p>', unsafe_allow_html=True)
            show_pro_upgrade()
            return
    
    # Mode selection
    mode = st.radio("Mode", ["📋 Quick Mode (Form)", "💬 Chat Mode"], horizontal=True, label_visibility="collapsed")
    
    if mode == "💬 Chat Mode":
        run_chat_mode()
        return
    
    # Sidebar - Input Form
    with st.sidebar:
        st.markdown("### 🏢 About Your Company")
        
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
        
        team_size = st.number_input("Engineering Team Size", min_value=1, max_value=500, value=10, step=1)
        monthly_users = st.number_input("Expected Monthly Users", min_value=100, max_value=100_000_000, value=10000, step=1000)
        budget_monthly = st.number_input("Monthly Tech Budget (USD)", min_value=0, max_value=1_000_000, value=2000, step=500)
        
        st.markdown("---")
        st.markdown("### 🛠️ Technical Details")
        
        product_type = st.selectbox(
            "Product Type",
            options=["web_app", "mobile_app", "api_backend", "marketplace", "saas_platform", "internal_tool"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        
        starting_point = st.selectbox(
            "Starting Point",
            options=["building_from_scratch", "migrating_existing", "scaling_current"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
        
        cloud_pref = st.selectbox("Cloud Preference", ["any", "aws", "gcp", "azure", "multi-cloud"])
        
        oss_pref = st.select_slider(
            "Open Source Preference",
            options=["oss_first", "balanced", "licensed_first"],
            value="balanced",
            format_func=lambda x: {"oss_first": "Prefer OSS", "balanced": "Balanced", "licensed_first": "Prefer Licensed"}[x],
        )
        
        st.markdown("---")
        st.markdown("### 🌍 Deployment & Compliance")
        
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
                "product_type": product_type,
                "starting_point": starting_point,
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
        
        # Add "New Blueprint" button to allow generating another
        if st.button("🔄 Generate New Blueprint", type="secondary"):
            st.session_state.pop("generated", None)
            st.session_state.pop("blueprint", None)
            st.session_state.pop("validation", None)
            st.rerun()
        
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

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Maturity Assessment</div>
            <div class="feature-desc">Know your current level and get a clear path to enterprise-grade architecture</div>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">OSS vs Licensed</div>
            <div class="feature-desc">Side-by-side comparison with real TCO math for every component in your stack</div>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Compliance Ready</div>
            <div class="feature-desc">Validated against HIPAA, PCI-DSS, SOC2, GDPR, ISO27001 from day one</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 style="margin-top:1.5rem;">How Jarwin AI Works</h3>', unsafe_allow_html=True)
    st.markdown("""
    1. **Tell us about your company** — industry, team size, budget, compliance needs
    2. **Jarwin AI analyzes** and designs your complete architecture
    3. **Get your blueprint** — phased roadmap, tool recommendations, compliance report, cost analysis
    4. **Already have a stack?** — find where you're overspending with OSS vs Licensed TCO comparison
    """)


def run_chat_mode():
    """Chat mode — conversational interface with Jarwin."""
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chat_context" not in st.session_state:
        st.session_state.chat_context = None
    
    if "chat_history_all" not in st.session_state:
        st.session_state.chat_history_all = []
    
    # Sidebar: Chat history + help
    with st.sidebar:
        st.markdown("### 📌 Quick Commands")
        st.caption("Try typing these:")
        st.caption("• generate fintech 20 engineers")
        st.caption("• which cloud for healthcare?")
        st.caption("• PostgreSQL vs MySQL?")
        st.caption("• what about HIPAA?")
        st.caption("• best monitoring tool?")
        
        if st.session_state.chat_history_all:
            st.markdown("---")
            st.markdown(f"### 📜 Past Chats ({len(st.session_state.chat_history_all)})")
            for i, chat in enumerate(reversed(st.session_state.chat_history_all)):
                user_msgs = [m for m in chat if m["role"] == "user"]
                if user_msgs:
                    st.caption(f"• {user_msgs[0]['content'][:35]}...")
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if st.session_state.chat_messages:
                st.session_state.chat_history_all.append(st.session_state.chat_messages.copy())
            st.session_state.chat_messages = []
            st.session_state.chat_context = None
            st.rerun()
    
    # Display chat messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🏗️" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])
    
    # Welcome message
    if not st.session_state.chat_messages:
        welcome = """Hey! I'm **Jarwin AI** — your complete company architect. 👋

I design your **entire technology + operations stack** — infrastructure, DevOps, security, team structure, analytics, compliance, and more. With direct links to docs & downloads for every recommended tool.

---

📌 **Quick Guide (Rule-Based Mode — Free)**

This chat uses keyword matching to answer your questions. For full AI-powered conversations, upgrade to Pro.

**What you can ask:**
- `"which cloud for fintech?"` → Cloud comparison
- `"PostgreSQL vs MySQL?"` → Database comparison  
- `"what about HIPAA?"` → Compliance guidance
- `"best monitoring tool?"` → Monitoring recommendations
- `"microservices or monolith?"` → Architecture patterns
- `"how much will it cost?"` → Cost breakdown by budget

**To generate your full blueprint, type something like:**
- `"generate fintech 20 engineers $5000 budget aws"`
- `"generate healthcare startup 8 engineers"`
- `"generate ecommerce series_a 30 engineers"`

💡 *Include your industry, team size, and budget for best results. Say "generate" to create your 14-section blueprint.*"""
        
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
    col1.caption(summary.get("current_name", ""))
    col2.metric("Target Level", summary["target_level"])
    col2.caption(summary.get("target_name", ""))
    col3.metric("Timeline", summary["timeline"])
    col4.metric("Estimated Cost", summary["recommended_monthly_cost"])
    
    # Compliance status
    compliance_color = "🟢" if blueprint["compliance_report"]["overall_status"] == "COMPLIANT" else "🟡" if blueprint["compliance_report"]["overall_status"] == "GAPS_FOUND" else "⚪"
    st.info(f"{compliance_color} Compliance Status: **{blueprint['compliance_report']['overall_status']}** | Frameworks: {', '.join(blueprint['compliance_report']['applicable_frameworks'])}")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🗺️ Roadmap", "🛠️ Tool Recommendations", "🏗️ Full Architecture", "✅ Compliance", "💰 Cost Analysis", "📋 Full Report"])
    
    with tab1:
        display_roadmap(blueprint)
    
    with tab2:
        display_tools(blueprint)
    
    with tab3:
        display_e2e_architecture(blueprint)
    
    with tab4:
        display_compliance(blueprint)
    
    with tab5:
        display_costs(blueprint)
    
    with tab6:
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
    
    is_pro = st.session_state.get("is_pro", False)
    recommendations = blueprint["architecture_recommendations"]
    
    for phase in recommendations:
        with st.expander(f"Phase {phase['phase']}: Level {phase['level']} - {phase['name']}", expanded=(phase["phase"] == 1)):
            components = phase["components"]
            
            # Free users see only first 5 components
            if not is_pro and len(components) > 5:
                visible = components[:5]
                locked_count = len(components) - 5
            else:
                visible = components
                locked_count = 0
            
            for comp in visible:
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
            
            # Show locked message for free users
            if locked_count > 0:
                st.info(f"🔒 **{locked_count} more components** available with Pro — including security, observability, and data tools.")
                st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;font-weight:600;">⭐ Upgrade to see all →</span>', unsafe_allow_html=True)


def display_compliance(blueprint):
    """Display compliance report."""
    st.subheader("Compliance Report")
    
    is_pro = st.session_state.get("is_pro", False)
    report = blueprint["compliance_report"]
    
    if report["overall_status"] == "NO_COMPLIANCE_REQUIRED":
        st.info("No specific compliance frameworks detected for your configuration.")
        return
    
    # Everyone sees the status
    for fw, scores in report.get("framework_scores", {}).items():
        score_pct = int(scores["score"] * 100)
        status_icon = "✅" if scores["status"] == "COMPLIANT" else "⚠️"
        st.write(f"{status_icon} **{fw}**: {score_pct}% ({scores['controls_met']}/{scores['controls_total']} controls)")
        st.progress(scores["score"])
    
    if not is_pro:
        st.info("🔒 **Full compliance details** (control mappings, gap analysis, remediation steps) available with Pro.")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;font-weight:600;">⭐ Upgrade for full compliance report →</span>', unsafe_allow_html=True)
        return
    
    # Pro users see full details
    
    # Pro users see full details
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
    
    is_pro = st.session_state.get("is_pro", False)
    costs = blueprint["cost_projection"]
    
    # Everyone sees totals
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🟢 Full OSS Path")
        st.metric("Monthly", f"${costs['oss_path']['monthly']:,.0f}")
    
    with col2:
        st.markdown("### 🔵 Full Licensed Path")
        st.metric("Monthly", f"${costs['licensed_path']['monthly']:,.0f}")
    
    with col3:
        st.markdown("### ⭐ Recommended")
        st.metric("Monthly", f"${costs['recommended_path']['monthly']:,.0f}")
    
    savings = costs.get("savings_vs_licensed", {})
    if savings.get("annual", 0) > 0:
        st.success(f"💰 **You save ${savings['annual']:,.0f}/year** with the recommended path vs. all-licensed")
    
    if not is_pro:
        st.info("🔒 **Detailed cost breakdown** (per-service costs, annual projections, 3-year TCO) available with Pro.")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;font-weight:600;">⭐ Upgrade for full cost analysis →</span>', unsafe_allow_html=True)
        return
    
    # Pro: full breakdown
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Annual (OSS)", f"${costs['oss_path']['annual']:,.0f}")
        st.metric("3-Year (OSS)", f"${costs['oss_path']['three_year']:,.0f}")
    with col2:
        st.metric("Annual (Licensed)", f"${costs['licensed_path']['annual']:,.0f}")
        st.metric("3-Year (Licensed)", f"${costs['licensed_path']['three_year']:,.0f}")
    with col3:
        st.metric("Annual (Recommended)", f"${costs['recommended_path']['annual']:,.0f}")
        st.metric("3-Year (Recommended)", f"${costs['recommended_path']['three_year']:,.0f}")


def display_e2e_architecture(blueprint):
    """Display full E2E architecture — locked for free, unlocked for Pro."""
    st.subheader("Complete E2E Architecture Blueprint")
    
    is_pro = st.session_state.get("is_pro", False)
    
    # Generate E2E data
    context = st.session_state.get("last_context", {})
    maturity = blueprint.get("maturity_assessment", {})
    
    if context and maturity:
        e2e = generate_full_e2e(context, maturity)
    else:
        st.warning("Generate a blueprint first to see full architecture.")
        return
    
    if is_pro:
        # Pro users see everything
        for section_key, section_meta in E2E_SECTIONS.items():
            with st.expander(f"{section_meta['icon']} {section_meta['title']}", expanded=False):
                section_data = e2e.get(section_key, {})
                for key, value in section_data.items():
                    if key != "preview":
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    else:
        # Free users see locked previews
        st.info("💡 **11 architecture sections available.** Upgrade to Jarwin Pro to unlock full details.")
        st.markdown("")
        
        for section_key, section_meta in E2E_SECTIONS.items():
            section_data = e2e.get(section_key, {})
            preview = section_data.get("preview", "")
            st.markdown(f"🔒 **{section_meta['icon']} {section_meta['title']}** — _{preview}_")
        
        st.markdown("")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;background:linear-gradient(135deg,#6366f1,#a855f7);color:white;padding:10px 24px;border-radius:8px;font-weight:600;">⭐ Upgrade to Jarwin Pro — Unlock All Sections</span>', unsafe_allow_html=True)


def display_full_report(blueprint):
    """Display full JSON report for download."""
    st.subheader("Full Architecture Report")
    
    is_pro = st.session_state.get("is_pro", False)
    
    # Next steps (everyone sees)
    st.markdown("### Next Steps")
    for i, step in enumerate(blueprint.get("next_steps", []), 1):
        st.write(f"{i}. {step}")
    
    if not is_pro:
        st.markdown("---")
        st.info("🔒 **Full report download** (JSON with all architecture details) available with Pro.")
        st.markdown('<span title="Contact: krishnask921@gmail.com" style="cursor:pointer;color:#6366f1;font-weight:600;">⭐ Upgrade to download full report →</span>', unsafe_allow_html=True)
        return
    
    # Pro: full download
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
