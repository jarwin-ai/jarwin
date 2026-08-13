# Jarwin — Documentation

## Overview

Jarwin is an Adaptive Architecture Blueprint System — a multi-agent AI platform that generates end-to-end technology architecture recommendations for companies based on their industry, size, compliance requirements, and budget.

**Live App**: https://jarwin-ai.streamlit.app  
**Source Code**: https://github.com/jarwin-ai/jarwin

---

## How It Works

### User Flow

1. User visits `jarwin-ai.streamlit.app`
2. Chooses **Chat Mode** (conversational) or **Quick Mode** (form-based)
3. Provides company details (industry, team size, budget, compliance needs)
4. Jarwin's agents collaborate to generate a complete architecture blueprint
5. User receives: roadmap, tool recommendations, compliance report, cost analysis
6. User can download the report as JSON

### Agent Pipeline

```
User Input
    │
    ▼
Context Agent — structures raw input into standardized profile
    │
    ▼
Maturity Agent — determines current level (1-5) and target level
    │
    ▼
Tool Agent — for each component, finds best OSS and Licensed tools
    │
    ▼
Compliance Agent — validates all recommendations against regulatory frameworks
    │
    ▼
Collaboration Agent — cross-checks for budget overruns, conflicts, gaps
    │
    ▼
Blueprint Agent — assembles final output with cost projections
    │
    ▼
Output: Architecture Blueprint (JSON + UI visualization)
```

---

## Maturity Levels

| Level | Name | Description | Typical Team |
|-------|------|-------------|-------------|
| 1 | Foundation | Single-region monolith, basic monitoring | 1-5 engineers |
| 2 | Structured | Multi-AZ, automated CI/CD, APM | 5-20 engineers |
| 3 | Scalable | Multi-region, microservices, service mesh | 20-100 engineers |
| 4 | Resilient | Active-active, event sourcing, progressive delivery | 50-500 engineers |
| 5 | Optimized | Global edge, self-healing, AI-driven ops | 200+ engineers |

---

## Scoring Algorithm

Each tool is scored using a weighted formula:

```
Score = α×Compatibility + β×TCO + γ×Compliance + δ×Health + ε×Integration + ζ×TeamFit
```

Where:
- **Compatibility** (20%): How well the tool fits requirements
- **TCO** (25%): Total cost of ownership (lower = better score)
- **Compliance** (30%): Coverage of required regulatory frameworks
- **Health** (20%): Community health (OSS) or vendor stability (Licensed)
- **Team Fit** (15%): Match with team's existing skills

---

## TCO Calculation

For each tool, TCO includes:
- **Direct costs**: License fees, subscription costs
- **Operational costs**: Maintenance time × team hourly rate
- **Infrastructure costs**: Server/hosting costs for self-managed tools
- **Total**: Sum projected over 36 months

---

## Compliance Frameworks Supported

| Framework | Industries | Key Controls |
|-----------|-----------|-------------|
| HIPAA | Healthcare, Health Tech | Encryption, audit logs, BAA, access control |
| PCI-DSS | Fintech, E-commerce, Banking | Network segmentation, WAF, vulnerability scanning |
| SOC2 | SaaS, Enterprise Software | Access control, change management, monitoring |
| GDPR | Any (EU users) | Data residency, consent, right to erasure |
| ISO27001 | Enterprise, Government | ISMS policy, risk assessment, business continuity |

---

## API / Programmatic Usage

Currently Jarwin runs as a Streamlit web app. API access is planned for Pro users.

To use programmatically (local):

```python
from agents.context_agent import analyze_context
from agents.maturity_agent import assess_maturity
from agents.tool_agent import recommend_tools
from agents.compliance_agent import check_compliance
from agents.blueprint_agent import generate_blueprint

# Define your company
user_inputs = {
    "industry": "fintech",
    "team_size": 15,
    "monthly_users": 50000,
    "budget_monthly": 5000,
    "growth_stage": "series_a",
    "cloud_preference": "aws",
    "oss_preference": "balanced",
    "regions": ["us", "eu"],
    "uptime_sla": 99.9,
}

# Run the pipeline
context = analyze_context(user_inputs)
maturity = assess_maturity(context)
recommendations = recommend_tools(context, maturity)
compliance = check_compliance(context, recommendations)
blueprint = generate_blueprint(context, maturity, recommendations, compliance)

# blueprint is a dict with full architecture plan
print(blueprint["executive_summary"])
```

---

## Admin Dashboard

Access at: `https://jarwin-ai.streamlit.app/?admin=jarwin2024`

Shows:
- Total blueprints generated
- Today's usage
- Weekly usage
- Total page visits
- Top industries
- Chat vs Form mode split

---

## Deployment

### Streamlit Cloud (Current — Free)
- Auto-deploys on every `git push` to `main` branch
- URL: `jarwin-ai.streamlit.app`
- Zero configuration needed

### Self-Hosted (Alternative)
```bash
git clone https://github.com/jarwin-ai/jarwin.git
cd jarwin
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

---

## Roadmap

| Timeline | Feature |
|----------|---------|
| Done | V1: Core agents + Form UI |
| Done | V2: Chat + LLM + Memory + Collaboration |
| Done | Analytics + Pro paywall |
| Next | PDF export for Pro users |
| Next | More tools in knowledge base (200+) |
| Next | API access for Pro users |
| Future | Lifecycle monitoring (detect when to transition phases) |
| Future | Infrastructure-as-Code output (Terraform/Pulumi) |
| Future | Custom domain (jarwin.ai) |

---

## Contact

- GitHub: https://github.com/jarwin-ai
- App: https://jarwin-ai.streamlit.app
