"""Offline, read-only defensive policy checks. No network, shell, or OT actuation."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

INJECTION_PATTERNS = (
    re.compile(r"ignore (?:all |any |the )?(?:previous|prior) instructions", re.I),
    re.compile(r"(?:ignore|desconsidere) (?:(?:todas? as?|as) )?instru[cç][õo]es anteriores", re.I),
    re.compile(r"(?:reveal|print|mostre|revele).{0,50}(?:system prompt|prompt do sistema)", re.I),
    re.compile(r"<\s*(?:system|developer)\s*>", re.I),
    re.compile(r"(?:override|bypass|ignore).{0,40}(?:security policy|safety policy|guardrails)", re.I),
)
CRITICAL_PREFIXES = ("irrigation.", "valve.", "pump.", "tractor.", "drone.", "sprayer.", "fertilizer.", "plc.", "scada.")
EXPORT_TOOLS = frozenset({"http_post", "send_email", "upload_file", "export_data", "webhook_send"})
DECISION_RANK = {"allow": 0, "review": 1, "deny": 2}
SEVERITY_RANK = {"info": 0, "medium": 1, "high": 2, "critical": 3}

@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str

@dataclass(frozen=True)
class Result:
    event_id: str
    agent_id: str
    event_type: str
    decision: str
    severity: str
    findings: list[Finding]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

def load_policy(path: str | Path) -> dict[str, Any]:
    policy = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or not isinstance(policy.get("approved_agents"), dict):
        raise ValueError("Policy requires approved_agents mapping")
    if not isinstance(policy.get("allowed_destination_hosts"), list):
        raise ValueError("Policy requires allowed_destination_hosts list")
    for key, value in policy["approved_agents"].items():
        if not isinstance(key, str) or not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("approved_agents values must be lists of tool names")
    if not all(isinstance(x, str) for x in policy["allowed_destination_hosts"]):
        raise ValueError("allowed_destination_hosts must contain strings")
    limit = policy.get("rate_limit_per_minute", 5)
    if type(limit) is not int or not 1 <= limit <= 10000:
        raise ValueError("rate_limit_per_minute must be 1..10000")
    policy["rate_limit_per_minute"] = limit
    return policy

def _safe_str(obj: dict[str, Any], field: str, limit: int = 256) -> str:
    val = obj.get(field, "")
    if not isinstance(val, str) or len(val) > limit:
        raise ValueError(f"{field} must be a string of at most {limit} characters")
    return val

def _parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include UTC offset")
    return parsed.astimezone(timezone.utc)

def _host(value: str) -> str | None:
    try:
        url = urlsplit(value)
        if url.scheme not in {"https", "http"} or url.username or url.password:
            return None
        return url.hostname.lower().rstrip(".") if url.hostname else None
    except ValueError:
        return None

class Guardian:
    """Stateful analysis-only detector for in-order JSONL streams."""

    def __init__(self, policy: dict[str, Any]):
        self.policy = policy
        self.history: dict[str, deque[datetime]] = defaultdict(deque)

    def inspect(self, event: dict[str, Any]) -> Result:
        if not isinstance(event, dict):
            raise ValueError("Each event must be a JSON object")
        agent = _safe_str(event, "agent_id", 128)
        kind = _safe_str(event, "event_type", 32)
        timestamp = _parse_time(_safe_str(event, "timestamp", 64))
        tool = _safe_str(event, "tool", 128)
        asset = _safe_str(event, "asset", 128)
        destination = _safe_str(event, "destination", 2048)
        source = _safe_str(event, "source", 128)
        content = _safe_str(event, "content", 20000)
        if not agent or kind not in {"tool_call", "text_input", "api_request", "sensor_reading", "auth_event"}:
            raise ValueError("agent_id and supported event_type are required")
        if len(json.dumps(event, ensure_ascii=False)) > 65536:
            raise ValueError("Event exceeds 64 KiB")
        event_id = _safe_str(event, "event_id", 128) or sha256(json.dumps(event, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
        findings: list[Finding] = []
        decision = "allow"

        def flag(rule: str, severity: str, message: str, recommended: str) -> None:
            nonlocal decision
            findings.append(Finding(rule, severity, message))
            if DECISION_RANK[recommended] > DECISION_RANK[decision]:
                decision = recommended

        approved = self.policy["approved_agents"]
        if agent not in approved:
            flag("unknown_agent", "high", "Identidade do agente não autorizada.", "deny")
        if kind == "tool_call":
            if not tool:
                flag("missing_tool", "high", "Chamada sem identificação da ferramenta.", "deny")
            elif tool not in approved.get(agent, []):
                flag("tool_not_allowed", "high", "Ferramenta fora da lista autorizada para o agente.", "deny")
            if tool.casefold().startswith(CRITICAL_PREFIXES):
                flag("ot_actuation", "critical", "Ação física/OT solicitada: aprovação externa obrigatória; este monitor nunca executa comandos.", "deny")
            if tool in EXPORT_TOOLS:
                host = _host(destination)
                allowed = {item.lower().rstrip(".") for item in self.policy["allowed_destination_hosts"]}
                if not host or host not in allowed:
                    flag("exfiltration_destination", "critical", "Destino de exportação ausente, inválido ou não autorizado.", "deny")
        if kind == "text_input":
            if any(pattern.search(content) for pattern in INJECTION_PATTERNS):
                flag("prompt_injection_indicator", "high", "Possível instrução maliciosa em conteúdo não confiável.", "review")
            if source not in {"audit-gateway", "field-gateway", "security-siem"}:
                flag("untrusted_input_source", "medium", "Origem do texto não reconhecida: tratar como dados, nunca como instruções.", "review")
        if kind in {"api_request", "auth_event"}:
            # Requires chronological input; not designed for distributed ingestion.
            q = self.history[agent]
            cutoff = timestamp - timedelta(seconds=60)
            while q and q[0] < cutoff:
                q.popleft()
            q.append(timestamp)
            if len(q) > self.policy["rate_limit_per_minute"]:
                flag("agent_activity_spike", "high", "Volume de eventos excede o limite configurado por minuto.", "review")
        if kind == "sensor_reading" and asset == "soil_moisture":
            reading = event.get("value")
            if type(reading) not in {int, float} or not 0 <= reading <= 100:
                flag("sensor_anomaly", "medium", "Leitura inválida ou fora da faixa física esperada (0–100%).", "review")
        severity = max((f.severity for f in findings), key=lambda x: SEVERITY_RANK[x], default="info")
        msg = "Sem anomalias pelas regras configuradas." if not findings else " ; ".join(f.message for f in findings)
        return Result(event_id, agent, kind, decision, severity, findings, msg)
