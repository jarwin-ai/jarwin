# Jarwin - Adaptive Architecture Blueprint System

Your AI Architecture Advisor that generates E2E technology architecture recommendations with dual-path (OSS vs Licensed) comparison and compliance mapping.

## What It Does

- **Maturity Assessment**: Determines your current architecture maturity level (1-5)
- **Progressive Roadmap**: Generates phased architecture plan from current to target state
- **Dual-Path Recommendations**: For every component, compares OSS and Licensed options with TCO
- **Compliance Mapping**: Validates architecture against HIPAA, PCI-DSS, SOC2, GDPR, ISO27001
- **Cost Projections**: Full TCO comparison across all paths

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to share.streamlit.io
3. Connect your repo
4. Deploy!

## Tech Stack

- Python + Streamlit (UI)
- Custom multi-agent architecture (Context, Maturity, Tool, Compliance, Blueprint agents)
- Structured knowledge base (not LLM hallucinations)
