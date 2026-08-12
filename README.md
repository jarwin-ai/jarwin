# Jarwin - Adaptive Architecture Blueprint System

**Live App**: [jarwin-ai.streamlit.app](https://jarwin-ai.streamlit.app)

Your AI Architecture Advisor that generates E2E technology architecture recommendations with dual-path (OSS vs Licensed) comparison and compliance mapping.

## What It Does

- **Chat Mode**: Talk to Jarwin naturally — describe your company and get architecture advice
- **Maturity Assessment**: Determines your current architecture maturity level (1-5)
- **Progressive Roadmap**: Generates phased architecture plan from current to target state
- **Dual-Path Recommendations**: For every component, compares OSS and Licensed options with TCO
- **Compliance Mapping**: Validates architecture against HIPAA, PCI-DSS, SOC2, GDPR, ISO27001
- **Cost Projections**: Full TCO comparison across all paths
- **Agent Collaboration**: Agents validate each other's recommendations (budget, conflicts, compliance)
- **Memory**: Remembers your company profile across sessions

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional: Enable AI Chat (Free, Local)

```bash
brew install ollama
ollama serve
ollama pull llama3
```

Jarwin works without Ollama (rule-based mode), but with it, chat becomes AI-powered.

## Tech Stack

- Python + Streamlit (UI)
- 6 Specialized Agents (Context, Maturity, Tool, Compliance, Blueprint, Chat)
- Agent Collaboration & Validation layer
- SQLite Memory (session persistence)
- LLM Engine (Ollama local / OpenAI optional)
- Structured Knowledge Base (50+ tools, 5 compliance frameworks, 5 maturity patterns)

## Architecture

```
User → Chat/Form → Context Agent → Maturity Agent → Tool Agent → Compliance Agent → Blueprint Agent
                                                                         ↑
                                                              Collaboration Agent (validates all)
```

## License

MIT
