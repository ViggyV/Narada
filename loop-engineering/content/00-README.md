# Loop Engineering Series

A practical, source-grounded series on **loop engineering** with Claude Code and the Claude Platform — the shift from writing one-shot prompts to designing self-running systems that prompt the agent for you.

> Loop engineering = you design the system that finds work, hands it out, verifies it, records progress, and decides the next step — then let it run on a trigger.
> — concept named by Addy Osmani (June 2026), crystallizing statements by Boris Cherny (Claude Code) and Peter Steinberger (OpenClaw)

## The series

| # | File | What it covers |
|---|------|----------------|
| 01 | [What Is Loop Engineering](01-what-is-loop-engineering.md) | The concept, origin, why now, and the corrected attribution |
| 02 | [Anatomy of a Loop](02-anatomy-of-a-loop.md) | The unified six-component architecture + the harness lens |
| 03 | [Triggers & Schedulers](03-triggers.md) | `/loop`, Routines, scheduled tasks, GitHub Actions, Managed Agents schedules |
| 04 | [Skills-First Discipline & Harness Design](04-skills-and-harness-design.md) | Skills, progressive disclosure, and Anthropic's three harness patterns |
| 05 | [Verification: Maker vs. Checker](05-verification.md) | `/goal`, Outcomes graders, self-preference bias, binary rubrics |
| 06 | [Memory & State](06-memory.md) | CLAUDE.md, memory folders, compaction, and Dreaming |
| 07 | [Parallelism, Worktrees & Dynamic Workflows](07-parallelism-and-dynamic-workflows.md) | Isolation lanes, subagents, multiagent orchestration, 100-agent workflows |
| 08 | [Safety, Cost & Security](08-safety-cost-security.md) | Stop rules, token economics, MCP attack surface, harness boundaries |
| 09 | [The Implementation Playbook](09-playbook.md) | Go/no-go test, step-by-step build, anti-patterns, graduation benchmarks |

## What's new in this edition (claude.com/blog review, Feb–Jul 2026)

This series updates the base "Definitive Best-Practices Guide" with material published on claude.com/blog in the last five months:

1. **Routines in Claude Code** (Apr 14, 2026) — `/schedule` now creates cloud Routines that run on Anthropic infrastructure with your machine off. The "trigger" building block is officially productized. → File 03
2. **Agent Harness Design: 3 Patterns** (Apr 2, 2026) — Anthropic's own framing of the loop-around-the-model: use what Claude knows (bash + text editor), strip the harness down ("what can I stop doing?"), and set boundaries carefully (cache design, declarative tools). Includes hard numbers: code-execution orchestration lifted Opus 4.6 BrowseComp accuracy from 45.3% to 61.6%. → Files 02, 04, 08
3. **Claude Managed Agents** (Apr 8 → Jun 9, 2026) — the maker/checker and memory patterns are now first-class platform features:
   - **Outcomes**: a rubric-driven separate grader in its own context window; up to +10 points task success vs. a standard prompting loop. → File 05
   - **Dreaming** (research preview): a scheduled process that reviews sessions and curates memory between runs — a self-improvement loop on top of your loops. Harvey reported ~6× completion-rate improvement in their tests. → File 06
   - **Multiagent orchestration**, **webhooks**, **schedules + vaults**, **self-hosted sandboxes and MCP tunnels**. → Files 03, 07, 08
4. **Dynamic Workflows in Claude Code** (May 28, 2026; now GA) — Claude writes its own orchestration scripts and fans work across tens to hundreds of parallel subagents, with independent verification and adversarial "refuter" agents before results reach you. Flagship case: Bun ported from Zig to Rust (~750k lines, 11 days, 99.8% of the test suite passing). → File 07
5. **Choosing a Claude model and effort level in Claude Code** (Jul 7, 2026) — model/effort selection is now a loop-design decision (e.g., cheap fast evaluators, `ultracode`/xhigh effort for workflow-scale tasks). → Files 05, 07
6. **Operational evidence** — Anthropic's own large-scale code migrations post (Jul 16), overnight-agent case studies (Cognition Jul 10, Rakuten Jul 20), and the CISO's guide to agentic AI (Jul 17) all reinforce the series' verification-first, least-privilege stance. → Files 08, 09

## Primary sources used across the series

- Osmani, A. "Loop Engineering." June 7, 2026; republished O'Reilly Radar June 22, 2026.
- Anthropic, claude.com/blog: Agent Harness Design (Apr 2); Claude Managed Agents series (Apr 8, Apr 23, May 19 ×2, Jun 9); Routines (Apr 14); Dynamic Workflows (May 28); Model & effort levels (Jul 7); AI code migration (Jul 16); CISO guide (Jul 17).
- Anthropic. "Building Effective Agents"; "How we built our multi-agent research system"; Claude Code docs (code.claude.com/docs).
- "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems." arXiv:2604.14228, Apr 16, 2026.
- Anthropic. "Agent SDK Overview." code.claude.com/docs/en/agent-sdk/overview, Apr 30, 2026.
- Crosley, B. "Claude Code CLI: The Complete Guide — Hooks, MCP, Skills." Jun 8, 2026 (v2.1.169).
- AntStack. "Claude Agents, Subagents, Agent Teams, Skills & MCP: A Developer's Field Guide." Mar 9, 2026.
- McNamara, C. "Understanding Skills, Agents, Subagents, and MCP in Claude Code." Oct 18, 2025.
- Smith Horn Group. "Choosing between skills, subagents, and MCP servers in Claude Code." Dec 3, 2025.
- Totalum. "Claude Agent SDK in 2026: What It Is, When To Use It." Jun 2026.
- Panickssery, Bowman & Feng. "LLM Evaluators Recognize and Favor Their Own Generations." NeurIPS 2024 (Oral).

*Version note: Claude Code ships fast. Feature specifics cited here reflect roughly v2.1.139–v2.1.169+ and mid-2026 platform docs. Verify exact flags against current docs before relying on them.*
