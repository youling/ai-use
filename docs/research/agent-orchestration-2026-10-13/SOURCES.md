# Evidence Register — 2026-10-13 Agent Collaboration & Magpie

**Classification: NON-NORMATIVE RESEARCH / L3.** Links are public source pointers, not automatic validation. `UPSTREAM_DOCUMENTED` is a claim by vendor/maintainer, not a local demonstration. Versioned source names preserve attribution; URL freshness can drift.

| ID | Primary URL (public) | Evidence / date | Supports / does not support |
| --- | --- | --- | --- |
| S01 | [OpenAI Codex App](https://openai.com/index/introducing-the-codex-app/) | OpenAI 2026-02-02; 2026-03 Windows update | Human supervising parallel project agents/threads and worktrees; not our local executor qualification |
| S02 | [OpenAI Agents API — Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) | current developer docs, queried 2026-10-13 | Child context, coordination, permission/capability caveats; note child filesystem may be shared |
| S03 | [OpenAI Responses Multi-agent beta](https://developers.openai.com/api/docs/guides/responses-multi-agent) | current developer beta, queried 2026-10-13 | Parallel tree delegation and cost/limit tradeoffs; nested capability != ai-use authority |
| S04 | [OpenAI dots](https://openai.com/index/introducing-dots/) | OpenAI 2026-09-29 | Read-only proactive research, cloud isolation, custom permissions, review and approval; product claims only |
| S05 | [OpenAI × Atlassian Teamwork Graph](https://openai.com/index/atlassian-partnership/) | 2026-10-06 | People/project/document/decision context graph with Jira/Confluence existing truth |
| S06 | [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) | 2025-06-13 | Orchestrator-worker, parallel bounded subresearch, evaluator/bottlenecks, internal benchmark limitations |
| S07 | [Anthropic Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 2025-11-26 | Initializer + coding shifts with durable artifacts for cross-context continuation |
| S08 | [Anthropic Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 2026-03-24 | Planner/generator/evaluator loops; model-dependent context approach |
| S09 | [Anthropic Parallel Compiler](https://www.anthropic.com/engineering/building-c-compiler) | 2026-02-05 | Many agents, measurable end artifact, substantial cost; experiment not blanket deployment/safety guidance |
| S10 | [Google ADK cross-language A2A](https://developers.googleblog.com/build-cross-language-multi-agent-team-with-google-agent-development-kit-and-a2a/) | 2026-06-22 | Opaque cross-language agents + validation as separate deterministic component |
| S11 | [A2A Protocol](https://a2a-protocol.org/latest/topics/key-concepts/) | current spec docs, queried 2026-10-13 | AgentCard/Task/Message/Artifact and async lifecycle; not GitHub Work authority |
| S12 | [Microsoft Agent Framework orchestrations](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/) | docs updated 2026-08-25 | Sequential/concurrent/handoff/groupchat/magentic patterns |
| S13 | [Microsoft HITL](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) / [Agent 365 registry](https://learn.microsoft.com/entra/agent-id/identity-platform/agent-registry-convergence) | current Microsoft docs | Checkpoints + approval requests; separate enterprise agent identity/governance |
| S14 | [Temporal durable agent workflow](https://temporal.io/blog/build-durable-ai-agents-pydantic-ai-and-temporal) | current reference design, 2025-11 | Retry, persisted workflows, external signals and human approval; no mandatory adoption |
| S15 | [DeepMind Gemini Deep Think / Aletheia](https://deepmind.google/blog/accelerating-mathematical-and-scientific-discovery-with-gemini-deep-think/) | 2026-02-11 | Math hypothesis → natural-language verifier → revise; claims explicitly bounded by significance |
| S16 | [DeepMind AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) | 2025-05; also [2026 follow-up](https://deepmind.google/blog/alphaevolve-impact/) | Program search + automated evaluation on algorithm/mathematical optimization |
| S17 | [OpenAI First Proof submissions](https://openai.com/index/first-proof-submissions/) | 2026-02-20 | Explicitly documented correction after expert/community review; human-in-loop eval limits |
| S18 | [OpenAI Ten mathematical advances](https://openai.com/zh-Hans-CN/index/ten-advances-in-mathematics/) | 2026-08-01 | Vendor-reported research claims, Lean formalization and human authorship statement |
| S19 | [OpenAI Navier–Stokes proof announcement](https://openai.com/index/navier-stokes-solution/) | 2026-09-08 | Vendor claim + Lean; do not call universally/independently settled from author alone |
| S20 | [OpenAI bulk math publication](https://openai.com/index/sharing-ai-progress-in-mathematics/) | 2026-10-06 | Published GitHub results, some formalizations and further revision process |
| S21 | [External caveat on formal/human proof gap](https://techcrunch.com/2026/10/08/openais-math-solutions-arent-meeting-the-fields-standards-yet/) | independent reporting, 2026-10-08 | Commentary on proof presentation and formal statement gap; not authoritative proof audit |
| S22 | [Magpie README](https://github.com/yetone/magpie/blob/113672508a54da80b11523544b1bba75a4e02948/README.md) / [Integrating](https://github.com/yetone/magpie/blob/113672508a54da80b11523544b1bba75a4e02948/docs/integrating.md) / [Reference](https://github.com/yetone/magpie/blob/113672508a54da80b11523544b1bba75a4e02948/docs/reference.md) | `yetone/magpie@113672508a54da80b11523544b1bba75a4e02948`; upstream 2026-10-13 | API endpoints, CLI/providers/plugins, loopback permissive auth; upstream documented not locally reproduced |
| S23 | [CC Switch](https://github.com/farion1231/cc-switch) | current upstream README, 2026-10-13 | Competing provider config/routing; explicitly warns subscriptions may conflict with vendor terms |
| S24 | [LiteLLM proxy architecture](https://docs.litellm.ai/docs/proxy/architecture) / [virtual keys](https://docs.litellm.ai/docs/proxy/virtual_keys) | current upstream docs | Official API provider proxy with key budgets/DB/Redis, retries/fallback and access policy |
| S25 | [New API gateway](https://github.com/QuantumNous/new-api/blob/main/README.en.md) | current upstream README | Authorized upstream API gateway alternative; does not prove our suitability |

## Cross-check categories

- **Vendor documentary claim**: S01–S20, S22–S25. Neither endorsement nor local runtime proof.
- **Independent community challenge**: S21. Useful to design counterexamples; confirm contested technical claims with mathematics community/actual formal scripts before stronger statements.
- **Local execution qualification**: **none in this research**. Existing [ai-use PR #150](https://github.com/youling/ai-use/pull/150) is separately labeled `QUALIFIED_SYNTHETIC_ONLY`, not an independent Magpie test.
- **Exact upstream Magpie snapshot**: Git ref above captures repository state when reviewed. Credentials, user accounts, deployed configuration, provider terms and quotas are intentionally not collected here.

## Follow-up source prioritization

If this research is revisited after a provider API, license, model, tool contract, security posture or accepted Work architecture changed, reread relevant **upstream official spec/docs at exact version**; compare against current project facts. No arbitrary weekly full-rescan or model ranking. Study missing coverage only where it would change the decision.
