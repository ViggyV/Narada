# 08 — Safety, Cost & Security

## TL;DR
- The hard part of loop engineering is not autonomy — it's **stop conditions, cost control, and the connector attack surface**.
- Token economics are asymmetric and documented: agents use ~4× chat tokens, multi-agent systems ~15× (Anthropic engineering data); Steinberger's documented extreme was $1,305,088.81 in one month of API spend (~$300K with Fast Mode off). Dynamic workflows carry an explicit "substantially more tokens" warning from Anthropic itself.
- **New since the base guide:** Anthropic's CISO-facing posts (Apr 10 and Jul 17, 2026) reframe the security posture — the goal isn't zero risk, it's risk you've *chosen*, bounded, and can observe. Managed Agents' self-hosted sandboxes, MCP tunnels, and vaults (May–Jun 2026) are the platform's answer for keeping loops inside your perimeter.

## Stop rules & termination (non-negotiable)

- Hard iteration/turn cap in every goal (`or stop after N turns`) **plus** a wall-clock or dollar ceiling. Runaway loops (an agent hammering a broken tool) are a documented production failure mode.
- `/goal` has **no built-in token budget** — the bound lives in your condition. Interrupt: Ctrl+C or `/goal clear`.
- **Escalate, don't spin:** on a blocker, describe the problem, write it to the triage inbox, exit.
- Dynamic workflows: keep the first-run confirmation on; org admins can disable workflows entirely via managed settings if review bandwidth can't keep up.

## Cost controls

- Budget upfront against the 4×/15× multipliers. `/cost` to monitor; `/compact` to trim history.
- **Idempotency guards** (File 06) prevent the most common silent sink: re-doing completed work each trigger fire.
- Cloud Routines draw down subscription limits with per-plan daily caps — start daily-frequency, scale after observing.
- **Model/effort as a cost dial** (Anthropic, Jul 7, 2026): Haiku-class evaluators for frequent binary gates; reserve high effort (`ultracode`/xhigh) for workflow-scale tasks; don't switch models mid-session (it breaks prompt caches — cached tokens are ~10% the cost of base input). Cache design principles from the harness post: static content first, appended `<system-reminder>` messages instead of prompt edits, tool-list stability, breakpoint updates.
- Spend subagents only where a second opinion is worth paying for.

## Security: the connector attack surface

2026's documented MCP security crisis — indirect **prompt injection** (malicious instructions hidden in issues, docs, tool output), **over-permissioned connectors** enabling exfiltration, and **supply-chain/tool-poisoning** attacks — makes an unattended loop with write-capable connectors an unattended attack surface. Gravitee's "State of AI Agent Security 2026" (900+ respondents) found 88% of organizations reporting confirmed or suspected AI-agent security incidents in the past year (92.7% in healthcare).

Controls, in priority order:

1. **Least privilege.** Scope connectors minimally; `--allowedTools` (e.g., read-only `Read,Grep,Glob`) for analysis loops; enable specific safe bash commands via `/permissions` rather than `--dangerously-skip-permissions` (Cherny: never outside a sandbox).
2. **Treat everything the loop reads as untrusted input** — tickets, PRs, web pages, tool output.
3. **Keep the `claude/` branch guardrail on** for Routines; the loop proposes, humans merge.
4. **Declarative tools at security boundaries** (harness pattern #3): promote hard-to-reverse actions to dedicated, typed, gateable, auditable tools instead of raw bash strings; add staleness checks to write tools; log all tool invocations. Auto-mode's second-Claude command review can reduce the need for dedicated tools — but only for tasks where you trust the general direction.
5. **Perimeter options for organizations** (Managed Agents, May–Jun 2026): **self-hosted sandboxes** keep execution inside your infrastructure; **MCP tunnels** reach internal systems without exposing them publicly; **vaults** keep secrets out of prompts, memory files, and repos.
6. **Adopt the CISO framing** (Anthropic, Jul 17, 2026): zero risk isn't the job — enumerate what the loop can touch, bound the blast radius, instrument everything, and make the residual risk an explicit, reviewed decision.

## Comprehension debt

The faster the loop ships code you didn't write, the wider the gap between the codebase and your understanding (Karpathy/Osmani). Anthropic's own large-scale migration write-up (Jul 16, 2026) and the Bun rewrite share the same discipline: massive automation, but every change lands as a reviewable PR. Read what the loop produces. Two people can build the same loop and get opposite results — one moves faster on work they understand; the other stops understanding the work.

## Sources
- Anthropic, "Zero risk isn't the job: a CISO's guide to agentic AI" (Jul 17, 2026); "Preparing your security program for AI-accelerated offense" (Apr 10, 2026)
- Anthropic, "New in Claude Managed Agents: self-hosted sandboxes and MCP tunnels" (May 19, 2026); schedules & vaults (Jun 9, 2026)
- Anthropic, "Agent Harness Design" (Apr 2, 2026) — cache principles, declarative tools, auto-mode
- Anthropic, "How Anthropic runs large-scale code migrations with Claude Code" (Jul 16, 2026)
- Gravitee, "State of AI Agent Security 2026"; Tom's Hardware / The Next Web (Steinberger spend, May 2026)

→ Next: [09 — The Implementation Playbook](09-playbook.md)
