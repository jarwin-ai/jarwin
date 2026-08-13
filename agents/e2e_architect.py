"""
Jarwin E2E Architecture Engine
Generates complete 14-section architecture blueprint based on company context.
"""


def generate_architecture_pattern(context: dict, maturity: dict) -> dict:
    """Recommend architecture pattern based on team size and maturity."""
    team = context["organization"]["team_size"]
    level = maturity["current_level"]
    industry = context["organization"]["industry"]
    
    if team <= 10 or level <= 1:
        pattern = "Monolith"
        description = "Single deployable unit. Simple, fast to ship, easy to debug."
        reasoning = f"With {team} engineers, a monolith keeps complexity low and velocity high."
        next_step = "Transition to Modular Monolith when team exceeds 15 or deploy frequency exceeds 10/week."
    elif team <= 30 or level == 2:
        pattern = "Modular Monolith"
        description = "Single deployment, code organized by business domain with clear boundaries."
        reasoning = f"Team of {team} benefits from domain separation without microservices overhead."
        next_step = "Extract high-traffic domains into independent services when scaling demands it."
    elif team <= 100 or level == 3:
        pattern = "Microservices"
        description = "Independent services per business domain. Independent deployment and scaling."
        reasoning = f"With {team} engineers across multiple teams, microservices enable parallel development."
        next_step = "Add service mesh and event-driven patterns as service count exceeds 20."
    else:
        pattern = "Domain-Driven Microservices + Event Sourcing"
        description = "Event-driven architecture with CQRS. Full domain isolation with eventual consistency."
        reasoning = f"Enterprise scale ({team} engineers) requires domain-driven design for team autonomy."
        next_step = "Implement saga patterns for cross-domain transactions."
    
    return {
        "pattern": pattern,
        "description": description,
        "reasoning": reasoning,
        "next_step": next_step,
        "preview": f"{pattern} — {description[:60]}..."
    }


def generate_code_framework(context: dict) -> dict:
    """Recommend programming languages and frameworks."""
    industry = context["organization"]["industry"]
    team = context["organization"]["team_size"]
    languages = context["technical"].get("language_preferences", [])
    
    # Backend recommendation
    if industry in ["fintech", "banking", "enterprise_software"]:
        backend = {"language": "Java / Kotlin", "framework": "Spring Boot", "reason": "Enterprise-grade, strong typing, excellent for financial systems"}
    elif industry in ["healthcare", "government"]:
        backend = {"language": "Python", "framework": "FastAPI + SQLAlchemy", "reason": "Clean code, strong ecosystem for data handling, HIPAA libraries available"}
    elif team <= 10:
        backend = {"language": "Python", "framework": "FastAPI", "reason": "Fast development, easy hiring, excellent for MVPs and rapid iteration"}
    elif team <= 30:
        backend = {"language": "TypeScript", "framework": "Node.js (NestJS)", "reason": "Full-stack TypeScript reduces context switching, great for API-heavy apps"}
    else:
        backend = {"language": "Go", "framework": "Gin / Fiber", "reason": "High performance, low resource usage, excellent for microservices at scale"}
    
    # Frontend recommendation
    if team <= 5:
        frontend = {"framework": "Next.js (React)", "reason": "Full-stack capability, SSR, largest ecosystem"}
    elif industry in ["enterprise_software"]:
        frontend = {"framework": "Angular", "reason": "Opinionated structure suits enterprise teams, built-in tools"}
    else:
        frontend = {"framework": "Next.js (React)", "reason": "Most versatile, largest talent pool, excellent DX"}
    
    return {
        "backend": backend,
        "frontend": frontend,
        "api_style": "REST + OpenAPI" if team <= 20 else "gRPC (internal) + REST (external)",
        "preview": f"{backend['language']} ({backend['framework']}) + {frontend['framework']}"
    }


