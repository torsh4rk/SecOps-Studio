# Agro AI Guardian

### Explainable, read-only AI-agent security monitoring for connected agriculture

[![CI](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/agro-ai-guardian-tests.yml/badge.svg)](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/agro-ai-guardian-tests.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/Version-0.1.0-6B7280)
![Status](https://img.shields.io/badge/Status-Read--only%20MVP-256D4A)

**Agro AI Guardian** is a defensive, dependency-light research prototype for assessing AI-agent activity and structured event telemetry in agricultural technology environments. It detects selected policy violations and suspicious signals involving AI agents, APIs, IoT sensors, and *attempted* OT-sensitive tool use.

**Design contract:** **observe → validate → classify → explain → alert for human review**. It does not operate field equipment, execute remediation, scan targets, or enforce access decisions on external systems.

> **Maturity:** proof of concept, suitable for controlled demonstrations and technical review. Not a production-grade SOC, intrusion-prevention system, industrial safety controller, or complete AI-agent firewall.

## 1. Problem statement and business relevance

Connected farming may combine environmental feeds, telemetry, scheduling services, devices, and automated software agents. A manipulated tool result or unauthorized agent may lead to unwanted data access or unsafe attempts to control downstream systems.

This prototype investigates a **defense-in-depth monitoring layer**, aimed at making suspicious events observable and interpretable. It is designed around explicit safety boundaries because any software touching physical equipment requires more than a demonstration rule engine.

**Representative scenarios:** a sensor-observer agent attempts an export, a field-data feed contains prompt-injection language, an unknown agent requests a valve operation, or a moisture reading falls outside the defined illustrative range. All scenarios in this repository are simulated.

## 2. Implemented capabilities

| Signal | Rule identifier | Behavior | Typical outcome |
|---|---|---|---|
| Agent outside configured list | `unknown_agent` | Checks `agent_id` against policy | `deny` / high |
| Disallowed tool invocation | `tool_not_allowed` | Compares tool name to agent-specific allowlist | `deny` / high |
| Unspecified tool | `missing_tool` | Flags tool-call events lacking `tool` | `deny` / high |
| Attempted OT actuation | `ot_actuation` | Recognizes named prefixes such as `valve.`, `pump.`, `drone.`, `plc.` | `deny` / critical |
| Prompt-injection patterns | `prompt_injection_indicator` | English/Portuguese regular-expression indicators | `review` / high |
| Unrecognized content source | `untrusted_input_source` | Checks source label against trusted-source literals | `review` / medium |
| Export to unapproved host | `exfiltration_destination` | Validates URL host for named export tools | `deny` / critical |
| Activity burst | `agent_activity_spike` | Counts API/authentication events per agent in a rolling 60s window | `review` / high |
| Sensor anomaly | `sensor_anomaly` | Checks example `soil_moisture` value against 0–100 | `review` / medium |

**What these checks are not:** actual authentication, hardware interlocks, DNS/firewall egress restrictions, a semantic prompt-injection classifier, behavioral anomaly ML, or a verified industrial control safety system.

### Advisory decisions

- `allow` — no configured rule raised a finding for this event.
- `review` — suspicious or low-confidence signal requiring analyst inspection.
- `deny` — policy indicates that the action should not proceed; **the prototype does not enforce it**.

Severity is the maximum severity among findings (`info`, `medium`, `high`, `critical`). The engine preserves rule IDs and concise explanations and intentionally does not echo arbitrary raw prompt contents into alerts.

## 3. Architecture and trust boundaries

```text
     [External sources: feed / API / agent logs / sensors]
                            |
                            v
     [Trusted gateway: authentication, integrity, transport]
                    OUTSIDE THIS MVP
                            |
                            v
                    Input JSONL stream
                            |
                  validate event fields
                            |
                            v
     +-----------------------------------------------+
     |           Guardian rule engine                |
     | approved_agents | tool rules | URL host check |
     | prompt patterns | event burst | sensor bounds |
     +-----------------------------------------------+
                            |
                            v
              Structured decision + findings
                   /                   \
                  v                     v
       JSONL / stdout/file     Optional local Ollama
                                sanitized rule summary
                  \                     /
                   v                   v
                 Human SOC / security review
                    (external process)

     PLC / valves / pumps / drones / SCADA: NOT CONNECTED
```

**Implemented components:**

- `agro_guardian/core.py` — policy validation, event validation, classification, bounded in-process event history.
- `agro_guardian/__main__.py` — local JSONL stream/file CLI and structured output.
- `agro_guardian/llm.py` — optional localhost Ollama explanation, without decision authority.
- `config/policy.example.json` — example identities, tools, destination hosts, and rate threshold.
- `examples/events.jsonl` — synthetic positive and suspicious examples.
- `tests/test_guardian.py` — 14 deterministic unit/integration-style cases.
- `docs/THREAT_MODEL.md` — threat boundaries, assumptions, and missing production controls.

**Trust model:** the input stream itself is untrusted. A caller-supplied `agent_id` is not authenticated. Content and local LLM outputs must always be treated as data, not higher-priority instructions. A separate authorized enforcement point would be required to put policy decisions into effect.

## 4. Requirements and installation

- Python **3.11 or later**.
- Git, for cloning.
- No external Python dependencies for normal inspection.
- Optional: a local Ollama installation and downloaded model if summary generation is desired.

From the repository root:

```bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/agro-ai-guardian

python3 --version
python3 -m agro_guardian --input examples/events.jsonl
```

To write structured results to a file:

```bash
python3 -m agro_guardian \
  --policy config/policy.example.json \
  --input examples/events.jsonl \
  --output alerts.jsonl
```

Read events from stdin:

```bash
cat examples/events.jsonl | python3 -m agro_guardian --input -
```

Output is one JSON object per input line. The sample data is synthetic and includes no real agricultural telemetry or credentials.

## 5. JSONL event contract

Each nonempty input line must be one JSON object with:

| Field | Requirement | Notes |
|---|---|---|
| `timestamp` | Required | ISO 8601 with timezone offset, e.g. `2026-11-12T05:00:00Z` |
| `agent_id` | Required | Agent label only, **not** identity proof |
| `event_type` | Required | One of `tool_call`, `text_input`, `api_request`, `sensor_reading`, `auth_event` |
| `event_id` | Optional | Hash-based identifier generated if absent |
| `tool` | Per event | Name used for agent tool policy checks |
| `destination` | Per event | URL used for certain export-tool checks |
| `source` / `content` | Per event | Input origin and suspicious text indicators |
| `asset` / `value` | Per event | Illustrative sensor ID/type and reading |

**Example input:**

```json
{"event_id":"attack-001","timestamp":"2026-11-12T05:00:01Z","agent_id":"unknown-bot","event_type":"tool_call","tool":"valve.open","asset":"valve-01"}
```

**Example output (derived from the current policy and rules):**

```json
{
  "event_id": "attack-001",
  "agent_id": "unknown-bot",
  "event_type": "tool_call",
  "decision": "deny",
  "severity": "critical",
  "findings": [
    {"rule": "unknown_agent", "severity": "high", "message": "Identidade do agente não autorizada."},
    {"rule": "tool_not_allowed", "severity": "high", "message": "Ferramenta fora da lista autorizada para o agente."},
    {"rule": "ot_actuation", "severity": "critical", "message": "Ação física/OT solicitada: aprovação externa obrigatória; este monitor nunca executa comandos."}
  ],
  "explanation": "Identidade do agente não autorizada. ; Ferramenta fora da lista autorizada para o agente. ; Ação física/OT solicitada: aprovação externa obrigatória; este monitor nunca executa comandos."
}
```

The output reports a policy recommendation **only**. No valve operation is attempted or intercepted.

## 6. Configure the example policy

```json
{
  "approved_agents": {
    "farm-observer": ["read_sensor", "query_logs"],
    "security-sentinel": ["query_logs", "read_sensor"],
    "irrigation-planner": ["read_sensor", "query_logs", "propose_schedule"]
  },
  "allowed_destination_hosts": ["telemetry.example.org"],
  "rate_limit_per_minute": 5
}
```

This configuration is illustrative, **not** a production authorization model.

- Agent and tool lists are exact-name matches.
- Export destinations are compared by normalized host **text**; this is not DNS, TLS, routing, or firewall enforcement.
- Activity checks depend on events arriving in chronological order and stay in process memory.
- The approved text sources are currently hard-coded in the prototype (`audit-gateway`, `field-gateway`, `security-siem`).
- The sensor rule demonstrates only one metric (`soil_moisture`); it cannot verify physical sensor authenticity.

## 7. Optional local LLM: explanation, never enforcement

Ollama is **not required** for detection. If installed and running on `127.0.0.1:11434`:

```bash
# Prepare a local model separately using Ollama, then:
python3 -m agro_guardian \
  --input examples/events.jsonl \
  --local-llm llama3.2
```

The LLM receives sanitized **rule descriptions and decision metadata**, not arbitrary event prompt text. Its output is appended as `local_llm_summary`. If the local model fails, the policy result remains unchanged and a generic `local_llm_error` is recorded.

**This is not a RAG implementation, a trained detection model, or autonomous incident response.** It is deterministic inspection plus an optional natural-language summarization step.

## 8. Testing and reproducibility

```bash
python3 -m unittest discover -s tests -v
```

The repository includes **14 test cases** covering benign tool use, unknown agents, disallowed actions, OT-sensitive requests, English/Portuguese injection indicators, text-source trust, export-host edge cases, rate thresholds, invalid sensor readings, timestamp validation, suppression of raw secret echoes, and CLI output.

The GitHub Actions [workflow](../.github/workflows/agro-ai-guardian-tests.yml) runs Python 3.12 unit tests and the example detection command. See the [latest workflow results](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/agro-ai-guardian-tests.yml). Passing tests demonstrate these specified cases only; no production accuracy, resilience, or OT safety assurance has been measured.

## 9. Security boundaries and current limitations

| Area | Current limitation | What production would require |
|---|---|---|
| Identity | `agent_id` is unverified input | Authenticated producer identities, mTLS, gateway controls |
| Prompt injection | Simple regular-expression coverage | Broader adversarial datasets, layered controls, continuous validation |
| API abuse | Single-process event counters | Distributed rate limiting, synchronized timestamps, persistent event correlation |
| Egress | URL host-text check only | Network policy, DNS/TLS controls, proxy logs and enforceable egress |
| OT actions | Flags suspicious tool names; does not enforce | Network segmentation, safety interlocks, independent approval pathways |
| Sensor telemetry | Example range check only | Device authenticity, calibrated bounds, provenance and domain expertise |
| Alerting | Local JSONL/stdout/file | SIEM/SOAR integration, retention, role-based access, operational playbooks |
| LLM | Optional local summaries; no decision rights | Evaluated model deployment, output handling, privacy controls |
| Model / data security | No training, retrieval, or inference perimeter | Appropriate controls if later used with cloud or RAG workloads |

**Do not deploy this prototype as the sole safeguard for equipment, farm operations, employee safety, or regulated data.** Restrict testing to your own or expressly authorized systems and nonproduction data.

## 10. Forward-looking engineering roadmap

The following items are **proposals, not existing functionality**:

1. Authenticated telemetry gateway and signed, normalized event ingestion.
2. Configurable security policies and safer approvals for external enforcement integrations.
3. SIEM-compatible alert forwarding and alert lifecycle handling.
4. Expanded adversarial evaluation (including multilingual and tool-output prompt injection).
5. Isolated agriculture/OT simulation lab and failure-mode tests.
6. Performance, reliability, usability, and false-positive/false-negative benchmarking.

## 11. References and responsible development

- [Threat model for this repository](docs/THREAT_MODEL.md)
- [NIST SP 800-82 Rev. 3 — Guide to Operational Technology (OT) Security](https://csrc.nist.gov/pubs/sp/800/82/r3/final)
- [MITRE ATLAS — Adversarial Threat Landscape for Artificial-Intelligence Systems](https://atlas.mitre.org/)
- [OWASP — Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)

This is an independent, AI-assisted research demonstration. No customer implementation, certification, vendor approval, or operational deployment is claimed. Review the source and validate security assumptions before building on it.

**Repository owner:** [torsh4rk](https://github.com/torsh4rk)  
**License for this subproject:** [MIT](LICENSE)  
**Language:** documentation in English; current rule explanations include Portuguese.
