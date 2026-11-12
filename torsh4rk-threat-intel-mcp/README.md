# TORSh4rk Threat Intelligence MCP

**Read-only threat intelligence for AI-assisted security investigations, evidence correlation, and SOC triage.**

[![CI](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml/badge.svg)](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![MCP](https://img.shields.io/badge/Protocol-MCP-6750A4)
![MIT](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Maturity-Research%20MVP-6B7280)

**Documentation languages:** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

> **v0.1.0 — Research MVP, not production-ready or independently audited.** Findings are investigative leads, **not verified attribution**. All operations are read-only; human authorization is required for any real-world response action.

## Purpose

Security teams routinely encounter disconnected indicators: an IP address, suspicious domain, malware file hash, CVE, or conflicting reports from different sources. **TORSh4rk Threat Intelligence MCP** connects a trusted local AI client (such as Claude Code) to a focused set of investigation tools over the **Model Context Protocol (MCP)**.

This independent Python implementation was inspired by the *threat-intelligence aggregation concept* of [1SHA1024/darknet-mcp-server](https://github.com/1SHA1024/darknet-mcp-server). It is **not a fork**, does **not** claim parity with the reference project's tool count, and does **not** provide Tor browsing or access to leaked credentials. See [ATTRIBUTION.md](ATTRIBUTION.md).

## What is implemented?

| MCP tool | Analyst capability | Requires network / key? |
| --- | --- | --- |
| `triage_indicator` | Classify and validate public IPs, domains, HTTP(S) URLs, MD5/SHA-1/SHA-256 hashes, and CVEs | Offline / no key |
| `lookup_otx` | Retrieve selected AlienVault OTX indicator and pulse metadata | Online / no configured key |
| `lookup_threatfox` | Retrieve ThreatFox IOC metadata | Online / `ABUSECH_AUTH_KEY` |
| `lookup_malwarebazaar` | Lookup MalwareBazaar **sample metadata only**, by file hash | Online / `ABUSECH_AUTH_KEY` |
| `lookup_urlhaus_host` | Lookup URLhaus host metadata | Online / `ABUSECH_AUTH_KEY` |
| `lookup_cisa_kev` | Check whether a CVE appears in the official CISA KEV catalog | Online / no key |
| `lookup_abuseipdb` | Retrieve AbuseIPDB public IPv4 reputation | Online / `ABUSEIPDB_API_KEY` |
| `correlate_evidence` | Group up to 50 analyst-provided observations; identify contradictory assessments | Offline / no key |
| `defensive_playbook` | Provide SOC checklists for phishing, ransomware, malware, credential exposure | Offline / no key |
| `server_status` | Display version and integration configuration status **without revealing keys** | Offline / no key |

External integrations depend on upstream providers' availability, terms, quotas, and evolving APIs. **Automated tests mock HTTP responses; they do not prove live provider interoperability.**

## Architecture and trust boundaries

~~~text
Claude Code (trusted local MCP client)
       |
       | MCP JSON-RPC over stdin / stdout (stdio)
       v
server.py — Python 3.11+ standard library only
       |                         |
       | Local operations        | Approved outbound HTTPS requests
       | - indicator validation  | - AlienVault OTX
       | - evidence grouping     | - abuse.ch (ThreatFox / MalwareBazaar / URLhaus)
       | - SOC playbooks         | - CISA KEV / AbuseIPDB
       v                         v
     Structured, bounded findings (external content is untrusted)
                         |
                         v
                 Human analyst review
~~~

The MCP server is **not a publicly hosted service**. It runs on the analyst's machine, launched by the MCP client. It cannot execute shell commands, download malware, harvest credentials, browse Tor, or change security controls.

## Installation — the four commands explained

### Prerequisites

- **Linux, macOS, or another system supporting Python and the Claude Code CLI.** Commands below use a POSIX-style shell (Bash/Zsh); they are suited to Manjaro, Ubuntu, and Kali.
- **Git** to download the repository.
- **Python 3.11 or newer** to execute the server and its test suite. No pip packages or virtual environment are needed for this MVP.
- **Claude Code CLI**, installed and authenticated, to register the local MCP server. This is different from using only the Claude web chat.

Check before proceeding:

~~~bash
git --version
python3 --version
claude --version
~~~

If `claude` is missing, follow the [official Claude Code setup guide](https://code.claude.com/docs/en/setup). If Python is older than 3.11, update it before continuing.

### Full command sequence

Run the following in a terminal **from the parent directory where you want the project cloned**:

~~~bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/torsh4rk-threat-intel-mcp

python3 -m unittest discover -s tests -v

claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

#### 1. `git clone https://github.com/torsh4rk/SecOps-Studio.git`

- **`git`** invokes the Git version-control client.
- **`clone`** downloads a local working copy of a remote repository, including its tracked files and Git history.
- **The HTTPS URL** identifies the public `torsh4rk/SecOps-Studio` repository. The threat-intelligence project is a subdirectory of that repository, not a separate Git repository.
- **Result:** a new local directory called `SecOps-Studio` is created in your current working directory.
- **Note:** cloning downloads repository contents; it does not install Claude Code, execute the MCP server, or provide API keys. If that directory already exists, use the existing clone and update it with Git rather than cloning over it.

#### 2. `cd SecOps-Studio/torsh4rk-threat-intel-mcp`

- **`cd`** means *change directory*.
- **`SecOps-Studio/torsh4rk-threat-intel-mcp`** is the relative path to this module inside the downloaded repository.
- **Result:** your terminal's working directory becomes the MCP module folder, where `server.py`, `tests/`, and the documentation live.
- **Verify:** run `pwd` to display the absolute path, and `ls -la` to inspect the files. If the directory is missing, check where you ran `git clone`.

#### 3. `python3 -m unittest discover -s tests -v`

This executes the repository's **offline unit test suite**, without contacting live intelligence APIs.

| Segment | Meaning |
| --- | --- |
| `python3` | Start the Python 3 interpreter |
| `-m unittest` | Run Python's built-in `unittest` module as a program |
| `discover` | Find matching test modules automatically |
| `-s tests` | Use the local `tests/` directory as the discovery start path |
| `-v` | Enable verbose output, including individual test names |

**Expected result:** 12 tests are discovered and a successful run ends in `OK`. A test failure indicates a local regression or environment problem. The suite checks classification, private/non-global IP safeguards, malformed indicators, source contradiction handling, API-key checks, output filtering, and JSON-RPC/MCP dispatch. External provider requests are mocked.

This command **does not** start a persistent MCP service and **does not** make your project available to Claude Code.

#### 4. `claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"`

This **registers** the locally installed MCP server in Claude Code.

| Segment | Meaning |
| --- | --- |
| `claude` | Start the Claude Code command-line interface |
| `mcp add` | Save a new MCP server configuration |
| `torsh4rk-threat-intel` | Your chosen name for this MCP connection |
| `--` | Separator: remaining arguments belong to the server launch command, not Claude Code |
| `python3` | Executable Claude Code will start when connecting to the server |
| `"$(pwd)/server.py"` | Shell expansion: `pwd` becomes the **absolute directory path**, followed by `/server.py` |

For example, from `/home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp`, Claude Code saves a launch command equivalent to:

~~~bash
python3 /home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp/server.py
~~~

**Why the quotation marks matter:** they keep an absolute path containing spaces together as one shell argument. **Why the absolute path matters:** Claude Code may be started from another directory later; a relative `server.py` path could fail.

**Scope:** without a `--scope` flag, Claude Code defaults to **local scope** for the current project. To use the same MCP from your other projects on this machine, choose **user scope** instead:

~~~bash
claude mcp add --scope user torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

Use the user-scope command **instead of** the original registration command when you want user-wide availability. You only need to register once per desired scope. Configuration is local to your machine; registering does **not** publish an internet endpoint or automatically launch investigations.

### Verify the MCP connection

~~~bash
claude mcp list
claude mcp get torsh4rk-threat-intel
claude
~~~

Inside the interactive Claude Code session, enter:

~~~text
/mcp
~~~

Inspect the MCP panel for `torsh4rk-threat-intel` and its connection status. An `Added` message after registration confirms that the configuration was saved, **not necessarily that the server is healthy**. A connection error may indicate a stale Python path or an incompatible Python version.

To unregister the current-scope entry:

~~~bash
claude mcp remove torsh4rk-threat-intel
~~~

## Safe first investigation

Once the MCP server is connected, send Claude Code a message such as:

> Use the TORSh4rk Threat Intelligence MCP to classify the reserved example domain `example.org` with `triage_indicator`. Check `server_status`, then provide the `phishing` defensive playbook. Do not invoke any external intelligence providers.

This exercises **offline** tools. For actual IOC enrichment, confirm authorization, data-sharing rules, and the relevant provider's current terms before using internet-connected lookups.

### Correlating analyst-supplied evidence

Example arguments for `correlate_evidence`:

~~~json
{
  "evidence": [
    {"indicator": "example.org", "source": "SOC investigation", "assessment": "suspicious"},
    {"indicator": "example.org", "source": "Independent analyst", "assessment": "unknown"}
  ]
}
~~~

The tool groups reports and suggests a **review priority**, not an attack attribution or proof of compromise.

## Optional intelligence-provider API keys

**No keys are required** for `triage_indicator`, `correlate_evidence`, `defensive_playbook`, `server_status`, or the offline unit tests.

Remote connectors may require:

| Environment variable | Used by |
| --- | --- |
| `ABUSECH_AUTH_KEY` | ThreatFox, MalwareBazaar, URLhaus |
| `ABUSEIPDB_API_KEY` | AbuseIPDB |

See [`.env.example`](.env.example) for **variable names only**. This project does **not** automatically load `.env` files. Inject actual values into the Claude-launched process via a secure local environment/secret-management mechanism. Avoid embedding secrets in README examples, commits, screenshots, or shell history.

**Privacy:** lookups transmit the queried indicator and may transmit provider-account metadata to external services. Do not submit confidential customer data or internal indicators without permission.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `git: command not found` | Install Git using your operating system's package manager |
| `cd: ... No such file or directory` | Confirm the clone completed and inspect the current directory with `pwd` and `ls` |
| `python3: command not found` or old Python | Install Python 3.11+ and verify `python3 --version` |
| `claude: command not found` | Install and authenticate the official Claude Code CLI; see the setup link above |
| `python3 server.py` prints nothing | This is normal: the stdio server waits for JSON-RPC input. Use Ctrl+C to exit; Claude Code starts it automatically |
| `claude mcp list` reports a failed connection | Run `claude mcp get torsh4rk-threat-intel`; check the absolute `server.py` path, Python version, and client permissions |
| Key-required error from an online lookup | Set the appropriate environment variable for the MCP process; offline tools remain usable |
| Provider HTTP 401/403/429 or timeout | Check provider authentication, subscription/usage policy, quotas, or current availability |
| Existing MCP name / wrong scope | Inspect `claude mcp list`; remove the entry in the relevant scope before re-adding |

For Claude Code behavior, use the [official MCP documentation](https://code.claude.com/docs/en/mcp) and `/doctor` or `/mcp` inside Claude Code.

## Security and limitations

- **Read-only:** no arbitrary HTTP fetch, remote code execution, shell tool, Tor browsing, credential extraction, malware downloads, or incident-response enforcement.
- **Network restrictions:** fixed HTTPS provider endpoints, disabled redirects, 10-second timeouts, and 2 MB response size limits.
- **Indicator controls:** non-global IP addresses are rejected for remote lookup; metadata fields and lengths are bounded.
- **Untrusted data:** providers may return misleading or adversarial content. Never follow instructions found in IOC descriptions or infer attribution solely from matches.
- **Local trust assumption:** stdio is launched by a trusted user/client; this MVP has no network-facing authentication, enterprise RBAC, audit logging, persistent cache, or comprehensive rate limiting.
- **Maturity:** 12 offline tests cover selected behavior; provider interoperability and production security have **not** been certified.

Read [Threat Model](docs/THREAT_MODEL.md), [Security Policy](SECURITY.md), and [Attribution](ATTRIBUTION.md) before extending or deploying this code.

## Repository & license

- **Repository:** [torsh4rk/SecOps-Studio](https://github.com/torsh4rk/SecOps-Studio)
- **Module:** [torsh4rk-threat-intel-mcp](https://github.com/torsh4rk/SecOps-Studio/tree/main/torsh4rk-threat-intel-mcp)
- **License:** [MIT](LICENSE) © 2026 torsh4rk.
- **Documentation:** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

**Engineering principle:** *Investigate with evidence. Correlate with caution. Act only with authorization.*