def generate_devops_pipeline(context: dict, maturity: dict) -> dict:
    """Recommend DevOps pipeline and practices."""
    level = maturity["current_level"]
    cloud = context["technical"].get("cloud_preference", "any")
    
    if level <= 1:
        pipeline = {
            "ci_cd": "GitHub Actions",
            "branching": "GitHub Flow (main + feature branches)",
            "deployment": "Direct push to cloud (Railway/Render) or Docker Compose",
            "environments": "Production only (staging when team grows)",
            "containers": "Docker",
            "orchestration": "None needed yet",
        }
    elif level == 2:
        pipeline = {
            "ci_cd": "GitHub Actions + automated tests",
            "branching": "GitHub Flow with PR reviews",
            "deployment": "Docker → Container registry → ECS/Cloud Run",
            "environments": "Staging + Production",
            "containers": "Docker + Docker Compose",
            "orchestration": "ECS / Cloud Run (managed)",
        }
    elif level == 3:
        pipeline = {
            "ci_cd": "GitHub Actions + ArgoCD (GitOps)",
            "branching": "Trunk-based development with feature flags",
            "deployment": "GitOps: merge to main → auto-deploy via ArgoCD",
            "environments": "Dev + Staging + Production (per region)",
            "containers": "Docker + Kubernetes (EKS/GKE)",
            "orchestration": "Kubernetes + Helm charts",
        }
    else:
        pipeline = {
            "ci_cd": "GitHub Actions + ArgoCD + Argo Rollouts",
            "branching": "Trunk-based with feature flags (LaunchDarkly)",
            "deployment": "Progressive delivery: Canary → Blue/Green → Full rollout",
            "environments": "Dev + Staging + Pre-prod + Production (multi-region)",
            "containers": "Docker + Kubernetes (multi-cluster)",
            "orchestration": "Kubernetes + Istio service mesh + Argo Rollouts",
        }
    
    return {
        **pipeline,
        "preview": f"{pipeline['ci_cd']} → {pipeline['deployment'][:50]}..."
    }


def generate_infrastructure(context: dict, maturity: dict) -> dict:
    """Recommend infrastructure architecture."""
    cloud = context["technical"].get("cloud_preference", "aws")
    if cloud == "any":
        cloud = "aws"
    level = maturity["current_level"]
    regions = context["organization"].get("regions", ["us"])
    
    if level <= 1:
        infra = {
            "cloud_provider": cloud.upper(),
            "regions": "Single region (us-east-1)" if cloud == "aws" else "Single region",
            "networking": "Default VPC, public subnets, Security Groups",
            "compute": "2-3 instances or containers",
            "storage": "Single managed database + S3 for files",
            "cdn": "Cloudflare (free tier) for static assets",
            "dns": "Cloudflare DNS",
        }
    elif level == 2:
        infra = {
            "cloud_provider": cloud.upper(),
            "regions": "Single region, Multi-AZ",
            "networking": "Custom VPC: public subnet (ALB) + private subnet (app + DB)",
            "compute": "Container service (ECS/Cloud Run) with auto-scaling",
            "storage": "RDS Multi-AZ + S3 + ElastiCache",
            "cdn": "CloudFront / Cloudflare Pro",
            "dns": "Route53 / Cloudflare with health checks",
        }
    elif level == 3:
        infra = {
            "cloud_provider": cloud.upper(),
            "regions": f"Multi-region ({', '.join(regions)}), Active-Passive",
            "networking": "VPC peering, Transit Gateway, private subnets, NAT Gateway",
            "compute": "Kubernetes (EKS/GKE) with node auto-scaling",
            "storage": "Aurora Global DB + ElastiCache cluster + S3 cross-region replication",
            "cdn": "CloudFront with edge functions",
            "dns": "Route53 latency-based routing",
        }
    else:
        infra = {
            "cloud_provider": f"{cloud.upper()} (primary) + multi-cloud ready",
            "regions": "Global, Active-Active, Edge deployment",
            "networking": "Service mesh (Istio), zero-trust network, Global Accelerator",
            "compute": "Multi-cluster Kubernetes with federation",
            "storage": "CockroachDB/Spanner (global) + Redis Cluster + Data Lake",
            "cdn": "Global edge with compute (CloudFront Functions / Workers)",
            "dns": "Global traffic management with health-based failover",
        }
    
    return {
        **infra,
        "preview": f"{infra['cloud_provider']}, {infra['regions'][:40]}..."
    }


