"""
Jarwin Chat Agent
Handles conversational interaction — understands user intent,
extracts requirements through natural dialogue, and routes to specialist agents.
"""

from agents.llm_engine import get_llm
from agents.context_agent import analyze_context, INDUSTRY_MAP, GROWTH_STAGES
from agents.maturity_agent import assess_maturity
from agents.tool_agent import recommend_tools
from agents.compliance_agent import check_compliance
from agents.blueprint_agent import generate_blueprint

SYSTEM_PROMPT = """You are Jarwin, an AI Architecture Advisor. You help companies design their technology architecture.

Your job:
1. Understand the company's needs through conversation
2. Ask clarifying questions if needed (industry, team size, budget, etc.)
3. Provide architecture recommendations

You are friendly, concise, and expert. You speak like a senior solutions architect.

When you have enough info to make recommendations, structure your response clearly with:
- Current assessment
- Recommended tools (always show OSS vs Licensed options)
- Compliance notes
- Cost estimates

If the user asks a specific question about tools, architecture patterns, or best practices, answer directly without needing all company details.

Always be helpful even with partial information — make reasonable assumptions and state them."""


EXTRACT_PROMPT = """Extract company details from this conversation. Return ONLY valid JSON, no other text.

If a field is not mentioned, use the default value shown.

Required JSON format:
{
  "industry": "saas",
  "team_size": 10,
  "monthly_users": 10000,
  "budget_monthly": 2000,
  "growth_stage": "seed",
  "cloud_preference": "any",
  "oss_preference": "balanced",
  "regions": ["us"],
  "uptime_sla": 99.9
}

Valid industries: healthcare, health_tech, fintech, banking, ecommerce, saas, enterprise_software, edtech, gaming, social_media, logistics, government, retail, media, other
Valid stages: pre-seed, seed, series_a, series_b, series_c, growth, enterprise
Valid cloud: any, aws, gcp, azure, multi-cloud
Valid oss_preference: oss_first, balanced, licensed_first

Conversation:
"""


def extract_context_from_chat(messages: list) -> dict:
    """Try to extract company context from chat messages using LLM or fallback."""
    llm = get_llm()
    
    # Build conversation text
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages if m['role'] == 'user'])
    
    if llm.available:
        response = llm.generate(
            prompt=EXTRACT_PROMPT + conversation,
            system_prompt="You extract structured data from conversations. Return ONLY valid JSON.",
            temperature=0.1
        )
        if response:
            try:
                # Try to parse JSON from response
                import json
                # Find JSON in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    extracted = json.loads(response[start:end])
                    return extracted
            except:
                pass
    
    # Fallback: keyword extraction
    return extract_context_keywords(conversation)


def extract_context_keywords(text: str) -> dict:
    """Simple keyword-based extraction when LLM is not available."""
    text_lower = text.lower()
    
    # Detect industry
    industry = "saas"
    for ind in INDUSTRY_MAP.keys():
        if ind.replace("_", " ") in text_lower or ind in text_lower:
            industry = ind
            break
    
    # Detect team size
    team_size = 10
    import re
    team_matches = re.findall(r'(\d+)\s*(?:engineers?|developers?|devs?|people|team)', text_lower)
    if team_matches:
        team_size = int(team_matches[0])
    
    # Detect users
    monthly_users = 10000
    user_matches = re.findall(r'(\d+[kKmM]?)\s*(?:users?|customers?|visitors?)', text_lower)
    if user_matches:
        val = user_matches[0].lower()
        if 'k' in val:
            monthly_users = int(float(val.replace('k', '')) * 1000)
        elif 'm' in val:
            monthly_users = int(float(val.replace('m', '')) * 1_000_000)
        else:
            monthly_users = int(val)
    
    # Detect budget
    budget = 2000
    budget_matches = re.findall(r'\$(\d+[kK]?)', text)
    if budget_matches:
        val = budget_matches[0].lower()
        if 'k' in val:
            budget = int(float(val.replace('k', '')) * 1000)
        else:
            budget = int(val)
    
    # Detect growth stage
    growth_stage = "seed"
    for stage in GROWTH_STAGES:
        if stage.replace("_", " ") in text_lower:
            growth_stage = stage
            break
    
    # Detect cloud
    cloud = "any"
    if "aws" in text_lower:
        cloud = "aws"
    elif "gcp" in text_lower or "google cloud" in text_lower:
        cloud = "gcp"
    elif "azure" in text_lower:
        cloud = "azure"
    
    # Detect regions
    regions = ["us"]
    if "eu" in text_lower or "europe" in text_lower:
        regions.append("eu")
    if "india" in text_lower:
        regions.append("india")
    if "global" in text_lower:
        regions = ["global"]
    
    return {
        "industry": industry,
        "team_size": team_size,
        "monthly_users": monthly_users,
        "budget_monthly": budget,
        "growth_stage": growth_stage,
        "cloud_preference": cloud,
        "oss_preference": "balanced",
        "regions": regions,
        "uptime_sla": 99.9,
    }


