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
    
    # Check if user wants to generate architecture
    trigger_words = ["generate", "recommend", "build", "design", "architecture", "what should i use",
                     "suggest", "blueprint", "advise", "help me choose"]
    wants_architecture = any(w in last_lower for w in trigger_words)
    
    # If enough context and user wants architecture, generate it
    if wants_architecture or (context and len(messages) >= 2):
        # Extract context from conversation
        user_inputs = extract_context_from_chat(messages)
        
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
    
    # General conversation - use LLM if available
    if llm.available:
        conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        response = llm.generate(
            prompt=f"Conversation so far:\n{conversation_text}\n\nRespond as Jarwin:",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7
        )
        if response:
            return {"response": response, "context": None, "blueprint": None}
    
    # Fallback: rule-based responses
    return {"response": generate_fallback_response(last_message, messages), "context": None, "blueprint": None}


def generate_fallback_response(message: str, messages: list) -> str:
    """Generate response without LLM using rules."""
    msg_lower = message.lower()
    
    if len(messages) <= 1:
        return """Hey! I'm Jarwin, your AI Architecture Advisor. 👋

I help companies design their complete technology stack — from databases to deployment.

To get started, tell me about your company:
- What **industry** are you in?
- How big is your **engineering team**?
- What's your **monthly tech budget**?
- Any **compliance** requirements (HIPAA, PCI-DSS, SOC2)?

Or just describe what you're building and I'll figure out the rest!"""
    
    if "hello" in msg_lower or "hi" in msg_lower or "hey" in msg_lower:
        return "Hey! Tell me about what you're building and I'll help you design the architecture."
    
    if "help" in msg_lower:
        return """I can help you with:

1. **Full architecture blueprint** — tell me your industry, team size, and budget
2. **Tool comparison** — "Should I use PostgreSQL or MongoDB?"
3. **Compliance guidance** — "What do I need for HIPAA compliance?"
4. **Cost optimization** — "How to reduce my cloud bill?"

What would you like help with?"""
    
    if any(w in msg_lower for w in ["database", "db", "postgres", "mysql", "mongo"]):
        return """For databases, I recommend based on your needs:

**Relational (structured data):**
- 🟢 OSS: PostgreSQL (free, powerful, scales well)
- 🔵 Licensed: AWS Aurora ($30+/mo, managed, auto-scaling)

**Document/NoSQL:**
- 🟢 OSS: MongoDB Community (free, flexible schema)
- 🔵 Licensed: MongoDB Atlas ($0-57+/mo, fully managed)

Tell me more about your use case (data size, read/write patterns, team expertise) and I'll narrow it down."""

    if any(w in msg_lower for w in ["compliance", "hipaa", "pci", "gdpr", "soc"]):
        return """Compliance requirements significantly affect your architecture choices. Here's a quick overview:

- **HIPAA** (Healthcare): Need encryption at rest + transit, audit logging, BAA with vendors
- **PCI-DSS** (Payments): Network segmentation, WAF, vulnerability scanning, encrypted card data
- **SOC2** (SaaS): Access controls, change management, monitoring, incident response
- **GDPR** (EU users): Data residency in EU, consent management, right to erasure

Which frameworks apply to you? I'll filter my recommendations to only compliant tools."""

    # Default: ask for more details
    return """Thanks for that info! To give you the best architecture recommendation, I still need:

- **Industry**: What sector are you in?
- **Scale**: How many users do you expect?
- **Budget**: Monthly tech spend?

Or just say **"generate"** and I'll work with what I have so far!"""


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