def generate_ai_ml_stack(context: dict) -> dict:
    """Recommend AI/ML stack if applicable."""
    industry = context["organization"]["industry"]
    budget = context["organization"]["budget_monthly_usd"]
    
    if budget < 1000:
        ai_stack = {
            "llm": "OpenAI API (GPT-4o-mini) — pay per use, cheapest quality option",
            "hosting": "API-based (no GPU needed)",
            "ml_ops": "Not needed at this stage",
            "vector_db": "Supabase pgvector (free tier)",
            "use_cases": "Chatbot, content generation, document processing",
        }
    elif budget < 5000:
        ai_stack = {
            "llm": "OpenAI GPT-4o (primary) + Anthropic Claude (fallback)",
            "hosting": "API-based + AWS Lambda for processing",
            "ml_ops": "Simple model versioning with MLflow",
            "vector_db": "Pinecone or Weaviate (managed)",
            "use_cases": "RAG, intelligent search, automation, customer support AI",
        }
    else:
        ai_stack = {
            "llm": "Fine-tuned models (Llama 3) + GPT-4o for complex tasks",
            "hosting": "AWS SageMaker / GCP Vertex AI for custom models",
            "ml_ops": "MLflow + Kubeflow for training pipelines",
            "vector_db": "Weaviate / Qdrant (self-hosted for data control)",
            "use_cases": "Custom models, real-time inference, predictive analytics, AI agents",
        }
    
    return {
        **ai_stack,
        "preview": f"{ai_stack['llm'][:50]}..."
    }


def generate_team_and_process(context: dict, maturity: dict) -> dict:
    """Recommend team organization + project management process (merged)."""
    team = context["organization"]["team_size"]
    
    if team <= 5:
        result = {
            "team_model": "Single cross-functional team — everyone does everything",
            "squads": "1 team (no squads needed yet)",
            "methodology": "Kanban — continuous flow, no heavy sprint ceremonies",
            "tool": "Linear Free or Notion boards",
            "standup": "Daily async (Slack bot or Geekbot) — 2 min each",
            "release_process": "Ship when ready — no release train",
            "communication": "Slack + daily async standup + weekly 30-min sync",
            "hiring_priority": "Full-stack engineer → then DevOps",
        }
    elif team <= 15:
        result = {
            "team_model": "2 squads: Product (features) + Platform (infra/DevOps)",
            "squads": "Product squad (5-8) + Platform squad (3-5)",
            "methodology": "Scrum — 2-week sprints with planning, review, retro",
            "tool": "Linear (recommended) or Jira Standard",
            "standup": "Daily sync standup (15 min) per squad",
            "release_process": "Weekly releases (Tuesdays) with changelog",
            "communication": "Slack + Notion wiki + weekly all-hands (30 min)",
            "hiring_priority": "Backend specialist → Frontend specialist → SRE",
        }
    elif team <= 50:
        result = {
            "team_model": "Domain-oriented squads (3-5 squads) + 1 platform team",
            "squads": "Squads by business domain (6-8 per squad) + shared platform",
            "methodology": "Scrum per squad + quarterly OKR planning",
            "tool": "Linear or Jira + Confluence for docs",
            "standup": "Squad standups (daily) + cross-squad sync (weekly)",
            "release_process": "Bi-weekly releases with feature flags",
            "communication": "Slack + Notion + bi-weekly demos + quarterly all-hands",
            "hiring_priority": "Engineering managers → Staff engineers → Security engineer",
        }
    else:
        result = {
            "team_model": "Tribes & Squads (Spotify model) with autonomous ownership",
            "squads": "Multiple tribes, 6-8 per squad, chapters for specialties",
            "methodology": "SAFe or custom scaled agile — quarterly PI planning",
            "tool": "Jira Premium + Jira Align (portfolio) + Confluence",
            "standup": "Squad daily → Scrum of Scrums (weekly) → ART sync (bi-weekly)",
            "release_process": "Release train (bi-weekly) + progressive rollout + feature flags",
            "communication": "Dedicated tools per tribe + architecture council + PI events",
            "hiring_priority": "VP Engineering → Principal architects → SRE team lead",
        }
    
    return {
        **result,
        "preview": f"{result['team_model'][:35]}... | {result['methodology'][:25]}..."
    }