def generate_chat_response(messages: list, context: dict = None) -> dict:
    """
    Generate a response in chat mode.
    Returns: {"response": str, "context": dict or None, "blueprint": dict or None}
    """
    llm = get_llm()
    last_message = messages[-1]["content"] if messages else ""
    last_lower = last_message.lower()
    
    # Check if user explicitly wants to generate architecture
    explicit_triggers = ["generate", "recommend", "build my", "design my", "create blueprint", "give me architecture"]
    wants_architecture = any(w in last_lower for w in explicit_triggers)
    
    # Extract what we know so far from conversation
    user_inputs = extract_context_from_chat(messages)
    
    # Check what's missing
    missing_fields = []
    if user_inputs.get("budget_monthly", 2000) == 2000 and "budget" not in last_lower and "$" not in last_message:
        missing_fields.append("monthly tech budget")
    if user_inputs.get("growth_stage", "seed") == "seed" and not any(s in last_lower for s in ["seed", "series", "growth", "enterprise", "pre-seed"]):
        missing_fields.append("growth stage (seed, Series A/B/C, growth, enterprise)")
    if user_inputs.get("monthly_users", 10000) == 10000 and not any(w in last_lower for w in ["user", "customer", "visitor"]):
        missing_fields.append("expected monthly users")
    
    # If user wants architecture but key info is missing, ask first
    if wants_architecture and len(missing_fields) >= 2:
        fields_text = "\n".join([f"- **{f}**" for f in missing_fields])
        response = f"""I have some details but need a few more to give you the best recommendations:

{fields_text}

Share these and I'll generate your complete architecture blueprint!

Or say **"generate anyway"** and I'll use reasonable defaults for what's missing."""
        return {"response": response, "context": user_inputs, "blueprint": None}
    
    # If "generate anyway" or enough info available, produce blueprint
    force_generate = "generate anyway" in last_lower or "go ahead" in last_lower
    
    if (wants_architecture and len(missing_fields) < 2) or force_generate:
        # Override with any existing context
        if context:
            for key, val in context.items():
                if val and key in user_inputs:
                    user_inputs[key] = val
        
        # Run the full agent pipeline
        analyzed_context = analyze_context(user_inputs)
        maturity = assess_maturity(analyzed_context)
        recommendations = recommend_tools(analyzed_context, maturity)
        compliance = check_compliance(analyzed_context, recommendations)
        blueprint = generate_blueprint(analyzed_context, maturity, recommendations, compliance)
        
        # Generate summary response
        summary = format_blueprint_summary(blueprint)
        
        # If LLM available, make it conversational
        if llm.available:
            enhance_prompt = f"""Based on this architecture analysis, write a friendly, concise summary for the user.
            
Analysis:
{summary}

User's question: {last_message}

Write 3-5 paragraphs. Be specific about tool names and costs. Be conversational."""
            
            enhanced = llm.generate(enhance_prompt, SYSTEM_PROMPT, 0.7)
            if enhanced:
                return {"response": enhanced, "context": user_inputs, "blueprint": blueprint}
        
        return {"response": summary, "context": user_inputs, "blueprint": blueprint}
    
    # Not generating — continue conversation
    # If we extracted some context, acknowledge it
    extracted_info = []
    if user_inputs.get("industry") != "saas":
        extracted_info.append(f"Industry: **{user_inputs['industry'].replace('_', ' ').title()}**")
    if user_inputs.get("team_size") != 10:
        extracted_info.append(f"Team: **{user_inputs['team_size']} engineers**")
    if user_inputs.get("cloud_preference") != "any":
        extracted_info.append(f"Cloud: **{user_inputs['cloud_preference'].upper()}**")
    
    if extracted_info:
        info_text = ", ".join(extracted_info)
        missing_text = "\n".join([f"- {f}" for f in missing_fields[:3]])
        
        response = f"""Got it! Here's what I have so far: {info_text}

To generate your architecture blueprint, I still need:
{missing_text}

Or say **"generate"** and I'll work with what I have (using defaults for the rest)."""
        return {"response": response, "context": user_inputs, "blueprint": None}
    
    # No context extracted — answer the specific question using fallback
    fallback = generate_fallback_response(last_message, messages)
    return {"response": fallback, "context": user_inputs, "blueprint": None}


