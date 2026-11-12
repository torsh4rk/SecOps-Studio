#!/usr/bin/env python3
"""Read-only, dependency-free MCP threat-intelligence server (stdio/JSON-RPC)."""
from __future__ import annotations

import ipaddress
import json
import os
import re
import sys
from urllib import error, parse, request

VERSION = "0.1.0"
PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}
MAX_RESPONSE = 2_000_000
TIMEOUT = 10
HASH_RE = re.compile(r"^(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})$")
CVE_RE = re.compile(r"^CVE-\d{4}-\d{4,}$", re.I)
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$", re.I)


class ToolError(Exception):
    """Expected, safe-to-display tool failure."""


def classify(value: str) -> dict:
    if not isinstance(value, str) or not (1 <= len(value.strip()) <= 2048):
        raise ToolError("Indicator must be a string of 1 to 2048 characters")
    value = value.strip()
    if CVE_RE.fullmatch(value):
        return {"type": "cve", "value": value.upper(), "external_lookup_allowed": True}
    if HASH_RE.fullmatch(value):
        return {"type": "hash", "value": value.lower(), "external_lookup_allowed": True}
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        return {"type": "ip", "value": str(ip), "external_lookup_allowed": ip.is_global}
    if DOMAIN_RE.fullmatch(value):
        return {"type": "domain", "value": value.lower(), "external_lookup_allowed": True}
    if value.startswith(("http://", "https://")):
        try:
            url = parse.urlsplit(value)
            host = url.hostname or ""
            if url.username or url.password or not host or url.port is None and ":" in url.netloc.split("@")[0] and host.count(":") == 0:
                raise ValueError("Invalid URL authority")
            h = classify(host)
            if h["type"] not in ("domain", "ip"):
                raise ValueError("Invalid URL hostname")
            if url.port is not None and not 1 <= url.port <= 65535:
                raise ValueError("Invalid port")
            return {"type": "url", "value": parse.urlunsplit((url.scheme, url.netloc.lower(), url.path, url.query, "")), "external_lookup_allowed": h["external_lookup_allowed"]}
        except (ValueError, RecursionError) as exc:
            raise ToolError("Malformed URL") from exc
    raise ToolError("Unsupported indicator; expected public IP, domain, URL, CVE, or MD5/SHA1/SHA256")


def validate(value: str, kinds: tuple[str, ...]) -> dict:
    item = classify(value)
    if item["type"] not in kinds:
        raise ToolError(f"Expected indicator of type {', '.join(kinds)}")
    if not item["external_lookup_allowed"]:
        raise ToolError("Private/non-global IP addresses and URLs cannot be sent to external intelligence services")
    return item


