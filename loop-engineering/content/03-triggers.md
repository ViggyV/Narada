# 03 — Triggers & Schedulers

## TL;DR
- Four trigger tiers, by durability: **in-session** (`/loop`), **local persistent** (Desktop scheduled tasks), **cloud** (Routines via `/schedule`), and **infrastructure-native** (GitHub Actions, Agent SDK, Managed Agents schedules).
- **New since the base guide:** Routines were formally announced on claude.com/blog (Apr 14, 2026), and Claude Managed Agents gained platform-level schedules plus environment-variable vaults (Jun 9, 2026) — so fully-hosted loops no longer require Claude Code at all.
- Pick the *least durable* trigger that satisfies the job. Durability you don't need is unattended risk you don't need.

## The trigger ladder

| Tier | Mechanism | Min interval | Survives laptop closed? | Notes |
|---|---|---|---|---|
| 1. In-session | `/loop 15m <prompt or /skill>` | interval-based | No | Session-scoped: fires only while Claude Code is running and idle; a fresh conversation clears it; no catch-up for missed fires |
| 2. Local persistent | Desktop scheduled task | 1 min | No (machine must be awake) | v2.1.72+ |
| 3. Cloud | `/schedule` → **Routine** | 1 hour | **Yes** | Runs on Anthropic infra; fresh repo clone each run; pushes to `claude/`-prefixed branches by default; daily caps by plan (Pro ~5, Max ~15, Team/Enterprise ~25) |
| 4. Infra-native | GitHub Actions `schedule` + `anthropics/claude-code-action@v1` or headless `claude -p`; **Managed Agents schedules** | your CI's | Yes | Best for CI-coupled loops and org-owned deployments |

## Routines (Apr 14, 2026 — now the canonical cloud trigger)

The `/schedule` command in the CLI creates a cloud Routine. Practical implications for loop design:

- **Fresh clone each run** → your loop must bootstrap from the repo alone. Anything it needs (skills, memory files, checker agents) must be *committed*: `.claude/skills/`, `.claude/agents/`, CLAUDE.md, progress files.
- **`claude/` branch prefix** is a built-in guardrail — keep it. The loop proposes; humans merge.
- **Subscription draw-down + per-plan caps** → start daily, observe usage, then increase frequency.

## Managed Agents schedules + vaults (Jun 9, 2026)

For loops that outgrow a repo — cross-system business workflows, agents your team shares — Claude Managed Agents now supports running agents **on a schedule** with secrets stored in **vaults**, plus **webhooks** to notify you when an outcome-gated run completes (May 2026). Combined with self-hosted sandboxes and MCP tunnels (May 19, 2026), this is the "tier 4" trigger for organizations: the loop lives on the platform, not on anyone's laptop, with Console-level tracing of every step.

**Rule of thumb:** repo-shaped work → Routines; org-shaped work → Managed Agents.

## The orchestration-skill pattern (author's preferred trigger)

A scheduled task or Routine's prompt can invoke a skill or slash command (e.g., `/loop /review-pr 1234`), so a single **orchestration skill** can carry the goal, completion condition, and verification settings in one versioned artifact. Confirmed viable and recommended: it keeps trigger configuration thin and puts the actual loop logic in git where the checker can see it too.

## Trigger anti-patterns

- **Don't** use a cloud Routine for something `/loop` can do while you're at the desk — you lose the ability to watch it in training mode.
- **Don't** schedule without idempotency guards (see File 06); a re-fired trigger that re-does completed work is the most common silent cost sink.
- **Don't** let a trigger imply permission. The trigger decides *when*; permissions (`/permissions`, `--allowedTools`, vault scoping) decide *what*.

## Sources
- Anthropic, "Introducing routines in Claude Code" (claude.com/blog, Apr 14, 2026)
- Anthropic, "New in Claude Managed Agents: run agents on a schedule and store environment variables in vaults" (Jun 9, 2026)
- Anthropic, "New in Claude Managed Agents: self-hosted sandboxes and MCP tunnels" (May 19, 2026)
- Claude Code docs (code.claude.com/docs); Crosley, complete guide (Jun 2026)

→ Next: [04 — Skills-First Discipline & Harness Design](04-skills-and-harness-design.md)
