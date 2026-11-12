# SecOps Studio

### Security engineering research · AI-agent defense · Connected agriculture

[![Agro AI Guardian CI](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/agro-ai-guardian-tests.yml/badge.svg)](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/agro-ai-guardian-tests.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Scope](https://img.shields.io/badge/Scope-Defensive%20Security-256D4A)
![Maturity](https://img.shields.io/badge/Maturity-Research%20MVP-6B7280)

**SecOps Studio** is an independent security engineering workspace. Its featured project, **[Agro AI Guardian](agro-ai-guardian/)**, explores how deterministic guardrails and optional local language-model assistance can help security teams review suspicious AI-agent activity in connected agricultural environments.

> **In one sentence:** a reproducible, read-only proof of concept that turns AI-agent and agricultural telemetry into structured, explainable security findings—without issuing commands to field equipment.

**Project status:** Agro AI Guardian v0.1 · Research / proof of concept · **Not production-ready** · **No live OT integration**

---

## Threat Intelligence MCP — independent module

**[TORSh4rk Threat Intelligence MCP](torsh4rk-threat-intel-mcp/)** is a read-only research MCP server with 10 analyst tools for IOC triage, enrichment through approved providers, deterministic evidence correlation, and SOC response checklists. It uses Python 3.11+ with no runtime dependencies.

- [Project README and installation](torsh4rk-threat-intel-mcp/README.md)
- [Threat model](torsh4rk-threat-intel-mcp/docs/THREAT_MODEL.md)
- [Offline unit tests](torsh4rk-threat-intel-mcp/tests/test_server.py)

**Status:** Research MVP; not production-ready. No stolen credential access, malware downloading, Tor browsing, or automated containment.

---

## Executive overview

Agricultural operations increasingly depend on APIs, remote telemetry, sensor platforms, and software-controlled workflows. AI agents introduce an additional trust boundary when they read untrusted data, choose tools, or interact with services that may ultimately influence physical processes.

Agro AI Guardian addresses a limited, practical part of this problem: **analyzing captured events for policy violations and suspicious patterns before a security team designs enforcement controls.**

| Security concern | What the current MVP evaluates | Example |
|---|---|---|
| Agent authorization | Agent IDs against a configured allowlist | Unrecognized automation identity |
| Tool-use governance | Per-agent permitted tool names | An observer invoking an export tool |
| Prompt injection indicators | Selected English/Portuguese text patterns and source labels | Untrusted content attempting to override instructions |
| Data egress indicators | Exact host allowlist checks for named export tools | Export to an unapproved endpoint |
| OT-sensitive operations | Known prefixes associated with agricultural equipment | A request resembling `valve.open` |
| API and authentication bursts | In-memory event counts within a 60-second window | Unexpected burst of agent activity |
| Telemetry sanity checks | Example soil-moisture range validation | Out-of-range moisture value |
| Analyst assistance | Optional Ollama summary of sanitized findings | Human-readable SOC triage note |

**Important:** the program produces *recommendations*, not enforcement. A `deny` finding does **not** block traffic, revoke permissions, or stop a machine.

## Featured project: Agro AI Guardian

| Area | Details |
|---|---|
| Core language | Python 3.11+ |
| Core runtime dependencies | Python standard library only |
| Input | Local file / stdin, JSON Lines (JSONL) |
| Output | Structured JSONL decisions and findings |
| Policy | JSON-configured agent and tool allowlists, destination hosts, event-rate threshold |
| AI integration | Optional local Ollama, for explanation only |
| Operational stance | Read-only; no scanner, shell executor, network firewall, or OT actuator |
| Verification | 14 unit tests, example telemetry, GitHub Actions test workflow |

**Explore:** [Source and technical README](agro-ai-guardian/README.md) · [Threat model](agro-ai-guardian/docs/THREAT_MODEL.md) · [Policy example](agro-ai-guardian/config/policy.example.json) · [Test suite](agro-ai-guardian/tests/test_guardian.py) · [CI workflow](.github/workflows/agro-ai-guardian-tests.yml)

### Conceptual data flow

```text
  External telemetry / logs (untrusted)
                  |
                  v
      Authenticated collection layer
        [NOT included in this MVP]
                  |
                  v
        JSONL event stream
                  |
                  v
      +-----------------------+
      |   Agro AI Guardian    |
      |   - schema checks     |
      |   - policy rules      |
      |   - anomaly signals   |
      +-----------------------+
                  |
                  +----> Structured findings / decisions
                  |              |
                  |              v
                  |        Human SOC review
                  |
                  +----> Optional local Ollama
                         [sanitized summaries only]

    Agricultural equipment / PLCs / SCADA
         [NO CONTROL CONNECTION]
```

The detection engine remains authoritative for its own classifications. Model-generated summaries cannot rewrite the decision or run tools.

## Quick start: reproduce the demonstration

**Requirements:** Python 3.11+ and Git. The default demo needs **no API keys**, cloud account, model download, or production device.

```bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/agro-ai-guardian

# Evaluate representative simulated events
python3 -m agro_guardian --input examples/events.jsonl

# Execute all included unit tests
python3 -m unittest discover -s tests -v

# Save findings for further review
python3 -m agro_guardian \
  --policy config/policy.example.json \
  --input examples/events.jsonl \
  --output alerts.jsonl
```

The sample covers a legitimate sensor read and simulated suspicious activity. Results are classified as `allow`, `review`, or `deny` and include severity and rule identifiers. **These are advisory labels**, not automatic defensive actions.

For the complete event schema, security considerations, optional Ollama setup, and concrete examples, continue to **[Agro AI Guardian →](agro-ai-guardian/README.md)**.

## Repository structure

```text
SecOps-Studio/
├── agro-ai-guardian/       # Featured, independent defensive Python MVP
│   ├── agro_guardian/      # Rule engine, CLI and optional local LLM
│   ├── config/             # Illustrative policy
│   ├── docs/               # Threat model
│   ├── examples/           # Synthetic JSONL telemetry
│   └── tests/              # Automated unit tests
├── .github/workflows/      # Agro AI Guardian CI workflow
├── frontend/               # Separate pre-existing SecOps Studio web prototype
├── backend/                # Separate pre-existing web prototype backend
├── tests/                  # Existing web prototype tests
└── test_reports/           # Existing prototype test artifacts
```

**Scope boundary:** the pre-existing web application and backend are separate experimental components. They are **not** an integrated dashboard or deployment platform for Agro AI Guardian. The agricultural defense prototype runs independently from `agro-ai-guardian/`.

## Engineering principles

1. **Defense only.** Passive event analysis; no penetration-testing execution, persistence, or autonomous remediation.
2. **Bounded authority.** Local AI is optional and limited to explaining findings; decisions come from inspectable rules.
3. **Operational safety.** No actuation path to irrigation, valves, tractors, drones, PLCs, or SCADA.
4. **Explicit trust boundaries.** Event identity and provenance require external authentication; JSON fields alone are not proof.
5. **Reproducibility.** Minimal runtime dependencies, simulated telemetry, automated tests, and documented assumptions.
6. **Honest maturity labels.** A demonstration is not a production control, certified product, or proven mitigation against all agentic attacks.

### Deployment requirements not supplied by this prototype

For real-world use, security and operational teams would need authenticated ingestion, transport integrity, centralized log storage, access controls, network egress enforcement, SIEM/SOC integration, device segmentation, OT change management, comprehensive detection evaluation, and human-approved incident response procedures. These are **future integration requirements**, not existing capabilities.

## Roadmap (proposed; not implemented)

- Structured and authenticated intake from a dedicated telemetry gateway.
- Better normalization, threat intelligence enrichment, and coverage measurements with benign/adversarial datasets.
- Signed audit trails, distributed rate analysis, alert routing, and SIEM integration.
- Formal policy evaluation, approval workflows, and isolated IT/OT laboratory validation.
- Expanded multilingual prompt-injection tests and model-output safety evaluations.

No production performance, detection accuracy, or field deployment claims are made at this stage.

## Responsible use and provenance

Use only telemetry from systems you own or are expressly authorized to monitor. Do not connect this demo directly to safety-critical infrastructure. Security classifications can be wrong; independent engineering review and testing are required.

This is an **independent portfolio and research project**, not a claim of a customer engagement, vendor endorsement, or an existing deployment. Its development has involved AI assistance; the code, tests, design trade-offs, and limitations are included to support transparent technical evaluation.

**Author / repository owner:** [torsh4rk](https://github.com/torsh4rk)

**License:** [MIT license for the Agro AI Guardian subproject](agro-ai-guardian/LICENSE). Do not assume the same license applies automatically to unrelated components in this repository.

---

<sub>Português: o Agro AI Guardian é uma prova de conceito de segurança defensiva para monitorar eventos de agentes de IA e telemetria agrícola. Ele detecta indícios de abuso e gera alertas para análise humana; não controla máquinas nem bloqueia ataques automaticamente. Veja a <a href="agro-ai-guardian/README.md">documentação técnica</a>.</sub>
