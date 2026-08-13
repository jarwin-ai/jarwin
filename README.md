# Jarwin - Adaptive Architecture Blueprint System

**Live App**: [jarwin-ai.streamlit.app](https://jarwin-ai.streamlit.app)

Your AI Architecture Advisor that generates E2E technology architecture recommendations with dual-path (OSS vs Licensed) comparison, compliance mapping, and progressive maturity roadmap.

---

## Features

### Core Capabilities
- **Chat Mode** — Talk to Jarwin naturally, describe your company, get architecture advice instantly
- **Quick Mode (Form)** — Fill structured inputs for precise recommendations
- **Maturity Assessment** — Determines your architecture maturity level (1-5) with growth timeline
- **Progressive Roadmap** — Phased architecture plan from current state to target
- **Dual-Path Recommendations** — Every component shows OSS vs Licensed with TCO calculation
- **Compliance Mapping** — Auto-validates against HIPAA, PCI-DSS, SOC2, GDPR, ISO27001
- **Cost Projections** — Full TCO comparison across OSS, Licensed, and Recommended paths

### V2 Features
- **Agent Collaboration** — Agents validate each other (budget check, tool conflicts, compliance gaps)
- **LLM Integration** — Supports Ollama (free, local) or OpenAI (optional)
- **Session Memory** — Remembers company profiles across sessions (SQLite)
- **Usage Analytics** — Track blueprints generated, top industries, mode usage
- **Pro Plan** — Free tier (3 blueprints/month) + Pro tier (unlimited)

---

## Quick Start (Local)

```bash
git clone https://github.com/jarwin-ai/jarwin.git
cd jarwin
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Optional: Enable AI-Powered Chat (Free)

```bash
brew install ollama
ollama serve
ollama pull llama3
```

Without Ollama, Jarwin works in structured mode (rule-based). With Ollama, chat becomes AI-powered.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JARWIN SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT (Chat or Form)                                       │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Context     │→ │ Maturity     │→ │ Tool Recommender  │  │
│  │ Agent       │  │ Agent        │  │ (Dual-Path)       │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│                                             │               │
│                                             ▼               │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Blueprint   │← │ Compliance   │← │ Collaboration     │  │
│  │ Agent       │  │ Agent        │  │ Agent (Validator)  │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
│       │                                                     │
│       ▼                                                     │
│  OUTPUT: Blueprint + Compliance Report + Cost Analysis      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  SUPPORT SYSTEMS                                            │
│  • LLM Engine (Ollama / OpenAI)                             │
│  • Knowledge Base (50+ tools, 5 compliance frameworks)      │
│  • Memory (SQLite — session persistence)                    │
│  • Analytics (usage tracking)                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend/UI | Streamlit |
| Agents | Custom Python (6 specialized agents) |
| LLM | Ollama (local, free) / OpenAI (optional) |
| Database | SQLite (memory + analytics) |
| Knowledge Base | JSON (tools, compliance, patterns) |
| Hosting | Streamlit Cloud (free) |
| Source Control | GitHub |

---

## Knowledge Base

| Category | Public (Demo) | Pro (Full) |
|----------|--------------|-----------|
| **Tools** | 15 tools across 7 layers | 50+ tools with detailed profiles |
| **Compliance** | SOC2 only | HIPAA, PCI-DSS, SOC2, GDPR, ISO27001 |
| **Maturity Patterns** | Levels 1-2 | All 5 levels (Foundation → Optimized) |
| **Industries** | SaaS, Fintech, Healthcare | All 14 industry verticals |

---

## Agents

| Agent | Role |
|-------|------|
| **Context Agent** | Extracts and structures company requirements |
| **Maturity Agent** | Assesses current level, determines target, computes timeline |
| **Tool Agent** | Dual-path OSS vs Licensed recommendations with TCO |
| **Compliance Agent** | Validates against regulatory frameworks |
| **Blueprint Agent** | Assembles final output with cost projections |
| **Chat Agent** | Natural language interface with intent detection |
| **Collaboration Agent** | Cross-validates all recommendations |

---

## Plans & Pricing

| Feature | Free (Demo) | Pro ($29/mo) |
|---------|------|-------------|
| Blueprints/month | 1 | Unlimited |
| Tools in database | 15 | 50+ |
| Compliance frameworks | SOC2 only | HIPAA, PCI-DSS, SOC2, GDPR, ISO27001 |
| Industries | 3 | All 14 |
| Maturity levels | 1-2 | All 5 |
| Agent collaboration | — | Full validation |
| TCO detail | Basic | Detailed breakdown |
| PDF export | — | Yes |
| Priority support | — | Yes |

**Upgrade**: Contact krishnask921@gmail.com

---

## Project Structure

```
jarwin/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── agents/
│   ├── context_agent.py            # Requirement analysis
│   ├── maturity_agent.py           # Maturity assessment
│   ├── tool_agent.py               # Dual-path tool recommendations
│   ├── compliance_agent.py         # Regulatory validation
│   ├── blueprint_agent.py          # Output assembly
│   ├── chat_agent.py               # Conversational interface
│   ├── collaboration.py            # Agent cross-validation
│   ├── llm_engine.py               # LLM provider abstraction
│   ├── memory.py                   # Session persistence
│   └── analytics.py                # Usage tracking
├── knowledge_base/
│   ├── tools/tool_database.json    # 50+ tool profiles
│   ├── compliance/frameworks.json  # 5 regulatory frameworks
│   └── patterns/maturity_patterns.json  # 5 maturity levels
└── .env.example                    # Configuration template
```

---

## Contributing

Pull requests welcome! Areas to contribute:
- Add more tools to `knowledge_base/tools/tool_database.json`
- Add more compliance frameworks
- Improve scoring algorithms
- UI/UX improvements

---

## License

This project uses a **Business Source License**. See [LICENSE](LICENSE) for details.

- You may view and study the code for learning
- You may NOT use it to build a competing product
- For commercial licensing: krishnask921@gmail.com

---

**Built by [jarwin-ai](https://github.com/jarwin-ai) — Architecture intelligence for every company.**
