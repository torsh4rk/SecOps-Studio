# TORSh4rk Threat Intelligence MCP

**An independent, read-only Model Context Protocol (MCP) server for AI-assisted security investigations.**

[![Defensive security](https://img.shields.io/badge/Scope-Read--only%20Threat%20Intelligence-247A4A)](#security-model) [![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](#quick-start) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Status:** v0.1.0 • Research MVP • Not independently security audited. No claim of production readiness.
>
> **Design philosophy:** evidence before attribution, predictable tools before autonomous actions, and human approval before containment.

## Why this exists

Security analysts often need to relate domains, IPs, hashes, and CVEs across different intelligence providers. This MCP presents a narrowly scoped interface for *authorized defensive triage*: public IOC metadata, evidence correlation, and documented responder checklists. It deliberately does **not** retrieve stolen credentials, enumerate hidden services, download malware, run shell commands, scan arbitrary infrastructure, or change any security control.

Inspired by the threat-intelligence aggregation concept of [`1SHA1024/darknet-mcp-server`](https://github.com/1SHA1024/darknet-mcp-server), itself linked to [`badchars/darknet-mcp-server`](https://github.com/badchars/darknet-mcp-server). This is an **independent implementation**, not a fork and not a claim of 66 tools or 16 active providers. See [ATTRIBUTION.md](ATTRIBUTION.md).

## Available tools (10)

| Tool | Function | Internet | Credentials |
| --- | --- | --- | --- |
| `triage_indicator` | Validate and classify public IP, domain, URL, hash, CVE | No | None |
| `lookup_otx` | AlienVault OTX public indicator context | Yes | None configured (provider limits apply) |
| `lookup_threatfox` | ThreatFox IOC lookups | Yes | `ABUSECH_AUTH_KEY` |
| `lookup_malwarebazaar` | MalwareBazaar **metadata only** by hash | Yes | `ABUSECH_AUTH_KEY` |
| `lookup_urlhaus_host` | URLhaus malware-host metadata | Yes | `ABUSECH_AUTH_KEY` |
| `lookup_cisa_kev` | Official CISA Known Exploited Vulnerabilities catalog | Yes | None |
| `lookup_abuseipdb` | AbuseIPDB public IPv4 abuse reputation | Yes | `ABUSEIPDB_API_KEY` |
| `correlate_evidence` | Group analyst-supplied observations and flag contradictions | No | None |
| `defensive_playbook` | Return SOC response checklist templates | No | None |
| `server_status` | Version and configured integrations (never key values) | No | None |

**Source limitations:** API policies, availability, rate limits, and dataset recency are controlled by their operators. Some abuse.ch API use may be restricted by fair-use/commercial terms. Missing API keys result in explicit errors. Searches are *not* executed or validated live by the test suite.

## Architecture

```text
AI client (Claude Code / Claude Desktop / MCP-compatible agent)
                   | stdio, JSON-RPC / MCP
                   v
        +-----------------------------+
        | server.py (Python stdlib)   |
        | - argument validation       |
        | - tool allowlist            |
        | - fixed HTTPS destinations  |
        | - timeouts / size ceilings  |
        | - minimal structured data   |
        +-----------------------------+
            |                   |
      local correlation    optional outbound lookups
            |                   |
       SOC review           OTX / abuse.ch / CISA / AbuseIPDB
                                |
                          UNTRUSTED EVIDENCE
```

**Trust boundary:** external intelligence is untrusted information, not instructions. Correlation results are leads, not validated attribution. An IOC match by itself is not proof of compromise.

## Quick start

Requires Python **3.11+**. The server runs with the Python standard library; no `pip install` is needed.

```bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/torsh4rk-threat-intel-mcp
python3 server.py
```

The process communicates exclusively through `stdin`/`stdout` in the MCP stdio transport. **No startup banner appears on stdout**; your MCP client starts it automatically. Supported protocol versions: `2024-11-05`, `2025-03-26`, and `2025-06-18`.

### Claude Code

From the repo root, register a local stdio MCP server:

```bash
claude mcp add torsh4rk-threat-intel -- python3 /absolute/path/to/SecOps-Studio/torsh4rk-threat-intel-mcp/server.py
```

Use an absolute path and add optional credentials via your MCP client's secure environment-variable configuration. Never commit live keys to GitHub.

### Claude Desktop / compatible MCP clients

```json
{
  "mcpServers": {
    "torsh4rk-threat-intel": {
      "command": "python3",
      "args": ["/absolute/path/to/SecOps-Studio/torsh4rk-threat-intel-mcp/server.py"],
      "env": {
        "ABUSECH_AUTH_KEY": "REPLACE_WITH_LOCAL_VALUE",
        "ABUSEIPDB_API_KEY": "REPLACE_WITH_LOCAL_VALUE"
      }
    }
  }
}
```

Remove entries for keys you do not use. These values are placeholders, not real credentials. In production, use your client's secret manager/environment injection rather than storing API keys in shared configuration files.

### Example analyst workflow

1. Call `triage_indicator` with `example.org` (reserved demonstration domain).
2. Call an approved remote lookup for an authorized public IOC; inspect provider status and timestamps.
3. Feed **analyst-verified** observations to `correlate_evidence`, e.g.:

```json
{
  "evidence": [
    {"indicator": "example.org", "source": "SOC case 1482", "assessment": "suspicious"},
    {"indicator": "example.org", "source": "Independent lab", "assessment": "unknown"}
  ]
}
```

4. Use `defensive_playbook` for `phishing`, `ransomware`, `malware`, or `credential_exposure`; obtain approval through existing incident-response workflows.

### Run tests without API keys

```bash
python3 -m unittest discover -s tests -v
```

Tests cover indicator validation, private-address protections, key gating, response filtering, conflict-aware correlation, and MCP JSON-RPC dispatch. They mock outbound calls; **live provider interoperability is not part of the automated tests**.

## Security model

- Read-only tool registry: no arbitrary HTTP fetch, execution, Tor access, malware downloads, credential harvesting, submission to feeds, or configuration changes.
- Outbound lookup URLs are built exclusively for known providers, not chosen by an AI agent. Private/non-global IP indicators are rejected before external calls.
- HTTP redirect following is disabled, responses are capped at 2 MB, and outbound timeouts are 10 seconds.
- Sensitive API credentials come only from environment variables and are never included in results.
- Provider results are restricted to selected metadata fields; no unbounded raw content is passed to the model.
- No database or telemetry storage. Provider requests may still disclose the **queried indicator** and API account metadata to that provider; follow your organization's data-sharing policy.
- A per-process rate limiter and robust enterprise audit logging are **not** implemented in this MVP. Restrict client permissions, monitor provider quota, and deploy only in trusted analyst environments.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) and [SECURITY.md](SECURITY.md).

## Roadmap

- Proper rate limiting and optional allowlisted scopes for enterprise deployments.
- Caching with bounded TTL and provider-specific quotas.
- JSON schema-based contract tests against sanitized provider fixtures.
- OpenTelemetry auditing with privacy-preserving defaults.
- Optional Tor research in a separately sandboxed, opt-in process, *only* after a threat model and legal review.

## License & attribution

MIT © 2026 torsh4rk. Original project acknowledgment in [ATTRIBUTION.md](ATTRIBUTION.md). Contributions and security issues are welcome under [SECURITY.md](SECURITY.md).