def generate_security_architecture(context: dict, maturity: dict) -> dict:
    """Recommend security architecture."""
    level = maturity["current_level"]
    compliance = context["compliance"]["frameworks"]
    
    if level <= 1:
        security = {
            "auth": "Auth0 or Clerk (managed, handles everything)",
            "encryption": "TLS 1.3 (transit) + cloud-managed encryption at rest",
            "secrets": "Environment variables → migrate to Doppler/AWS Secrets Manager",
            "network": "Security Groups, HTTPS everywhere",
            "scanning": "GitHub Dependabot (free, automatic)",
            "model": "Perimeter security",
        }
    elif level == 2:
        security = {
            "auth": "Auth0 with RBAC + MFA enforced for admins",
            "encryption": "TLS 1.3 + AES-256 at rest + encrypted backups",
            "secrets": "AWS Secrets Manager or HashiCorp Vault",
            "network": "VPC + WAF (Cloudflare/AWS) + private subnets for DB",
            "scanning": "Snyk (dependencies) + Trivy (containers) + SAST in CI",
            "model": "Defense in depth",
        }
    elif level == 3:
        security = {
            "auth": "Auth0/Okta + SSO + SCIM provisioning + zero-trust access",
            "encryption": "KMS managed keys + field-level encryption for PII",
            "secrets": "HashiCorp Vault with auto-rotation",
            "network": "Zero-trust: mTLS between services, network policies, WAF + DDoS",
            "scanning": "Snyk + Trivy + DAST + penetration testing (quarterly)",
            "model": "Zero Trust Architecture",
        }
    else:
        security = {
            "auth": "Enterprise IAM + adaptive MFA + biometric + FIDO2",
            "encryption": "HSM-backed keys + bring-your-own-key + quantum-ready",
            "secrets": "Vault Enterprise with dynamic secrets + lease management",
            "network": "Microsegmentation + SIEM + automated threat response",
            "scanning": "Continuous red-team + bug bounty + SOC 24/7",
            "model": "Zero Trust + Automated Threat Hunting",
        }
    
    return {
        **security,
        "compliance_mapped": compliance,
        "preview": f"{security['model']} — {security['auth'][:40]}..."
    }


def generate_testing_strategy(context: dict, maturity: dict) -> dict:
    """Recommend testing strategy."""
    level = maturity["current_level"]
    
    if level <= 1:
        testing = {
            "unit": "Jest (JS) or Pytest (Python) — aim for 60% coverage on critical paths",
            "integration": "API tests with Supertest or httpx",
            "e2e": "Playwright for critical user flows (login, checkout)",
            "load": "Not needed yet (add when >10K users)",
            "strategy": "Test pyramid: many unit, few integration, minimal E2E",
        }
    elif level == 2:
        testing = {
            "unit": "80% coverage on business logic, run in CI",
            "integration": "Contract testing for API boundaries",
            "e2e": "Playwright suite for top 10 user journeys, run nightly",
            "load": "k6 basic load tests before major releases",
            "strategy": "Shift-left: tests gate every PR, no merge without green CI",
        }
    else:
        testing = {
            "unit": "90% coverage, mutation testing for critical modules",
            "integration": "Pact contract testing between all services",
            "e2e": "Playwright + visual regression (Chromatic), run per-PR",
            "load": "k6 + Grafana: continuous load testing in staging, chaos testing",
            "strategy": "Quality gates at every stage: PR → staging → canary → production",
        }
    
    return {
        **testing,
        "preview": f"{testing['strategy'][:60]}..."
    }


