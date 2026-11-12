# Agro AI Guardian 🛡️🌱

**Agente de defesa cibernética contra abuso de agentes de IA em ambientes agrícolas, IoT/OT e APIs.** MVP em Python 3.11+, sem dependências externas em tempo de execução.

> **Somente defesa.** Analisa telemetria de ativos próprios/autorizados. **Não** escaneia terceiros, explora falhas ou controla drones, válvulas, tratores, bombas ou PLCs. **Não bloqueia tráfego sozinho.** Os resultados `allow`, `review` e `deny` são recomendações; cabe a um gateway de confiança impor políticas. **Não é certificado nem pronto para produção OT.**

## O que detecta

- Agentes não autorizados e chamadas de ferramentas fora da allowlist por identidade.
- Tentativas de controle de equipamentos agrícolas (ações físicas/OT sempre classificadas como críticas).
- Indicadores básicos de prompt injection em português e inglês e fontes de texto não confiáveis.
- Tentativas de exportação para endereços fora dos hosts exatos autorizados.
- Picos de eventos de API/autenticação por agente em janelas de 60 segundos.
- Leituras de umidade do solo fora de 0–100% (exemplo ilustrativo).
- Saída de alertas sem replicar prompts brutos, argumentos ou segredos.

**IA opcional:** o Ollama local pode resumir achados saneados, mas não decide o risco nem executa ferramentas.

## Rodar

```bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/agro-ai-guardian
python3 --version       # Python 3.11+
python3 -m agro_guardian --input examples/events.jsonl
python3 -m unittest discover -s tests -v
```

Para gerar arquivo: `python3 -m agro_guardian --input examples/events.jsonl --output alerts.jsonl`.

Para usar um LLM local, instale e inicie o [Ollama](https://ollama.com/), disponibilize um modelo, e passe `--local-llm llama3.2`. O motor determinístico funciona sem modelo, Internet ou chaves de API.

## Evento de entrada (JSONL)

Um objeto JSON por linha:

```json
{"timestamp":"2026-11-12T05:00:00Z","agent_id":"farm-observer","event_type":"tool_call","tool":"read_sensor","asset":"field-01"}
```

| Campo | Descrição |
|---|---|
| `timestamp` | ISO-8601 com offset obrigatório |
| `agent_id` | Identificador do agente (deve ser autenticado externamente) |
| `event_type` | `tool_call`, `text_input`, `api_request`, `sensor_reading`, `auth_event` |
| `tool`, `source`, `destination`, `asset`, `content`, `value` | Opcionais por tipo de evento |
| `event_id` | Opcional; hash derivado quando ausente |

Edite `config/policy.example.json` para configurar os agentes aprovados, ferramentas, hosts e limite de taxa. Não coloque credenciais reais nos exemplos.

## Segurança, escopo e limitações

1. **MVP read-only**, não WAF, EDR, IPS ou firewall. `deny` é uma recomendação registrada, não um bloqueio executado.
2. Filtros por expressões regulares não capturam todos os ataques de prompt injection; falsos positivos/negativos são possíveis.
3. Limites de volume ficam em memória por processo e pressupõem eventos cronológicos; não substituem controle distribuído de taxa.
4. `agent_id` vindo de JSON não comprova identidade. Em produção, identidade e origem devem ser verificadas em gateway autenticado.
5. Allowlist de hosts aqui só avalia texto da URL; filtragem efetiva de egress/DNS deve ocorrer na rede.
6. Segregar redes IT/OT; nenhuma integração de campo deve operar sem aprovação externa verificável e ensaios em laboratório.
7. Resumos do modelo são conteúdo não confiável e jamais podem alterar decisões ou ferramentas.

Leia [modelo de ameaças](docs/THREAT_MODEL.md). Referências: [MITRE ATLAS](https://atlas.mitre.org/), [NIST SP 800-82 Rev. 3](https://csrc.nist.gov/pubs/sp/800/82/r3/final), [OWASP Agentic Skills Top 10](https://owasp.org/projects/agentic-skills-top-10).

**Finalidade:** exclusivamente Blue Team, SOC e AI Security, incluindo monitoramento de lavouras conectadas. Código de demonstração; validação em ambientes reais é trabalho adicional.
