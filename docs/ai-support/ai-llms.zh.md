# AI / LLMs

TronLink 的开发者文档以机器可读形式发布，便于 AI 智能体和基于 LLM 的工具直接发现、读取与集成。

!!! info "允许的用途 vs. 爬虫策略"
    本站为 **retrieval / RAG / inference-time grounding** 整理——下方的 `llms.txt` 与 `llms-full.txt` 全文包是这种用途的规范入口,且明确为 AI 使用而维护。

    **训练时批量抓取**是另一个问题,由本站的 `robots.txt` 加上边缘下发的 `Content-Signal` 指令控制。目前部分仅用于训练的 user-agent 被显式 Disallow;如果你的场景需要不同的策略,请联系我们,而不是通过解析全文包绕开信号。

## 可用端点

> **URL ≠ 源文件名。** 源文件带 `.en` / `.zh` 后缀（`llms.zh.txt`、`llms-full.en.txt`、`llms-full.zh.txt`），mkdocs 的 i18n 插件靠这个后缀来分流；**部署后后缀会被剥掉**，中文版本搬到 `/zh/` 下。请使用下表中的部署 URL；带语言后缀的源文件名 URL（如 `/llms-full.en.txt`）会 404。

| 端点（部署 URL） | 说明 |
| --- | --- |
| [/llms.txt](../../../llms.txt) | 英文版精选索引（[llmstxt.org](https://llmstxt.org/) 规范） |
| [/zh/llms.txt](../../llms.txt) | 中文版精选索引——同样版式，链接指向 `/zh/` 下的中文页面 |
| [/llms-full.txt](../../../llms-full.txt) | 所有英文页面全文聚合，便于单次抓取（由 `docs/llms-full.en.txt` 构建） |
| [/zh/llms-full.txt](../../llms-full.txt) | 所有中文页面全文聚合，便于单次抓取（由 `docs/llms-full.zh.txt` 构建） |
| [/reference/mcp-tools.json](../../../reference/mcp-tools.json) | 机器可读的 MCP 工具契约静态快照——name、description、`inputSchema`、annotations，经 `tools/list` 从 npm 已发布 server 抓取 |
| [/AGENTS.txt](https://docs.tronlink.org/AGENTS.txt) | AI 智能体定向文件——入口、主题地图、SSOT 边界（镜像于 `/AGENTS.md` 与 `/CLAUDE.md`） |
| [/.well-known/security.txt](https://docs.tronlink.org/.well-known/security.txt) | RFC 9116 漏洞披露指针（同时在 `/security.txt` 提供） |

生产地址：`https://docs.tronlink.org/llms.txt`、`https://docs.tronlink.org/zh/llms.txt`，以及对应的 `/llms-full.txt` 全文聚合。

## 该用哪个文件？

| 场景 | URL |
| --- | --- |
| 导航 / 找到正确的英文页面 | `/llms.txt` —— 简短的纯链接地图 |
| 导航 / 找到正确的中文页面 | `/zh/llms.txt` —— 中文描述、同样版式 |
| 一次抓取整份英文文档 | `/llms-full.txt` |
| 一次抓取整份中文文档 | `/zh/llms-full.txt` |
| 不启动 server 就读取完整 MCP 工具契约 | `/reference/mcp-tools.json`——静态快照；运行中 server 的 `tools/list` 仍是 SSOT |

请先用对应语言的索引并跟随其链接；需要一次性获取全部内容时再抓全文包。中文索引指向 `/zh/` 下的页面，英文索引指向根目录下的页面。

## 添加到你的 AI 工具

- **Cursor** —— Settings → Features → Docs → *Add new doc*,粘贴 `https://docs.tronlink.org/llms.txt`。
- **Claude / 支持 MCP 的智能体** —— TronLink 提供 MCP 服务以实现实时钱包与链上访问,host 配置见 [MCP Server TronLink](mcp-server-tronlink.md) 与 [MCP TronLink Signer](mcp-tronlink-signer.md)。仅作文档上下文时,把工具指向上面的 `llms.txt` 地址即可。
- **其他工具** —— 任何支持自定义文档 URL 的工具都可使用 `llms.txt` / `llms-full.txt` 端点。

## 覆盖范围

该聚合覆盖完整文档,包括 AI/智能体工具链：

- [MCP Server TronLink](mcp-server-tronlink.md) —— 链上、多签、GasFree 工具（Playwright + Direct API）
- [TronLink MCP Core](tronlink-mcp-core.md) —— 框架库：schema、工具定义、流程配方
- [TronLink Skills](tronlink-skills.md) —— 只读智能体技能集（钱包、代币、行情、兑换、资源、质押）
- [MCP TronLink Signer](mcp-tronlink-signer.md) —— 封装签名 SDK 的 MCP 服务
- [TronLink Signer](tronlink-signer.md) —— 独立签名 SDK
- [TronLink CLI](tronlink-cli.md) —— 命令行工具

以及 DApp 集成、移动端（DeepLink）和参考（网络、术语表、FAQ）章节。

## 给智能体的说明

- 从 `llms.txt` 开始——它是权威地图。不要盲目枚举站点文件。
- 工具调用请基于结构化的 `error.code` / `error.retryable` 分支,**不要**解析人类可读的 `message`。
- 读操作可安全重试;签名 / 远程写操作需要用户审批（HITL）,且不得自动重试——见各工具的「安全」一节。
- 实验时默认用测试网（`nile` / `shasta`）;只有动用真实资金时才用 `mainnet`。