def generate_disaster_recovery(context: dict, maturity: dict) -> dict:
    """Recommend disaster recovery plan."""
    level = maturity["current_level"]
    uptime = context["technical"].get("uptime_requirement", 99.9)
    
    if level <= 1:
        dr = {
            "backup": "Daily automated DB backups (7-day retention)",
            "rto": "4-8 hours (acceptable for early stage)",
            "rpo": "24 hours (daily backup)",
            "failover": "Manual: restore from backup to new instance",
            "runbook": "Document restore steps, test quarterly",
        }
    elif level == 2:
        dr = {
            "backup": "Hourly DB snapshots + daily full backup (30-day retention)",
            "rto": "1-2 hours",
            "rpo": "1 hour",
            "failover": "Multi-AZ automatic failover for database",
            "runbook": "Automated restore scripts, tested monthly",
        }
    elif level == 3:
        dr = {
            "backup": "Continuous replication + point-in-time recovery",
            "rto": "15-30 minutes",
            "rpo": "5 minutes",
            "failover": "Automated cross-region failover with health checks",
            "runbook": "Chaos engineering (monthly), automated failover testing",
        }
    else:
        dr = {
            "backup": "Real-time replication across regions + immutable backups",
            "rto": "< 5 minutes (near-zero downtime)",
            "rpo": "< 1 minute (near-zero data loss)",
            "failover": "Active-active: automatic traffic rerouting, no manual intervention",
            "runbook": "Weekly chaos engineering, quarterly DR drills, automated everything",
        }
    
    return {
        **dr,
        "preview": f"RTO: {dr['rto']}, RPO: {dr['rpo']}"
    }


def generate_data_architecture(context: dict, maturity: dict) -> dict:
    """Recommend data architecture."""
    level = maturity["current_level"]
    industry = context["organization"]["industry"]
    
    if level <= 1:
        data = {
            "primary_db": "PostgreSQL (single instance)",
            "caching": "Redis or application-level caching",
            "file_storage": "S3 / Cloud Storage",
            "analytics": "PostgreSQL queries + Metabase (free BI)",
            "data_flow": "Application → PostgreSQL → Metabase dashboards",
        }
    elif level == 2:
        data = {
            "primary_db": "PostgreSQL (Multi-AZ) + read replicas",
            "caching": "Redis cluster for sessions + query cache",
            "file_storage": "S3 with lifecycle policies",
            "analytics": "PostgreSQL → ETL (dbt) → Data Warehouse (BigQuery/Redshift)",
            "data_flow": "Application → DB → CDC → Warehouse → BI (Metabase/Looker)",
        }
    else:
        data = {
            "primary_db": "PostgreSQL cluster (write) + read replicas per region",
            "caching": "Redis Cluster + CDN edge caching",
            "file_storage": "S3 cross-region + intelligent tiering",
            "analytics": "Event streaming (Kafka) → Data Lake (S3/Delta) → Warehouse → BI",
            "data_flow": "Services → Kafka → Lake → dbt transforms → Warehouse → Dashboards + ML",
        }
    
    return {
        **data,
        "preview": f"{data['primary_db'][:30]} → {data['analytics'][:30]}..."
    }


def generate_automation(context: dict, maturity: dict) -> dict:
    """Recommend IaC and automation approach."""
    level = maturity["current_level"]
    
    if level <= 1:
        automation = {
            "iac": "Terraform (basic) — define infra as code from day 1",
            "config": "Environment variables + dotenv files",
            "provisioning": "Terraform apply manually (or in CI)",
            "monitoring_alerts": "UptimeRobot (free) + PagerDuty (free tier)",
            "auto_scaling": "Cloud provider auto-scaling (basic rules)",
        }
    elif level == 2:
        automation = {
            "iac": "Terraform with modules + state in S3/GCS",
            "config": "AWS Parameter Store or Doppler",
            "provisioning": "Terraform in CI/CD pipeline (plan on PR, apply on merge)",
            "monitoring_alerts": "Datadog/New Relic with Slack alerts + PagerDuty",
            "auto_scaling": "Target tracking policies (CPU/memory based)",
        }
    else:
        automation = {
            "iac": "Terraform + Terragrunt (multi-env) + policy-as-code (OPA)",
            "config": "HashiCorp Vault + dynamic configuration",
            "provisioning": "Full GitOps: infrastructure changes via PR review + auto-apply",
            "monitoring_alerts": "AI-driven alerting, auto-remediation for known issues",
            "auto_scaling": "Custom metrics + predictive scaling + spot instances",
        }
    
    return {
        **automation,
        "preview": f"{automation['iac'][:50]}..."
    }


