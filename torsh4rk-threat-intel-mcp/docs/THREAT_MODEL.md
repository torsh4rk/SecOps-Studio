# Threat model (research MVP)

## Protected assets

API keys, internal indicators and case context, analyst workstation privileges, integrity of investigation notes, and the reputation/availability of upstream data services.

## Adversary and trust boundaries

1. An untrusted indicator may be supplied by an end user, document, log or AI agent.
2. An upstream intelligence service may return misleading, outdated, adversarial or prompt-injection text.
3. The AI client may infer attribution or initiate unauthorized response actions if it over-trusts tool output.
4. API keys and queried indicators cross the local-to-provider trust boundary when remote calls occur.

## Controls actually implemented

- Fixed destination URLs only; no tool accepts an arbitrary destination to fetch.
- Non-global IP addresses are refused for remote lookups; typed domain, URL, CVE and hash validation.
- Secrets read from environment variables; no returned key values; no secrets bundled.
- HTTP redirects disabled; 10-second timeouts; 2 MB maximum response size.
- Selected, bounded metadata only from external APIs. Raw malware, HTML and full dumps are excluded.
- `correlate_evidence` treats source count as context, surfaces contradictory findings and explicitly avoids attribution claims.
- No mutation/shell/download/hidden-service tools.

## Residual risk and deployment requirements

- Provider content could still contain manipulative strings in selected metadata; the client must not treat external text as system instructions.
- Provider-side rate limits and retention/terms vary; implement organizational authorization, quotas, audit controls and legal review separately.
- Indicator sharing with providers may disclose investigative interest. Avoid confidential customer data unless authorized.
- Compromised local MCP client processes can access inherited credentials; use least-privilege secrets and isolated client profiles.
- Outbound lookup integrations are not live-tested by CI; provider schemas and authentication may change.
- This MVP does not provide RBAC, enterprise-grade logging, privacy redaction of all inputs, persistent cache, or service-to-service auth.

## Security validation checklist

- Run offline unit tests.
- Inspect source and third-party endpoints before configuring real API keys.
- Try only test indicators authorized by your organization.
- Verify upstream terms, quotas, TLS and authentication behavior in staging.
- Review investigation results before any containment or notifications.
