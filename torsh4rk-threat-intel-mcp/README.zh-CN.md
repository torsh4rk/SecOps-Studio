# TORSh4rk Threat Intelligence MCP

**面向 AI 辅助安全调查、证据关联分析与 SOC 告警研判的只读威胁情报 MCP 服务器。**

[![CI](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml/badge.svg)](https://github.com/torsh4rk/SecOps-Studio/actions/workflows/threat-intel-mcp-tests.yml)
![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB)
![MCP](https://img.shields.io/badge/Protocol-MCP-6750A4)
![MIT](https://img.shields.io/badge/License-MIT-blue)
![Status](https://img.shields.io/badge/Maturity-Research%20MVP-6B7280)

**文档语言：** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

> **v0.1.0 — 研究性 MVP，尚未达到生产就绪标准，也未经过独立安全审计。** 调查结果只是进一步分析的线索，**不等于已证实的攻击归因**。所有工具均为只读；实际事件响应必须经过人工授权。

## 项目简介

安全分析人员经常需要把分散的线索联系起来，例如 IP 地址、可疑域名、恶意软件文件哈希、CVE 编号以及互相矛盾的情报报告。**TORSh4rk Threat Intelligence MCP** 通过 **Model Context Protocol (MCP)**，为可信的本地 AI 客户端（例如 Claude Code）提供一组用途明确的安全调查工具。

本项目是独立开发的 Python 实现，受 [1SHA1024/darknet-mcp-server](https://github.com/1SHA1024/darknet-mcp-server) 的*威胁情报聚合理念*启发。项目**不是原仓库的 fork**，不声称具有相同数量的工具，不支持 Tor 浏览，也不提供泄露凭据的访问能力。请参阅 [ATTRIBUTION.md](ATTRIBUTION.md)。

## 已实现的工具

| MCP 工具 | 功能 | 网络与密钥要求 |
| --- | --- | --- |
| `triage_indicator` | 验证和分类公网 IP、域名、HTTP(S) URL、MD5/SHA-1/SHA-256 哈希及 CVE | 离线 / 无需密钥 |
| `lookup_otx` | 获取 AlienVault OTX 中选定的指标与 pulse 元数据 | 在线 / 未配置密钥 |
| `lookup_threatfox` | 查询 ThreatFox IOC 元数据 | 在线 / `ABUSECH_AUTH_KEY` |
| `lookup_malwarebazaar` | 按文件哈希查询 MalwareBazaar **样本元数据，不下载样本** | 在线 / `ABUSECH_AUTH_KEY` |
| `lookup_urlhaus_host` | 查询 URLhaus 主机元数据 | 在线 / `ABUSECH_AUTH_KEY` |
| `lookup_cisa_kev` | 核查 CVE 是否收录于 CISA KEV 官方目录 | 在线 / 无需密钥 |
| `lookup_abuseipdb` | 查询 AbuseIPDB 中公网 IPv4 的滥用信誉 | 在线 / `ABUSEIPDB_API_KEY` |
| `correlate_evidence` | 汇总最多 50 条分析人员提供的记录并标识评估冲突 | 离线 / 无需密钥 |
| `defensive_playbook` | 提供钓鱼、勒索软件、恶意软件和凭据泄露的 SOC 检查清单 | 离线 / 无需密钥 |
| `server_status` | 显示版本及集成配置状态，**不泄露密钥内容** | 离线 / 无需密钥 |

外部集成受情报提供方的可用性、服务条款、配额和 API 更新影响。**自动化测试使用模拟 HTTP 响应，不能证明与真实外部 API 的互操作性。**

## 架构与信任边界

~~~text
Claude Code（可信的本地 MCP 客户端）
       |
       | 基于 stdin / stdout (stdio) 的 MCP JSON-RPC
       v
server.py — 仅使用 Python 3.11+ 标准库
       |                         |
       | 本地操作                | 经批准的 HTTPS 请求
       | - 指标验证              | - AlienVault OTX
       | - 证据关联              | - abuse.ch：ThreatFox / MalwareBazaar / URLhaus
       | - SOC 响应清单          | - CISA KEV / AbuseIPDB
       v                         v
        经过筛选且大小受限的结构化结果
             （外部数据不可信）
                       |
                       v
                  人工分析复核
~~~

本 MCP **不是公开托管的网络服务**，而是在分析人员自己的机器上由 MCP 客户端启动。它不能执行 shell 命令、下载恶意软件、收集密码、浏览 Tor 或修改安全控制措施。

## 安装指南：逐条解释四个命令

### 前置条件

- **Linux、macOS 或其他支持 Python 与 Claude Code CLI 的环境。** 以下示例使用 POSIX 风格的 Bash/Zsh shell，适用于 Manjaro、Ubuntu、Kali 等系统。
- **Git**：用于获取 GitHub 仓库。
- **Python 3.11 或更高版本**：用于执行 MCP 服务器与测试。本研究性 MVP 不需要额外执行 `pip install`，也不要求创建 Python 虚拟环境。
- **已安装并完成登录认证的 Claude Code CLI**：用于注册本地 MCP 服务器。仅使用浏览器里的 Claude 聊天界面是不够的。

首先检查：

~~~bash
git --version
python3 --version
claude --version
~~~

如果找不到 `claude` 命令，请参考 [Claude Code 官方安装文档](https://code.claude.com/docs/en/setup)。如果 Python 版本低于 3.11，请先升级。

### 完整的四步命令

在想要保存仓库的父目录中打开终端，执行：

~~~bash
git clone https://github.com/torsh4rk/SecOps-Studio.git
cd SecOps-Studio/torsh4rk-threat-intel-mcp

python3 -m unittest discover -s tests -v

claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

### 第 1 步：`git clone https://github.com/torsh4rk/SecOps-Studio.git`

- **`git`** 是 Git 版本控制客户端。
- **`clone`** 会复制远程仓库中的受版本管理文件及其 Git 历史到本地。
- **HTTPS 地址** 指向公开仓库 `torsh4rk/SecOps-Studio`。本 MCP 位于该仓库的子目录中，而不是单独的 Git 仓库。
- **执行结果：** 当前目录下创建一个新的 `SecOps-Studio` 文件夹。
- **注意：** 克隆代码不会安装 Claude Code、启动 MCP 或自动获取 API 密钥。如果本地已存在同名目录，应使用现有仓库并通过 Git 更新，而不是直接覆盖。

### 第 2 步：`cd SecOps-Studio/torsh4rk-threat-intel-mcp`

- **`cd`** 是 *change directory* 的缩写，用于切换当前工作目录。
- **相对路径** 指向刚才克隆的仓库中的 MCP 模块。
- **执行结果：** 终端进入包含 `server.py`、`tests/` 和文档文件的目录。
- **检查方法：** 运行 `pwd` 查看绝对路径，运行 `ls -la` 查看文件。如果提示目录不存在，请确认 `git clone` 是在哪个位置执行的。

### 第 3 步：`python3 -m unittest discover -s tests -v`

此命令执行项目的**离线单元测试**，不会访问真实的威胁情报 API。

| 命令组成部分 | 作用 |
| --- | --- |
| `python3` | 启动 Python 3 解释器 |
| `-m unittest` | 将 Python 标准库的 `unittest` 模块作为程序运行 |
| `discover` | 自动搜索符合规则的测试模块 |
| `-s tests` | 指定从本地 `tests/` 目录开始搜索 |
| `-v` | 启用详细输出，显示各个测试名称 |

**预期结果：** 共运行 12 项测试，最后显示 `OK`。失败通常意味着运行环境存在问题或代码出现回归。测试覆盖指标分类、私有/非全球可路由 IP 防护、非法输入处理、相互矛盾的证据、API 密钥检查、输出过滤和 MCP/JSON-RPC 请求分发。外部 HTTP 请求由模拟响应替代。

此命令**不会常驻运行 MCP 服务器，也不会将其注册到 Claude Code**。

### 第 4 步：`claude mcp add torsh4rk-threat-intel -- python3 "$(pwd)/server.py"`

此命令在 Claude Code 中**注册本地 MCP 服务器**。

| 命令组成部分 | 作用 |
| --- | --- |
| `claude` | Claude Code 命令行程序 |
| `mcp add` | 保存一项 MCP 服务器配置 |
| `torsh4rk-threat-intel` | 本次 MCP 连接的名称 |
| `--` | 分隔 Claude Code 参数与后面的服务器启动命令 |
| `python3` | Claude Code 连接服务器时启动的程序 |
| `"$(pwd)/server.py"` | shell 展开：把 `$(pwd)` 替换成当前目录的**绝对路径**，再附加 `/server.py` |

例如，在 `/home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp` 下执行后，保存的启动命令相当于：

~~~bash
python3 /home/analyst/SecOps-Studio/torsh4rk-threat-intel-mcp/server.py
~~~

**为什么加双引号？** 为了确保包含空格的路径被当作一个参数。**为什么使用绝对路径？** Claude Code 以后可能从不同目录启动，使用相对路径会导致找不到服务器脚本。

**配置作用域（scope）：** 不指定 `--scope` 时，Claude Code 默认采用与当前项目关联的 **local（本地）作用域**。如果希望该 MCP 在这台电脑上的**所有个人项目**中可用，请**改用**以下 user（用户）作用域命令：

~~~bash
claude mcp add --scope user torsh4rk-threat-intel -- python3 "$(pwd)/server.py"
~~~

根据实际需要选择其中一种注册方式；每个作用域只需注册一次。注册 MCP **不会创建公开的互联网服务，也不会自动发起安全调查**。

### 验证 MCP 连接

~~~bash
claude mcp list
claude mcp get torsh4rk-threat-intel
claude
~~~

进入交互式 Claude Code 会话后，输入：

~~~text
/mcp
~~~

检查 `torsh4rk-threat-intel` 的连接状态。注册后出现 `Added` 只表示配置已保存，**不代表服务器一定能够连接成功**。如需从当前作用域移除配置：

~~~bash
claude mcp remove torsh4rk-threat-intel
~~~

## 第一次安全测试

连接成功后，可以向 Claude Code 输入：

> 使用 TORSh4rk Threat Intelligence MCP，通过 `triage_indicator` 分类保留的示例域名 `example.org`；使用 `server_status` 查看状态，再返回 `phishing` 防御检查清单。不要访问任何外部情报服务。

这样可以先使用**离线工具**进行验证。实际查询 IOC 前，应确认自己获得授权、遵循数据共享策略，并了解相关提供方的当前使用条款。

### 证据关联示例

调用 `correlate_evidence` 的参数示例：

~~~json
{
  "evidence": [
    {"indicator": "example.org", "source": "SOC investigation", "assessment": "suspicious"},
    {"indicator": "example.org", "source": "Independent analyst", "assessment": "unknown"}
  ]
}
~~~

工具将整理报告并给出**建议的复核优先级**，但不会认定攻击者身份，也不能单独证明系统已被入侵。

## 可选的威胁情报 API 密钥

以下功能**不需要密钥**：`triage_indicator`、`correlate_evidence`、`defensive_playbook`、`server_status` 以及离线测试。

| 环境变量 | 适用服务 |
| --- | --- |
| `ABUSECH_AUTH_KEY` | ThreatFox、MalwareBazaar、URLhaus |
| `ABUSEIPDB_API_KEY` | AbuseIPDB |

[`.env.example`](.env.example) **仅列出环境变量名**。当前项目**不会自动读取 `.env` 文件**。请通过安全的本地环境变量注入或密钥管理机制，把真实密钥传递给 Claude Code 启动的服务器进程。不要把真实密钥写入 README、Git 提交、截图或 shell 历史。

**隐私提醒：** 在线查询会把待查指标发送给第三方，且可能同时暴露提供方账户的相关元数据。未经授权不得提交客户的保密信息。

## 常见问题排查

| 现象 | 检查方法 |
| --- | --- |
| `git: command not found` | 使用系统包管理器安装 Git |
| `cd: ... No such file or directory` | 确认克隆成功，并使用 `pwd`、`ls` 检查目录 |
| `python3: command not found` 或 Python 版本过低 | 安装 Python 3.11+，运行 `python3 --version` |
| `claude: command not found` | 根据官方指南安装 Claude Code CLI 并登录 |
| 直接运行 `python3 server.py` 后没有输出 | 这是正常现象：stdio 服务器在等待来自 stdin 的 JSON-RPC 消息。使用 Ctrl+C 退出；Claude Code 会自动启动它 |
| `claude mcp list` 显示连接失败 | 运行 `claude mcp get torsh4rk-threat-intel`，检查绝对路径、Python 版本和权限 |
| 在线查询提示缺少 API 密钥 | 为 MCP 进程配置相应环境变量；离线工具仍然可用 |
| HTTP 401/403/429 或超时 | 检查认证、用量配额、API 服务条款及可用性 |
| MCP 名称冲突或作用域不正确 | 查看 `claude mcp list`，在相应作用域移除旧配置后重新注册 |

更多信息请参阅 [Claude Code 官方 MCP 文档](https://code.claude.com/docs/en/mcp) 及交互式命令 `/mcp`、`/doctor`。

## 安全设计与局限性

- **只读：** 不提供任意 HTTP 请求、远程执行、shell 工具、Tor 浏览、凭据提取、恶意软件下载或自动化事件处置。
- **网络限制：** 仅使用固定 HTTPS 提供方地址；禁止 HTTP 重定向；超时时间 10 秒；响应大小上限 2 MB。
- **指标保护：** 不会把非全球可路由 IP 发送给外部服务；返回的元数据字段及长度受到限制。
- **不可信数据：** 第三方情报描述可能过时、错误或包含提示词注入。不能把这些文本当作系统指令，也不能仅凭 IOC 命中进行攻击归因。
- **本地信任假设：** stdio 模式假定启动者和 MCP 客户端可信。本 MVP 未提供网络身份认证、企业级 RBAC、完整审计日志、持久缓存或全面的速率限制。
- **成熟度：** 12 项离线测试仅覆盖部分行为；**尚未验证真实 API 的全部兼容性，也未完成生产安全认证**。

扩展或部署本项目之前，请阅读 [威胁模型](docs/THREAT_MODEL.md)、[安全策略](SECURITY.md) 和 [来源说明](ATTRIBUTION.md)。

## 仓库与许可证

- **仓库：** [torsh4rk/SecOps-Studio](https://github.com/torsh4rk/SecOps-Studio)
- **模块：** [torsh4rk-threat-intel-mcp](https://github.com/torsh4rk/SecOps-Studio/tree/main/torsh4rk-threat-intel-mcp)
- **许可证：** [MIT](LICENSE) © 2026 torsh4rk。
- **语言：** [English](README.md) · [Português (Brasil)](README.pt-BR.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md)

**工程原则：** *以证据调查，谨慎关联，获得授权后再行动。*