def generate_full_e2e(context: dict, maturity: dict) -> dict:
    """Generate complete E2E architecture covering ALL business needs."""
    return {
        "architecture_pattern": generate_architecture_pattern(context, maturity),
        "code_framework": generate_code_framework(context),
        "devops_pipeline": generate_devops_pipeline(context, maturity),
        "infrastructure": generate_infrastructure(context, maturity),
        "ai_ml_stack": generate_ai_ml_stack(context),
        "team_and_process": generate_team_and_process(context, maturity),
        "security_architecture": generate_security_architecture(context, maturity),
        "testing_strategy": generate_testing_strategy(context, maturity),
        "disaster_recovery": generate_disaster_recovery(context, maturity),
        "data_architecture": generate_data_architecture(context, maturity),
        "automation": generate_automation(context, maturity),
        "business_tools": generate_business_tools(context, maturity),
        "analytics_bi": generate_analytics_bi(context, maturity),
        "compliance_governance": generate_compliance_governance(context, maturity),
    }


def generate_compliance_governance(context: dict, maturity: dict) -> dict:
    """Recommend compliance and governance approach."""
    compliance = context["compliance"]["frameworks"]
    level = maturity["current_level"]
    
    if level <= 1:
        result = {
            "frameworks": ", ".join(compliance) if compliance else "SOC2 (recommended for any SaaS)",
            "approach": "Start documenting: access policies, change logs, incident procedures",
            "tools": "Vanta or Drata (automated SOC2) — saves months of manual work",
            "audit_readiness": "Begin SOC2 Type I preparation — takes 3-6 months",
            "governance": "Basic: code reviews required, access reviews quarterly",
            "data_policy": "Define data classification (public, internal, confidential, restricted)",
        }
    elif level == 2:
        result = {
            "frameworks": ", ".join(compliance) if compliance else "SOC2 Type II + GDPR",
            "approach": "Automated compliance monitoring with continuous evidence collection",
            "tools": "Vanta or Drata (automated) + external auditor (annual)",
            "audit_readiness": "SOC2 Type II in progress — continuous monitoring",
            "governance": "Change Advisory Board, access reviews monthly, vendor assessments",
            "data_policy": "Data retention policies, DPA with vendors, privacy impact assessments",
        }
    else:
        result = {
            "frameworks": ", ".join(compliance) if compliance else "SOC2 + ISO27001 + GDPR + industry-specific",
            "approach": "GRC platform with real-time compliance dashboard and automated remediation",
            "tools": "ServiceNow GRC or OneTrust + Vanta + external Big 4 auditor",
            "audit_readiness": "Always audit-ready — continuous compliance with automated evidence",
            "governance": "Architecture Review Board + Security Council + quarterly risk assessments",
            "data_policy": "Full data governance: lineage, classification, retention, cross-border controls",
        }
    
    return {
        **result,
        "preview": f"{result['frameworks'][:30]} — {result['approach'][:30]}..."
    }


