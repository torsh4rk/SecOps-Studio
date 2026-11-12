# TORSh4rk Threat Intelligence MCP

**Inteligência de ameaças somente para leitura, investigações de segurança assistidas por IA, correlação de evidências e triagem SOC.**

[![CI](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml/badge.svg)](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![MCP](https://img.shields.io/badge/Protocol-MCP-6750A4)
![MIT](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Maturity-Research%20MVP-6B7280)

**Idiomas:** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

> **v0.1.0 — MVP de pesquisa, não pronto para produção nem auditado de forma independente.** Resultados são indícios de investigação, **não atribuição comprovada**. Todas as ferramentas são de leitura; qualquer resposta operacional exige autorização humana.

## Objetivo

Equipes de segurança precisam relacionar indicadores isolados: endereços IP, domínios suspeitos, hashes de malware, CVEs e relatórios contraditórios. O **TORSh4rk Threat Intelligence MCP** conecta um cliente local de IA confiável (como Claude Code) a ferramentas de investigação por meio do **Model Context Protocol (MCP)**.

Esta implementação independente em Python foi inspirada no *conceito de agregação de inteligência* de [1SHA1024/darknet-mcp-server](https://github.com/1SHA1024/darknet-mcp-server). **Não é um fork**, não promete a mesma quantidade de ferramentas e não permite navegar pela rede Tor nem acessar credenciais vazadas. Consulte [ATTRIBUTION.md](ATTRIBUTION.md).

## Ferramentas implementadas

| Ferramenta MCP | O que faz | Internet / chave |
| --- | --- | --- |
| `triage_indicator` | Classifica e valida IPs públicos, domínios, URLs HTTP(S), hashes MD5/SHA-1/SHA-256 e CVEs | Offline / sem chave |
| `lookup_otx` | Consulta metadados selecionados de indicadores e pulses no AlienVault OTX | Online / sem chave configurada |
| `lookup_threatfox` | Consulta metadados de IOCs no ThreatFox | Online / `ABUSECH_AUTH_KEY` |
| `lookup_malwarebazaar` | Consulta **somente metadados** de amostras pelo hash | Online / `ABUSECH_AUTH_KEY` |
| `lookup_urlhaus_host` | Consulta metadados de hosts no URLhaus | Online / `ABUSECH_AUTH_KEY` |
| `lookup_cisa_kev` | Verifica se uma CVE está no catálogo oficial CISA KEV | Online / sem chave |
| `lookup_abuseipdb` | Consulta reputação de IPv4 público no AbuseIPDB | Online / `ABUSEIPDB_API_KEY` |
| `correlate_evidence` | Agrupa até 50 observações fornecidas pelo analista e indica conflitos | Offline / sem chave |
| `defensive_playbook` | Fornece checklists SOC para phishing, ransomware, malware e exposição de credenciais | Offline / sem chave |
| `server_status` | Mostra versão e integrações configuradas **sem revelar chaves** | Offline / sem chave |

As integrações externas dependem de disponibilidade, regras, cotas e eventuais mudanças das APIs. **Os testes automatizados simulam respostas HTTP; eles não comprovam interoperabilidade real com os provedores.**

## Arquitetura e limites de confiança

~~~text
Claude Code (cliente MCP local confiável)
       |
       | MCP JSON-RPC via stdin / stdout (stdio)
       v
server.py — biblioteca padrão Python 3.11+
       |                          |
       | Operações locais         | Consultas HTTPS autorizadas
       | - validação de IOCs      | - AlienVault OTX
       | - correlação             | - abuse.ch: ThreatFox, MalwareBazaar, URLhaus
       | - playbooks SOC          | - CISA KEV e AbuseIPDB
       v                          v
       Evidências estruturadas e limitadas
           (dados externos não confiáveis)
                         |
                         v
                   Revisão humana
~~~

O MCP **não é um serviço hospedado publicamente**. Ele é iniciado na máquina do analista pelo cliente MCP. Não executa comandos, baixa malware, coleta senhas, navega pelo Tor ou modifica controles de segurança.

## Instalação — explicação dos quatro comandos

### Pré-requisitos

- **Linux, macOS ou ambiente com Python e Claude Code CLI.** Os exemplos usam um shell POSIX (Bash/Zsh), como no Manjaro, Ubuntu e Kali.
- **Git**, para clonar o repositório.
- **Python 3.11 ou superior**, para executar o servidor e os testes. Este MVP não exige instalar pacotes pelo pip nem criar ambiente virtual.
- **Claude Code CLI instalado e autenticado** para registrar o MCP local; utilizar somente o chat do Claude no navegador não é suficiente.

Verifique:

~~~bash
git --version
python3 --version
claude --version
~~~

Se o comando `claude` não existir, consulte o [guia oficial de instalação do Claude Code](https://code.claude.com/docs/en/setup). Atualize o Python caso a versão seja anterior a 3.11.

### Execute estes quatro comandos no terminal

Comece na pasta onde deseja baixar o projeto:

~~~bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/torsh4rk-threat-intel-mcp

python3 -m unittest discover -s tests -v

claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

### 1. `git clone https://github.com/torsh4rk/SecOps-Studio.git`

- **`git`** é o cliente de controle de versão.
- **`clone`** baixa uma cópia local dos arquivos versionados e do histórico Git.
- **A URL HTTPS** identifica o repositório público `torsh4rk/SecOps-Studio`, que contém este MCP em um subdiretório; o MCP não é um repositório Git separado.
- **Resultado:** cria a pasta `SecOps-Studio` no diretório atual.
- **Importante:** clonar não instala o Claude Code, não inicia o MCP e não fornece chaves de API. Se a pasta já existir, reutilize o clone e atualize-o com Git em vez de tentar sobrescrevê-lo.

### 2. `cd SecOps-Studio/torsh4rk-threat-intel-mcp`

- **`cd`** significa *change directory*, ou mudar de diretório.
- **O caminho relativo** aponta para o módulo MCP dentro do repositório baixado.
- **Resultado:** o terminal entra na pasta com `server.py`, `tests/` e documentação.
- **Conferência:** execute `pwd` para ver o caminho absoluto e `ls -la` para listar os arquivos. Caso falhe, confirme em qual pasta o clone foi criado.

### 3. `python3 -m unittest discover -s tests -v`

Executa **testes unitários offline**, sem contatar APIs de inteligência reais.

| Parte | Explicação |
| --- | --- |
| `python3` | Abre o interpretador Python 3 |
| `-m unittest` | Executa o módulo `unittest`, incluído na biblioteca padrão |
| `discover` | Descobre automaticamente os arquivos de teste |
| `-s tests` | Define a pasta `tests/` como ponto inicial da descoberta |
| `-v` | Ativa o modo detalhado, exibindo o nome de cada teste |

**Resultado esperado:** 12 testes executados e a mensagem final `OK`. Falhas indicam um problema no ambiente ou uma regressão. Os testes cobrem classificação de indicadores, bloqueios a IPs privados/não globais, entradas inválidas, relatórios contraditórios, chaves de API, filtragem de saída e processamento MCP/JSON-RPC. As respostas HTTP externas são simuladas.

Este comando **não mantém um servidor MCP em execução** e **não o registra no Claude Code**.

### 4. `claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"`

Este comando **registra** o MCP local na configuração do Claude Code.

| Parte | Explicação |
| --- | --- |
| `claude` | Executável do Claude Code no terminal |
| `mcp add` | Adiciona uma configuração de servidor MCP |
| `torsh4rk-threat-intel` | Nome que identifica essa conexão MCP |
| `--` | Separa as opções do Claude Code do comando que inicia o servidor |
| `python3` | Executável que iniciará o servidor |
| `"$(pwd)/server.py"` | Expansão do shell: substitui `$(pwd)` pela **pasta absoluta** atual e acrescenta `/server.py` |

Por exemplo, dentro de `/home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp`, o comando salvo equivale a:

~~~bash
python3 /home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp/server.py
~~~

**Por que usar aspas?** Elas mantêm caminhos contendo espaços como um único argumento. **Por que caminho absoluto?** O Claude Code pode ser aberto a partir de outro diretório; um caminho relativo pode impedir a conexão.

**Escopo:** por padrão, o registro usa escopo **local**, associado ao projeto atual no Claude Code. Para disponibilizar o MCP em **todos os seus projetos neste computador**, escolha o escopo de usuário:

~~~bash
claude mcp add --scope user torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

Execute a variante de escopo de usuário **no lugar** da original quando essa for sua intenção. Uma configuração é suficiente por escopo. Registrar o servidor **não publica um endpoint na internet nem inicia investigações automaticamente**.

### Verificar a conexão MCP

~~~bash
claude mcp list
claude mcp get torsh4rk-threat-intel
claude
~~~

Dentro do Claude Code interativo, digite:

~~~text
/mcp
~~~

Confira o servidor `torsh4rk-threat-intel` e seu estado de conexão. Uma mensagem `Added` apenas confirma que a configuração foi gravada; **não garante que o servidor esteja funcionando**. Caso queira remover a configuração do escopo atual:

~~~bash
claude mcp remove torsh4rk-threat-intel
~~~

## Primeira investigação segura

Após conectar o MCP, peça ao Claude Code:

> Use o TORSh4rk Threat Intelligence MCP para classificar o domínio reservado `example.org` usando `triage_indicator`. Confira `server_status` e apresente o playbook defensivo de `phishing`. Não consulte serviços externos.

Esse fluxo usa somente ferramentas **offline**. Para enriquecimento real de IOCs, verifique autorização, política de compartilhamento de dados e os termos dos provedores.

### Exemplo de correlação

Argumentos de exemplo para `correlate_evidence`:

~~~json
{
  "evidence": [
    {"indicator": "example.org", "source": "SOC investigation", "assessment": "suspicious"},
    {"indicator": "example.org", "source": "Independent analyst", "assessment": "unknown"}
  ]
}
~~~

O resultado apresenta agrupamento e **prioridade sugerida para análise**, não atribuição do ataque nem prova de comprometimento.

## Chaves opcionais das APIs

**Não são necessárias chaves** para `triage_indicator`, `correlate_evidence`, `defensive_playbook`, `server_status` e os testes offline.

| Variável de ambiente | Utilização |
| --- | --- |
| `ABUSECH_AUTH_KEY` | ThreatFox, MalwareBazaar e URLhaus |
| `ABUSEIPDB_API_KEY` | AbuseIPDB |

O arquivo [`.env.example`](.env.example) contém **apenas os nomes das variáveis**. O projeto **não carrega automaticamente** arquivos `.env`. Disponibilize os valores reais ao processo iniciado pelo Claude Code utilizando um mecanismo local seguro de ambiente ou gerenciamento de segredos. Não publique chaves em commits, exemplos, imagens ou histórico do shell.

**Privacidade:** uma consulta externa transmite o indicador pesquisado e pode incluir metadados da conta do provedor. Não envie dados confidenciais de clientes sem autorização.

## Solução de problemas

| Sintoma | Verificação |
| --- | --- |
| `git: command not found` | Instale o Git pelo gerenciador de pacotes do sistema |
| `cd: ... No such file or directory` | Verifique se o clone terminou e confira `pwd` e `ls` |
| `python3: command not found` ou versão antiga | Instale Python 3.11+ e execute `python3 --version` |
| `claude: command not found` | Instale e autentique o Claude Code CLI seguindo o guia oficial |
| `python3 server.py` não imprime nada | Comportamento normal: o servidor stdio espera mensagens JSON-RPC. Saia com Ctrl+C; o Claude Code o inicia automaticamente |
| `claude mcp list` indica falha de conexão | Confira `claude mcp get torsh4rk-threat-intel`, o caminho absoluto, a versão do Python e as permissões |
| Falta de chave em uma consulta online | Configure a variável de ambiente exigida para o processo MCP; as ferramentas offline continuam funcionando |
| Erro HTTP 401/403/429 ou timeout | Verifique autenticação, cotas, termos de uso ou disponibilidade da API |
| Nome já registrado ou escopo incorreto | Confira `claude mcp list` e remova a entrada no escopo correto antes de adicioná-la novamente |

Consulte a [documentação oficial de MCP do Claude Code](https://code.claude.com/docs/en/mcp) e os comandos internos `/mcp` ou `/doctor`.

## Segurança e limitações

- **Somente leitura:** sem requisições HTTP arbitrárias, execução remota, shell, Tor, extração de credenciais, download de malware ou ações automáticas de contenção.
- **Restrições de rede:** endpoints HTTPS fixos, redirecionamentos desabilitados, limite de 10 segundos e respostas de até 2 MB.
- **Controles de indicadores:** IPs não globais não são enviados para consultas externas; metadados retornados são selecionados e limitados.
- **Dados não confiáveis:** descrições retornadas por provedores podem ser falsas ou maliciosas; não siga instruções nelas e não atribua ataques apenas por correspondência de IOCs.
- **Confiança local:** o stdio pressupõe um usuário/cliente confiável. Este MVP não inclui autenticação de rede, RBAC empresarial, trilhas completas de auditoria, cache persistente nem rate limiting abrangente.
- **Maturidade:** 12 testes offline verificam comportamentos selecionados. Integrações reais e segurança em produção **não foram certificadas**.

Leia o [Modelo de Ameaças](docs/THREAT_MODEL.md), a [Política de Segurança](SECURITY.md) e a [Atribuição](ATTRIBUTION.md) antes de expandir ou implantar o código.

## Repositório e licença

- **Repositório:** [torsh4rk/SecOps-Studio](https://github.com/torsh4rk/SecOps-Studio)
- **Módulo:** [torsh4rk-threat-intel-mcp](https://github.com/torsh4rk/SecOps-Studio/tree/main/torsh4rk-threat-intel-mcp)
- **Licença:** [MIT](LICENSE) © 2026 torsh4rk.
- **Documentação:** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

**Princípio de engenharia:** *Investigue com evidências. Correlacione com cautela. Aja somente com autorização.*
