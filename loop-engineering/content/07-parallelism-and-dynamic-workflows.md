# 07 — Parallelism, Worktrees & Dynamic Workflows

## TL;DR
- Isolation is non-negotiable once more than one agent runs: two agents on one `package.json` = zero survivors. Use `git worktree`, `--worktree`, `isolation: worktree` on subagents, or `/batch`.
- **New since the base guide:** three parallelism tiers now exist above hand-managed worktrees — **multiagent orchestration** in Managed Agents (lead + specialists on a shared filesystem, fully traceable in the Console), the **redesigned Claude Code desktop app built around parallel agents** (Apr 14, 2026), and **Dynamic Workflows** (May 28, 2026, GA): Claude writes its own orchestration scripts and runs tens to hundreds of parallel subagents with built-in verification.
- The flagship proof point: **Bun ported from Zig to Rust** via dynamic workflows — ~750,000 lines of Rust, eleven days from first commit to merge, 99.8% of the existing test suite passing.

## Tier 1: Worktrees and subagent isolation (hand-managed)

- `claude --worktree <name>` or `isolation: worktree` in subagent frontmatter; `/batch` for fan-out.
- **The classic trap:** worktrees only copy git-tracked files — `.env`, `node_modules`, and local config are missing by default. Use `.worktreeinclude`, a `WorktreeCreate` hook, or a reinstall step.
- Nuance worth keeping: Cherny himself runs ~5 local + 5–10 web sessions using a **separate `git checkout` per session**, not worktrees. Both isolation approaches are valid; worktrees are the officially recommended primitive for subagents.
- The desktop redesign (Apr 14, 2026) made parallel sessions a first-class UI concern — a signal that multi-lane operation is now the assumed default, not an expert trick.

## Tier 2: Multiagent orchestration (Managed Agents, May 2026)

When a job is too big for one agent to do well: a **lead agent** breaks it into pieces and delegates each to a **specialist with its own model, prompt, and tools** (e.g., an incident investigation fanning out through deploy history, error logs, metrics, and support tickets).

- Specialists work in parallel on a **shared filesystem** and feed the lead agent's context; events are persistent, so the lead can check back in mid-workflow.
- **Full tracing in the Claude Console**: which agent did what, in what order, and why — the observability answer to "how do I trust a fan-out I didn't watch?"
- Model-mixing is a cost lever: **Spiral** runs a Haiku lead (triage, follow-up questions) delegating drafting to Opus subagents. **Netflix's platform team** batches log analysis across hundreds of builds in parallel and surfaces only recurring patterns.

## Tier 3: Dynamic Workflows (Claude Code, GA)

The largest change to the parallelism landscape since the base guide:

- **What it is:** Claude plans from your prompt, writes orchestration scripts, fans work across **tens to hundreds of parallel subagents**, checks results before folding them in, and returns one coordinated answer. Agents attack the problem from independent angles; **adversarial agents try to refute findings**; the run iterates until answers converge.
- **Built for long-running work** — hours to days. Progress is saved as it goes; interrupted jobs resume rather than restart. Coordination happens *outside* the conversation, so the plan holds regardless of task size.
- **How to invoke:** turn on auto mode, then either ask for a workflow directly ("Create a workflow") or enable the `ultracode` setting (effort → xhigh; Claude decides when a workflow is warranted). On by default for Max/Team/Enterprise and the API; Pro enables in `/config`; admins can disable via managed settings. First trigger shows what's about to run and asks you to confirm.
- **Sweet-spot use cases:** codebase-wide bug hunts and security audits (parallel search + independent verification of every finding), large migrations/framework swaps/language ports spanning thousands of files, and critical work you need checked twice. Klarna reports it surfacing dead code and cleanup opportunities that static analysis missed.
- **Cost warning is explicit:** workflows consume substantially more tokens than a typical session — start on a scoped task.

### Case study: the Bun rewrite

Jarred Sumner's port of Bun from Zig to Rust is the canonical dynamic-workflows loop, and it decomposes exactly into this series' architecture:

1. One workflow mapped the correct Rust lifetime for every struct field in the Zig codebase (**analysis loop**).
2. The next wrote every `.rs` file as a behavior-identical port of its `.zig` counterpart — hundreds of agents in parallel, **two reviewers on each file** (maker + checkers).
3. A **fix loop** drove the build and test suite until both ran clean (machine-checkable finish line).
4. An overnight workflow then addressed unnecessary data copies and **opened a PR for each** for final review (human in the review seat).

Result: ~750k lines, 11 days, 99.8% test-suite pass — and, notably, *not yet in production*, which is itself the lesson: even at this scale, the loop proposes and humans decide.

## Choosing your tier

| Situation | Tier |
|---|---|
| 2–5 concurrent lanes you'll watch | Worktrees / checkouts (Tier 1) |
| Deployed, shared, cross-system job with tracing needs | Multiagent orchestration (Tier 2) |
| Huge, verifiable, bounded task (audit, migration, port) | Dynamic Workflows (Tier 3) |
| Token-constrained | Stay single-agent — multi-agent runs ~15× chat token usage (Anthropic engineering data) |

## Sources
- Anthropic, "Introducing dynamic workflows in Claude Code" (May 28, 2026)
- Anthropic, "New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration" (May 2026)
- Anthropic, "Redesigning Claude Code on desktop for parallel agents" (Apr 14, 2026)
- Anthropic, "How we built our multi-agent research system"
- Claude Code docs (worktrees, subagents, `/batch`)

→ Next: [08 — Safety, Cost & Security](08-safety-cost-security.md)