def generate_business_tools(context: dict, maturity: dict) -> dict:
    """Recommend business operations tools — ITSM, docs, communication, HR."""
    team = context["organization"]["team_size"]
    budget = context["organization"]["budget_monthly_usd"]
    
    if team <= 10:
        tools = {
            "communication": "Slack Free or Discord (team chat) + Google Meet (calls)",
            "documentation": "Notion (wiki, docs, knowledge base) — free for small teams",
            "itsm_helpdesk": "Not needed yet — use shared Slack channel for support",
            "hr_people": "Deel or Remote (for contractors) + Google Sheets for tracking",
            "crm": "HubSpot Free (contacts, deals, pipeline)",
            "email": "Google Workspace ($6/user/mo) or free Gmail",
            "design": "Figma Free (UI/UX) + Canva (marketing)",
            "legal": "Docusign or PandaDoc for contracts",
        }
    elif team <= 50:
        tools = {
            "communication": "Slack Pro ($7.25/user) + Zoom (meetings) + Loom (async video)",
            "documentation": "Notion Team or Confluence (structured wiki + docs)",
            "itsm_helpdesk": "Jira Service Management or Freshdesk (customer support)",
            "hr_people": "BambooHR or Zoho People (HR management + leave + payroll)",
            "crm": "HubSpot Starter or Salesforce Essentials ($25/user)",
            "email": "Google Workspace Business ($12/user/mo)",
            "design": "Figma Pro ($15/editor) + Canva Pro",
            "legal": "DocuSign Business + legal counsel retainer",
            "service_management": "ServiceNow (if enterprise clients) or Freshservice",
        }
    else:
        tools = {
            "communication": "Slack Enterprise + Zoom Enterprise + Loom Business",
            "documentation": "Confluence + Notion (hybrid) + internal wiki",
            "itsm_helpdesk": "ServiceNow ITSM (enterprise-grade) or Jira Service Management Premium",
            "hr_people": "Workday or SAP SuccessFactors (enterprise HR)",
            "crm": "Salesforce Enterprise ($150/user) + Gainsight (customer success)",
            "email": "Google Workspace Enterprise or Microsoft 365 E3",
            "design": "Figma Enterprise + Adobe Creative Cloud",
            "legal": "Ironclad (contract lifecycle) + in-house counsel",
            "service_management": "ServiceNow + PagerDuty (incident management)",
            "rpa_automation": "UiPath or Automation Anywhere (robotic process automation)",
        }
    
    return {
        **tools,
        "preview": f"{tools['communication'][:30]} + {tools['documentation'][:20]}..."
    }


def generate_analytics_bi(context: dict, maturity: dict) -> dict:
    """Recommend analytics, BI, and data tools."""
    level = maturity["current_level"]
    budget = context["organization"]["budget_monthly_usd"]
    industry = context["organization"]["industry"]
    
    if level <= 1:
        analytics = {
            "product_analytics": "Mixpanel Free or PostHog (open source) — track user behavior",
            "bi_dashboards": "Metabase (open source, self-host) or Google Looker Studio (free)",
            "data_warehouse": "Not needed yet — query production DB directly with read replica",
            "etl_pipeline": "Not needed yet — direct queries sufficient",
            "ab_testing": "PostHog feature flags or Growthbook (open source)",
            "cloud_analytics": "AWS CloudWatch or basic cloud dashboards",
        }
    elif level == 2:
        analytics = {
            "product_analytics": "Mixpanel or Amplitude ($0-1000/mo based on events)",
            "bi_dashboards": "Metabase (OSS) or Looker Studio + dbt for transforms",
            "data_warehouse": "BigQuery (GCP) or Redshift (AWS) — pay-per-query",
            "etl_pipeline": "dbt (transform) + Airbyte (ingestion, open source)",
            "ab_testing": "GrowthBook (OSS) or LaunchDarkly (feature flags)",
            "cloud_analytics": "AWS Athena (query S3 data directly) + QuickSight",
        }
    else:
        analytics = {
            "product_analytics": "Amplitude Enterprise or Heap (auto-capture everything)",
            "bi_dashboards": "Looker (GCP) or Tableau + dbt Cloud for modeling",
            "data_warehouse": "Snowflake or BigQuery (scalable, separated compute/storage)",
            "etl_pipeline": "dbt Cloud + Fivetran/Airbyte (managed ingestion) + Dagster (orchestration)",
            "ab_testing": "Eppo or Statsig (statistical rigor) + feature management",
            "cloud_analytics": "AWS Athena + Lake Formation + Redshift Spectrum",
            "ml_analytics": "Vertex AI or SageMaker for predictive analytics",
        }
    
    return {
        **analytics,
        "preview": f"{analytics['product_analytics'][:30]} + {analytics['data_warehouse'][:25] if 'data_warehouse' in analytics else ''}..."
    }