def generate_fallback_response(message: str, messages: list) -> str:
    """Generate smart response without LLM using enhanced rules."""
    msg_lower = message.lower()
    
    if len(messages) <= 1:
        return """Hey! I'm **Jarwin AI**, your Architecture Advisor. 👋

I help companies design their complete technology stack — from databases to deployment.

To get started, just tell me:
1. What **industry** are you in?
2. How big is your **engineering team**?
3. What's your **monthly tech budget**?
4. How many **users** do you expect?

Or just describe your project and I'll ask the right questions!"""
    
    if msg_lower.strip() in ["hello", "hi", "hey", "hi there", "hello there", "hey there"]:
        return "Hey! What are you building? Tell me your industry and team size and I'll design the perfect architecture for you."
    
    if "help" in msg_lower or "what can you do" in msg_lower:
        return """I can help you with:

**Full Architecture Design:**
→ Tell me your industry, team size, budget, and I'll design your complete stack

**Tool Comparisons:**
→ "PostgreSQL vs MySQL for fintech?"
→ "Best monitoring tool for a 10-person team?"

**Compliance Guidance:**
→ "What do I need for HIPAA compliance?"
→ "Is Supabase SOC2 compliant?"

**Cost Optimization:**
→ "How to keep infra costs under $3000/month?"

Just ask!"""

    # Database questions
    if any(w in msg_lower for w in ["database", "db", "postgres", "mysql", "mongo", "supabase", "firebase"]):
        if "vs" in msg_lower:
            return """**PostgreSQL vs MySQL:**

| Factor | PostgreSQL | MySQL |
|--------|-----------|-------|
| Complex queries | Better (CTEs, window functions) | Basic |
| JSON support | Excellent (JSONB) | Limited |
| Scalability | High (with partitioning) | High (simpler sharding) |
| Learning curve | Medium | Easier |
| Best for | Fintech, analytics, complex data | Simple CRUD, blogs, CMS |

**My recommendation:** PostgreSQL for most modern apps. MySQL only if team already knows it well.

Want me to generate a full architecture? Tell me your industry and team size."""
        return """**Database Recommendations:**

- **PostgreSQL** → Best all-rounder. Free, scales well, great for fintech/SaaS
- **Supabase** → PostgreSQL + auth + APIs built-in. Best for MVPs and small teams
- **AWS Aurora** → Managed PostgreSQL. Best when team is small but needs enterprise reliability
- **PlanetScale** → Serverless MySQL. Best for global apps with auto-scaling

What's your industry and team size? I'll narrow it down."""

    # Cloud questions
    if any(w in msg_lower for w in ["aws", "gcp", "azure", "cloud", "which cloud"]):
        return """**Cloud Platform Guide:**

| Factor | AWS | GCP | Azure |
|--------|-----|-----|-------|
| Market share | #1 (32%) | #3 (12%) | #2 (23%) |
| Best for | Everything (most services) | AI/ML, data analytics | Microsoft shops |
| Startup credits | $100K | $100K | $150K |
| Learning curve | Steep | Medium | Steep |

**Quick guide:**
- **Startup, no preference** → AWS (most docs, hiring pool)
- **AI/ML heavy** → GCP
- **Microsoft ecosystem** → Azure
- **Budget-conscious** → Start with DigitalOcean, migrate later

What's your team's current experience?"""

    # Compliance questions
    if any(w in msg_lower for w in ["compliance", "hipaa", "pci", "gdpr", "soc", "iso"]):
        if "hipaa" in msg_lower:
            return """**HIPAA (Healthcare):**
- Encryption at rest (AES-256) + in transit (TLS 1.2+)
- Audit logging for all PHI access
- Business Associate Agreement (BAA) with every vendor
- Access controls with minimum necessary privilege

**HIPAA-compliant tools:** AWS, GCP, Azure, Auth0, Datadog, MongoDB Atlas, Supabase (paid)

Want me to design a HIPAA-compliant architecture? Tell me your team size and budget."""
        if "pci" in msg_lower:
            return """**PCI-DSS (Payments/Fintech):**
- Network segmentation (isolate cardholder data)
- Web Application Firewall (WAF) required
- Quarterly vulnerability scans
- Encrypt all card data at rest and in transit

**Key tools needed:** WAF (Cloudflare), scanner (Snyk/Trivy), SIEM, encryption (KMS)

Say **"generate"** with your details and I'll build a PCI-compliant architecture."""
        return """**Compliance Frameworks:**
- **HIPAA** → Healthcare / health data
- **PCI-DSS** → Payments / card data
- **SOC2** → SaaS selling to enterprise
- **GDPR** → Users in EU
- **ISO27001** → Global enterprise / government

Tell me your industry and I'll identify what applies to you."""

    # Cost questions
    if any(w in msg_lower for w in ["cost", "budget", "cheap", "expensive", "save", "pricing", "how much"]):
        return """**Cost Guide by Budget:**

**Under $1,000/month:**
→ All OSS: PostgreSQL + Redis + Docker + Nginx + GitHub Actions + Prometheus
→ Host on DigitalOcean ($50-200/mo)

**$1,000 - $5,000/month:**
→ Mix: managed DB (Aurora) + OSS monitoring + GitHub Actions
→ Best balance of cost and operational effort

**$5,000+/month:**
→ Best-of-breed, multi-region, full observability
→ Focus on reliability over cost

What's your budget? I'll design within it."""

    # Architecture pattern questions
    if any(w in msg_lower for w in ["monolith", "microservice", "serverless", "architecture pattern", "pattern"]):
        return """**Architecture Patterns:**

**Monolith** (teams < 15):
→ Start here. Simpler, faster to ship.

**Modular Monolith** (teams 10-30):
→ Single deployment, code organized by domain. Best middle ground.

**Microservices** (teams > 20):
→ Only when you NEED independent scaling per service.
→ Requires: service mesh, distributed tracing, CI/CD per service.

**Rule of thumb:** Start monolith. Split only when you hit real pain. Most startups split too early.

What's your team size?"""

    # Monitoring questions
    if any(w in msg_lower for w in ["monitoring", "datadog", "grafana", "prometheus", "observability", "logging", "alerting"]):
        return """**Monitoring & Observability:**

| Tool | Type | Cost | Best For |
|------|------|------|----------|
| **Prometheus + Grafana** | OSS | Free | DevOps-skilled teams |
| **Datadog** | Licensed | $100+/mo | Managed, easy setup |
| **New Relic** | Licensed | Free tier | Getting started |
| **Sentry** | OSS/Freemium | Free | Error tracking |

**By team size:**
- **< 5 engineers:** Sentry + UptimeRobot (free)
- **5-20 engineers:** Datadog or New Relic
- **20+ engineers:** Prometheus + Grafana + Jaeger

What's your team size and main concern?"""

    # CI/CD questions
    if any(w in msg_lower for w in ["ci/cd", "cicd", "deploy", "pipeline", "github actions", "jenkins"]):
        return """**CI/CD Recommendations:**

- **GitHub Actions** → Free (2000 min/mo). Best for most teams on GitHub.
- **GitLab CI** → Free tier. Best for GitLab users.
- **ArgoCD** → Free. Best for Kubernetes + GitOps.
- **Jenkins** → Free (self-host). Enterprise with complex needs.

**90% of startups should just use GitHub Actions.** It's free, integrated, and powerful.

Want me to include CI/CD in a full architecture blueprint? Say **"generate"** with your details."""

    # Auth questions
    if any(w in msg_lower for w in ["auth", "login", "authentication", "oauth", "sso"]):
        return """**Authentication Recommendations:**

- **Auth0/Okta** → Best managed solution. Free tier, SOC2/HIPAA compliant.
- **Clerk** → Modern, developer-friendly. Great DX.
- **Supertokens** → Open source alternative. Self-host or managed.
- **Keycloak** → Enterprise OSS. Powerful but complex.
- **AWS Cognito** → Cheapest at scale. Harder DX.

**Quick pick:**
- Small team, want easy? → **Clerk** or **Auth0**
- Need compliance? → **Auth0** (has all certs)
- Want OSS control? → **Supertokens**"""

    # If nothing specific matches, be helpful
    return f"""Got it! To give you the best advice about *"{message[:50]}"*, I need a bit more context:

- Your **industry** (fintech, healthcare, SaaS, etc.)
- Your **team size**
- Your **budget**

Or ask me specific questions like:
- "PostgreSQL vs MySQL?"
- "Best cloud for a startup?"
- "What do I need for HIPAA?"
- "Design architecture for fintech"

What would you like to know?"""