def limited(value, limit=180):
    """Keep only scalar provider data; never return raw HTML, commands or binaries."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return "".join(c if c.isprintable() else " " for c in value)[:limit]
    return None


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_json(url: str, payload=None, key=None, form=False) -> dict:
    """Only fixed HTTPS endpoints chosen by this source code may call here."""
    headers = {"Accept": "application/json", "User-Agent": f"torsh4rk-threat-intel-mcp/{VERSION}"}
    body = None
    if key:
        headers["Auth-Key"] = key
    if payload is not None:
        if form:
            body = parse.urlencode(payload).encode("ascii")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=TIMEOUT) as response:
            if not str(response.headers.get("Content-Type", "")).lower().startswith(("application/json", "text/json", "application/octet-stream")):
                raise ToolError("Provider returned an unexpected content type")
            data = response.read(MAX_RESPONSE + 1)
            if len(data) > MAX_RESPONSE:
                raise ToolError("Provider response exceeded the safety size limit")
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                raise ToolError("Provider returned an unexpected JSON structure")
            return parsed
    except error.HTTPError as exc:
        raise ToolError(f"Provider HTTP error {exc.code}; verify API key, quota and endpoint availability") from exc
    except (error.URLError, TimeoutError) as exc:
        raise ToolError("Provider is unavailable or timed out") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise ToolError("Provider returned invalid JSON") from exc


def require_key(name: str) -> str:
    key = os.environ.get(name, "").strip()
    if not key:
        raise ToolError(f"Set the {name} environment variable to enable this read-only lookup")
    return key


def response(source, indicator, status, findings=None, **extra):
    return {"source": source, "indicator": indicator, "status": status, "findings": findings or [],
            "trust_boundary": "UNTRUSTED_EXTERNAL_DATA; evidence is not proof or attribution",
            "analyst_review_required": True, **extra}


def lookup_otx(indicator: str):
    item = validate(indicator, ("ip", "domain", "hash", "cve"))
    paths = {"ip": "IPv4", "domain": "domain", "hash": "file", "cve": "cve"}
    if item["type"] == "ip" and ":" in item["value"]:
        paths["ip"] = "IPv6"
    url = f"https://otx.alienvault.com/api/v1/indicators/{paths[item['type']]}/{parse.quote(item['value'], safe='')}/general"
    data = request_json(url)
    pulses = data.get("pulse_info") or {}
    matches = pulses.get("pulses") or []
    findings = [{"id": limited(x.get("id")), "name": limited(x.get("name")),
                 "created": limited(x.get("created"))} for x in matches[:10] if isinstance(x, dict)]
    return response("AlienVault OTX", item["value"], "ok", findings, reported_pulse_count=limited(pulses.get("count")))


def lookup_threatfox(indicator: str):
    item = validate(indicator, ("ip", "domain", "hash", "url"))
    key = require_key("ABUSECH_AUTH_KEY")
    is_hash = item["type"] == "hash"
    payload = {"query": "search_hash", "hash": item["value"]} if is_hash else {"query": "search_ioc", "search_term": item["value"], "exact_match": True}
    data = request_json("https://threatfox-api.abuse.ch/api/v1/", payload, key=key)
    hits = data.get("data") if isinstance(data.get("data"), list) else []
    findings = [{k: limited(hit.get(k)) for k in ("ioc", "ioc_type", "threat_type", "malware_printable", "first_seen_utc", "last_seen_utc", "confidence_level")}
                for hit in hits[:10] if isinstance(hit, dict)]
    return response("ThreatFox", item["value"], limited(data.get("query_status")), findings)


def lookup_malwarebazaar(file_hash: str):
    item = validate(file_hash, ("hash",))
    data = request_json("https://mb-api.abuse.ch/api/v1/", {"query": "get_info", "hash": item["value"]},
                        key=require_key("ABUSECH_AUTH_KEY"), form=True)
    hits = data.get("data") if isinstance(data.get("data"), list) else []
    findings = [{k: limited(hit.get(k)) for k in ("sha256_hash", "md5_hash", "sha1_hash", "first_seen", "last_seen", "file_type", "signature")}
                for hit in hits[:10] if isinstance(hit, dict)]
    return response("MalwareBazaar", item["value"], limited(data.get("query_status")), findings)


def lookup_urlhaus_host(host: str):
    item = validate(host, ("domain", "ip"))
    data = request_json("https://urlhaus-api.abuse.ch/v1/host/", {"host": item["value"]},
                        key=require_key("ABUSECH_AUTH_KEY"), form=True)
    hits = data.get("urls") if isinstance(data.get("urls"), list) else []
    findings = [{k: limited(hit.get(k)) for k in ("id", "date_added", "url_status", "threat", "last_online")}
                for hit in hits[:10] if isinstance(hit, dict)]
    return response("URLhaus", item["value"], limited(data.get("query_status")), findings)


def lookup_cisa_kev(cve: str):
    item = validate(cve, ("cve",))
    data = request_json("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    hits = [row for row in data.get("vulnerabilities", []) if isinstance(row, dict) and row.get("cveID", "").upper() == item["value"]]
    fields = ("cveID", "vendorProject", "product", "vulnerabilityName", "dateAdded", "dueDate", "knownRansomwareCampaignUse", "requiredAction")
    findings = [{k: limited(row.get(k)) for k in fields} for row in hits[:1]]
    return response("CISA KEV", item["value"], "listed" if findings else "not_listed", findings,
                    catalog_version=limited(data.get("catalogVersion")), catalog_released=limited(data.get("dateReleased")))


def lookup_abuseipdb(ip: str):
    item = validate(ip, ("ip",))
    if ":" in item["value"]:
        raise ToolError("AbuseIPDB lookup in this MVP supports IPv4 only")
    url = "https://api.abuseipdb.com/api/v2/check?" + parse.urlencode({"ipAddress": item["value"], "maxAgeInDays": 90})
    # AbuseIPDB requires the Key header (not abuse.ch Auth-Key).
    key = require_key("ABUSEIPDB_API_KEY")
    req = request.Request(url, headers={"Accept": "application/json", "Key": key, "User-Agent": f"torsh4rk-threat-intel-mcp/{VERSION}"})
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=TIMEOUT) as result:
            raw = result.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise ToolError("Provider response exceeded the safety size limit")
            data = json.loads(raw)
    except error.HTTPError as exc:
        raise ToolError(f"Provider HTTP error {exc.code}; verify API key and quota") from exc
    except (error.URLError, TimeoutError) as exc:
        raise ToolError("Provider is unavailable or timed out") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise ToolError("Provider returned invalid JSON") from exc
    info = data.get("data", {}) if isinstance(data, dict) else {}
    fields = ("ipAddress", "abuseConfidenceScore", "totalReports", "lastReportedAt", "usageType", "isTor")
    return response("AbuseIPDB", item["value"], "ok", [{k: limited(info.get(k)) for k in fields}])


def correlate_evidence(evidence: list):
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 50:
        raise ToolError("evidence must contain 1 to 50 records")
    groups = {}
    for i, record in enumerate(evidence):
        if not isinstance(record, dict):
            raise ToolError(f"evidence[{i}] must be an object")
        item = classify(record.get("indicator"))
        source = record.get("source")
        assessment = record.get("assessment")
        if not isinstance(source, str) or not 1 <= len(source.strip()) <= 80:
            raise ToolError(f"evidence[{i}].source must be 1 to 80 characters")
        if assessment not in ("malicious", "suspicious", "benign", "unknown"):
            raise ToolError(f"evidence[{i}].assessment is invalid")
        groups.setdefault(item["value"], []).append({"source": source.strip()[:80], "assessment": assessment})
    cases = []
    for indicator, records in groups.items():
        malicious_sources = {e["source"].lower() for e in records if e["assessment"] == "malicious"}
        benign_sources = {e["source"].lower() for e in records if e["assessment"] == "benign"}
        suspicious_sources = {e["source"].lower() for e in records if e["assessment"] == "suspicious"}
        contradictory = bool(malicious_sources and benign_sources)
        priority = "high" if len(malicious_sources) >= 2 or contradictory else "medium" if malicious_sources or suspicious_sources else "low"
        cases.append({"indicator": indicator, "report_count": len(records),
                      "independent_source_count": len({r['source'].lower() for r in records}),
                      "confirmed_malicious_sources": len(malicious_sources), "contradictory_reports": contradictory,
                      "review_priority_heuristic": priority, "reports": records})
    return {"cases": cases, "scope": "Deterministic grouping of analyst-supplied evidence only",
            "warning": "No automated attribution, no independent verification, and no claim of compromise"}


PLAYBOOKS = {
    "phishing": ["Preserve headers and timestamps", "Check URL/domain against approved intel feeds", "Determine user interaction and delivery scope", "Quarantine with owner approval", "Rotate credentials only if exposure is confirmed"],
    "ransomware": ["Escalate to incident command", "Preserve volatile evidence and isolate affected hosts under policy", "Check backups and recovery readiness", "Correlate hashes, domains and CISA KEV findings", "Coordinate legal/compliance notification assessments"],
    "malware": ["Do not download or execute samples through this MCP", "Collect hashes and host telemetry", "Cross-check sample metadata against trusted intel", "Validate detections with EDR and scope impacted hosts", "Escalate containment for human approval"],
    "credential_exposure": ["Confirm authorization and affected account ownership", "Avoid collecting raw passwords or credential dumps", "Check sign-in anomalies, MFA and token use", "Revoke sessions and reset credentials under incident policy", "Preserve evidence without disclosing personal data"],
}


def arg(name, description, kind="string"):
    return {"type": kind, "description": description}


def spec(name, description, fields, required):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": fields, "required": required, "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": name.startswith("lookup_")}}


TOOLS = [
    spec("triage_indicator", "Classify an IOC locally; no network activity.", {"indicator": arg("indicator", "Public IP, domain, URL, file hash or CVE")}, ["indicator"]),
    spec("lookup_otx", "Read-only public AlienVault OTX indicator context.", {"indicator": arg("indicator", "IP, domain, hash or CVE")}, ["indicator"]),
    spec("lookup_threatfox", "Read-only ThreatFox IOC metadata; needs ABUSECH_AUTH_KEY.", {"indicator": arg("indicator", "IP, domain, URL or hash")}, ["indicator"]),
    spec("lookup_malwarebazaar", "Read-only sample metadata (never downloads malware); needs ABUSECH_AUTH_KEY.", {"file_hash": arg("file_hash", "MD5, SHA1 or SHA256")}, ["file_hash"]),
    spec("lookup_urlhaus_host", "Read-only URLhaus malware distribution host metadata; needs ABUSECH_AUTH_KEY.", {"host": arg("host", "Public domain or IP")}, ["host"]),
    spec("lookup_cisa_kev", "Find a CVE in the official CISA Known Exploited Vulnerabilities catalog.", {"cve": arg("cve", "CVE-YYYY-NNNN")}, ["cve"]),
    spec("lookup_abuseipdb", "Read-only IPv4 abuse reputation; needs ABUSEIPDB_API_KEY.", {"ip": arg("ip", "Public IPv4 address")}, ["ip"]),
    spec("correlate_evidence", "Group analyst-supplied observations without claiming attribution.", {"evidence": {"type": "array", "minItems": 1, "maxItems": 50, "items": {"type": "object", "properties": {"indicator": {"type": "string"}, "source": {"type": "string"}, "assessment": {"type": "string", "enum": ["malicious", "suspicious", "benign", "unknown"]}}, "required": ["indicator", "source", "assessment"]}}}, ["evidence"]),
    spec("defensive_playbook", "Return a human-reviewed SOC triage checklist; no external operations.", {"scenario": {"type": "string", "enum": list(PLAYBOOKS)}}, ["scenario"]),
    spec("server_status", "Show offline server version and configured integration names, never keys.", {}, []),
]


def dispatch(name: str, args: dict) -> dict:
    if name not in {t["name"] for t in TOOLS}:
        raise ToolError("Unknown tool")
    if not isinstance(args, dict):
        raise ToolError("Arguments must be an object")
    schema = next(t["inputSchema"] for t in TOOLS if t["name"] == name)
    if set(args) - set(schema["properties"]) or any(k not in args for k in schema["required"]):
        raise ToolError("Unknown or missing arguments")
    if name == "triage_indicator":
        return classify(args["indicator"])
    if name == "lookup_otx":
        return lookup_otx(args["indicator"])
    if name == "lookup_threatfox":
        return lookup_threatfox(args["indicator"])
    if name == "lookup_malwarebazaar":
        return lookup_malwarebazaar(args["file_hash"])
    if name == "lookup_urlhaus_host":
        return lookup_urlhaus_host(args["host"])
    if name == "lookup_cisa_kev":
        return lookup_cisa_kev(args["cve"])
    if name == "lookup_abuseipdb":
        return lookup_abuseipdb(args["ip"])
    if name == "correlate_evidence":
        return correlate_evidence(args["evidence"])
    if name == "defensive_playbook":
        if args["scenario"] not in PLAYBOOKS:
            raise ToolError("Invalid scenario")
        return {"scenario": args["scenario"], "checklist": PLAYBOOKS[args["scenario"]], "requires_human_approval": True}
    return {"name": "torsh4rk-threat-intel-mcp", "version": VERSION, "transport": "stdio", "mode": "read_only",
            "integrations_configured": {"abuse_ch": bool(os.getenv("ABUSECH_AUTH_KEY")), "abuseipdb": bool(os.getenv("ABUSEIPDB_API_KEY"))}}


def handle(msg):
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
        return {"jsonrpc": "2.0", "id": msg.get("id") if isinstance(msg, dict) else None, "error": {"code": -32600, "message": "Invalid request"}}
    if "id" not in msg:
        return None  # Notifications must never receive responses.
    mid, method, params = msg["id"], msg["method"], msg.get("params") or {}
    if not isinstance(params, dict):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "Invalid parameters"}}
    if method == "initialize":
        protocol = params.get("protocolVersion")
        result = {"protocolVersion": protocol if protocol in PROTOCOLS else "2025-06-18",
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "torsh4rk-threat-intel-mcp", "version": VERSION}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        try:
            output = dispatch(params.get("name"), params.get("arguments") or {})
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}], "isError": False}
        except (ToolError, TypeError, KeyError, ValueError) as exc:
            result = {"content": [{"type": "text", "text": json.dumps({"error": str(exc)})}], "isError": True}
        except Exception:
            result = {"content": [{"type": "text", "text": json.dumps({"error": "Unexpected provider or server error"})}], "isError": True}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            reply = handle(msg)
            if reply is not None:
                sys.stdout.write(json.dumps(reply, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
