# Threat model — Agro AI Guardian v0.1

**Ativos:** trilhas de auditoria de agentes, identidades autenticadas, APIs de gateways agrícolas, ferramentas de IA, sensores, sistemas de irrigação e outras cargas OT. O programa consome telemetria **read-only**; não controla campo.

**Fronteiras de confiança:** entrada externa → gateway autenticado → stream JSONL validado → regras determinísticas → consola SOC. O modelo local opcional só recebe metadados de achados e não pode controlar ferramentas.

**Ameaças consideradas:** prompt injection, invocação indevida de ferramentas, identidades desconhecidas, tentativa de atuação física, exfiltração para destinos externos, uso excessivo de APIs e dados incoerentes de sensores.

**Controles fora deste MVP:** mTLS, autenticação, RBAC de rede, filtragem real de egress/DNS, verificação de integridade/assinatura de logs, SIEM, resposta a incidentes, autorização humana verificável, bloqueio de requisições e fail-safe de OT.

**Recomendação:** contas read-only, segmentação IT/OT, nenhum caminho de execução para SCADA/PLC, logs com retenção e saneamento, validação em laboratório e supervisão por profissionais. Trate eventos como dados, não como ordens. Não use este monitor isoladamente para proteger processos agrícolas críticos.

**Limites conhecidos:** sem análise multimodal, detecção semântica, correlação distribuída, autenticação integrada, sincronização de relógios ou aplicação de políticas de rede.