def format_blueprint_summary(blueprint: dict) -> str:
    """Format blueprint into a readable chat message."""
    summary = blueprint["executive_summary"]
    costs = blueprint["cost_projection"]
    maturity = blueprint["maturity_assessment"]
    
    text = f"""## Architecture Blueprint Generated! 🏗️

**Your Assessment:**
- Current: {summary['current_level']}
- Target: {summary['target_level']}  
- Timeline: {summary['timeline']}
- Compliance: {summary['compliance_status']}

**Cost Comparison (Monthly):**
- 🟢 Full OSS Path: ${costs['oss_path']['monthly']:,.0f}/mo
- 🔵 Full Licensed Path: ${costs['licensed_path']['monthly']:,.0f}/mo
- ⭐ Recommended Mix: ${costs['recommended_path']['monthly']:,.0f}/mo

**Key Recommendations (Phase 1):**
"""
    
    if maturity["phases"]:
        recs = blueprint["architecture_recommendations"]
        if recs:
            for comp in recs[0]["components"][:5]:  # Show first 5
                verdict = comp.get("verdict", "")
                if verdict == "OSS":
                    tool = comp.get("oss_recommendation", {}).get("name", "N/A")
                    text += f"- **{comp['component'].replace('_',' ').title()}**: 🟢 {tool}\n"
                elif verdict == "LICENSED":
                    tool = comp.get("licensed_recommendation", {}).get("name", "N/A")
                    text += f"- **{comp['component'].replace('_',' ').title()}**: 🔵 {tool}\n"
                else:
                    oss = comp.get("oss_recommendation", {}).get("name", "N/A")
                    text += f"- **{comp['component'].replace('_',' ').title()}**: 🟢 {oss} (either path works)\n"
    
    text += "\n*Switch to the 'Full Report' tab for detailed breakdown, or ask me questions about specific components!*"
    
    return text
