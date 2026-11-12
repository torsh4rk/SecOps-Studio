# Security policy

**Status:** Research MVP; not an audited security product. Do not connect it to production response or blocking controls.

For suspected vulnerabilities, do not publish exploit details or secrets in a public issue. Use GitHub's private vulnerability reporting if enabled for this repository, or privately contact the repository maintainer through an established secure channel. Do not open a public issue containing sensitive indicators or customer data.

## Defensive commitments

- All exposed MCP tools are read-only. No shell, Tor browsing, credential extraction, malware download or enforcement actions.
- External API results are untrusted; agents must not execute instructions embedded in provider data.
- Only provide publicly shareable indicators to remote APIs after checking authorization and relevant sharing restrictions.
- Restrict who can launch and configure the MCP server; secrets are inherited from the local environment.
- This MVP has no built-in user authentication because stdio assumes a trusted local launcher. **Do not expose it as an unauthenticated network service.**

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).
