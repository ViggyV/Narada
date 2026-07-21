# 06 — Memory & State

## TL;DR
- **The agent forgets; the repo doesn't** (Osmani). No memory file = no improvement = re-paying for the same issues every run. Memory lives on disk (or Linear/Jira), never in the chat.
- Anthropic ships a layered memory system: CLAUDE.md (conventions), auto-memory/MEMORY.md (learned patterns), the memory tool/folder (agent-chosen persistence), compaction (in-context continuity), and — **new** — **Dreaming** (Managed Agents, research preview): a scheduled process that curates memory *between* sessions.
- Harness-design evidence says memory investment compounds: the same memory-folder setup that barely helped older models lifted newer ones dramatically (compaction benchmark: 43% flat → 84%).

## The memory layers, loop by loop

| Layer | What it holds | Written by | Loop role |
|---|---|---|---|
| **CLAUDE.md** | Always-true conventions, documented mistakes (~2–3k tokens, git-tracked) | Humans + team | Constitution |
| **Auto-memory / MEMORY.md** | Learned patterns accumulated across sessions | Claude | Habits |
| **progress.md / state file** | What was tried, what passed, what's open, per loop | The loop, each run | Working notebook |
| **Memory tool / folder** | Agent-chosen notes and structured files | Claude, mid-task | Long-horizon continuity |
| **External trackers (Linear/Jira via MCP)** | Cross-team visible state | Connectors | Shared ledger |
| **Dreaming** | Curated, restructured memory distilled from past sessions | Scheduled platform process | Self-improvement |

## The state file: minimum viable loop memory

Anthropic's guidance is disarmingly simple: provide a place to write notes — as simple as a markdown file. The loop reads it at the start of each run and writes what it tried, what passed, and what's still open. Two hard requirements:

1. **Idempotency guards.** e.g., "if a PR labeled `claude-sweep` already exists this week, exit." Re-runs must not duplicate work — this is the most common silent cost sink.
2. **Committed, not local.** Cloud Routines start from a fresh clone; memory that isn't in the repo doesn't exist.

## What good agent memory looks like (harness-design evidence)

Anthropic's Pokémon long-horizon example is the clearest illustration of memory quality evolving:

- Sonnet 3.5 treated memory as a transcript — 31 files after 14,000 steps, including near-duplicate trivia notes, still stuck in the second town.
- Opus 4.6 at the same step count: 10 files in organized directories, three gym badges, and a `learnings.md` distilled from its own failures (tactical rules, confirmed dead-ends, bag-limit workarounds).

**Design your loop's memory format for the second kind:** distilled learnings and confirmed facts, not event logs. Compaction and memory-folder benchmarks (43%→84%; 60.4%→67.2%) show the payoff grows with each model generation — memory is the loop component that appreciates.

## Dreaming: a loop that improves your loops (May 2026, research preview)

Dreaming extends memory with a scheduled review process: it reads past agent sessions and memory stores, extracts patterns a single agent can't see (recurring mistakes, workflows agents converge on, preferences shared across a team), and **restructures memory so it stays high-signal**. Two governance modes: fully automatic, or review-before-changes-land — for unattended production loops, start with review mode.

- Together with memory it forms a two-tempo system: memory captures what each agent learns *as it works*; dreaming refines it *between sessions* and pools learnings across agents.
- Field result: **Harvey** (legal AI) reported completion rates up **~6×** in their tests once agents remembered filetype workarounds and tool-specific patterns between sessions.
- Loop-engineering framing: dreaming is a *meta-loop* — trigger (schedule) + work (pattern extraction) + verification (your review gate) + memory (the memory store itself). The same go/no-go and guardrail discipline applies.

## Memory anti-patterns

- **Never keep state in the chat.** Context is ephemeral by design; `/compact` trims it, sessions end.
- **Never let memory grow as an append-only log.** Un-curated memory decays into the Sonnet-3.5 Pokémon transcript. Either schedule dreaming/curation or have the loop itself rewrite (not just append) its state file.
- **Never store secrets in memory files.** Secrets go in vaults (Managed Agents) or your secret manager — memory files get committed and read broadly.

## Sources
- Osmani (Jun 2026)
- Anthropic, "Built-in memory for Claude Managed Agents" (Apr 23, 2026); "New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration" (May 2026)
- Anthropic, "Agent Harness Design: 3 Patterns" (Apr 2, 2026) — compaction/memory-folder benchmarks and Pokémon example
- Claude memory tool docs; Claude Code docs

→ Next: [07 — Parallelism, Worktrees & Dynamic Workflows](07-parallelism-and-dynamic-workflows.md)