def generate_project_management(context: dict, maturity: dict) -> dict:
    """Recommend project management, agile process, and delivery tools."""
    team = context["organization"]["team_size"]
    
    if team <= 10:
        pm = {
            "methodology": "Kanban (continuous flow) — no heavy sprints for small teams",
            "tool": "Linear (modern, fast) or Jira Free (up to 10 users)",
            "sprint_structure": "Not needed — use weekly goals instead of sprints",
            "roadmap": "Notion roadmap or Linear roadmap view",
            "documentation": "Notion (all-in-one: docs + wiki + tasks)",
            "retrospectives": "Bi-weekly team retro (15 min) — use FigJam or Notion",
            "standup": "Daily async standup (Slack bot or Geekbot)",
            "release_process": "Ship when ready — no release train needed yet",
        }
    elif team <= 30:
        pm = {
            "methodology": "Scrum — 2-week sprints, dedicated Scrum Master",
            "tool": "Linear (recommended) or Jira Standard",
            "sprint_structure": "2-week sprints: Planning (Mon) → Daily standup → Review (Fri) → Retro",
            "roadmap": "Linear roadmap + quarterly OKRs (Notion or Lattice)",
            "documentation": "Notion (team wiki) + ADRs in repo + Confluence for formal docs",
            "retrospectives": "Every sprint — action items tracked and followed up",
            "standup": "Daily sync standup (15 min) per squad",
            "release_process": "Weekly releases (Tuesdays) with changelog",
        }
    else:
        pm = {
            "methodology": "SAFe (Scaled Agile) or custom hybrid — PI planning quarterly",
            "tool": "Jira Premium + Confluence + Jira Align (cross-team)",
            "sprint_structure": "2-week sprints within 10-week Program Increments (PIs)",
            "roadmap": "Jira Align (portfolio) + quarterly PI planning events",
            "documentation": "Confluence (enterprise wiki) + Notion (team-level) + ADRs",
            "retrospectives": "Sprint retros + PI retrospective + innovation sprints",
            "standup": "Squad standups (daily) + Scrum of Scrums (weekly) + ART sync",
            "release_process": "Release train (bi-weekly) with feature flags + progressive rollout",
        }
    
    return {
        **pm,
        "preview": f"{pm['methodology'][:40]} — {pm['tool'][:20]}..."
    }


# Section display names for UI
E2E_SECTIONS = {
    "architecture_pattern": {"title": "Architecture Pattern", "icon": "🏛️"},
    "code_framework": {"title": "Code & Frameworks", "icon": "💻"},
    "devops_pipeline": {"title": "DevOps Pipeline", "icon": "🔄"},
    "infrastructure": {"title": "Infrastructure Design", "icon": "☁️"},
    "ai_ml_stack": {"title": "AI/ML Stack", "icon": "🤖"},
    "team_and_process": {"title": "Team & Delivery Process", "icon": "👥"},
    "security_architecture": {"title": "Security Architecture", "icon": "🔒"},
    "testing_strategy": {"title": "Testing Strategy", "icon": "🧪"},
    "disaster_recovery": {"title": "Disaster Recovery", "icon": "🛡️"},
    "data_architecture": {"title": "Data Architecture", "icon": "🗄️"},
    "automation": {"title": "Automation & IaC", "icon": "⚙️"},
    "business_tools": {"title": "Business Operations Tools", "icon": "🏢"},
    "analytics_bi": {"title": "Analytics & BI Stack", "icon": "📈"},
    "compliance_governance": {"title": "Compliance & Governance", "icon": "📜"},
}
