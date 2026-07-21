# 09 — The Implementation Playbook

## TL;DR
- Nine steps, front-loading verification: go/no-go test → prove the skill → build the checker → write the goal → add memory → add isolation → attach the trigger → training mode → graduate autonomy.
- **Updated for 2026 platform features:** the ladder now has explicit graduation points into Outcomes, Dreaming, and Dynamic Workflows — each of which you earn, not enable on day one.
- Benchmarks to graduate: 3 consecutive zero-correction supervised runs (weekly), one week of stable unattended operation with no runaway costs and no bad merges (monthly).

## Step 0 — The four-condition go/no-go test

Build a loop only if **all** are true:

1. **Does the task repeat?** One-off → just prompt.
2. **Is there a clear definition of done *and* a way to verify it?** Not machine-checkable → don't loop yet, or break it into checkpoints.
3. **Can you afford to be wasteful with tokens?** Loops trade tokens for your time (4×/15× multipliers; workflows more).
4. **Does the loop have every tool it needs to complete *and* verify the task?**

Good first candidates (boring, bounded, verifiable): failing-test fixes, lint/type cleanup, dependency-audit sweeps, dead-link checks, changelog generation, stale-branch cleanup, CI-failure triage.

## The build sequence

**Step 1 — Prove the execution skill(s).** Do it manually with Claude 3–5 times; capture as `.claude/skills/<name>/SKILL.md` with a tight trigger-oriented description, <~500 lines, verification command baked in. *No loop without a battle-tested skill behind it.*

**Step 2 — Build a separate checker.** Checker subagent in `.claude/agents/` with different instructions and ideally a different model family. Binary rubric ("Does every changed file have a passing test? yes/no"). Target ~1 validator per 4 work skills. *(2026 upgrade path: when the loop deploys as a Managed Agent, this rubric becomes your **Outcome**.)*

**Step 3 — Write the orchestration skill with a verifiable goal.**
```
/goal all tests in test/auth pass and lint is clean, or stop after 15 turns
```
Pair with auto mode. The evaluator only sees the transcript — make the skill *surface its proof* (print test output, exit codes).

**Step 4 — Give it a memory file.** `progress.md` read at start, written at end: tried / passed / open. Idempotency guards ("if a PR labeled `claude-sweep` exists this week, exit"). CLAUDE.md for conventions; commit everything — Routines clone fresh. *(2026 upgrade path: once several loops share learnings, turn on **Dreaming** in review mode.)*

**Step 5 — Add isolation if parallel.** `isolation: worktree` in subagent frontmatter or `claude --worktree <name>`. Mind the worktree trap: only git-tracked files come along — handle `.env`/`node_modules` via `.worktreeinclude` or a `WorktreeCreate` hook.

**Step 6 — Attach the trigger** (least durable that satisfies the job): `/loop` (in-session) → Desktop scheduled task (local, machine awake) → `/schedule` Routine (cloud, fresh clone, `claude/` branches) → GitHub Actions / Managed Agents schedule (infra-native).

**Step 7 — Run in training mode.** First several runs pause at each key step for human approval. This is a discipline (permission prompts/checkpoints), not a named feature. Watch the reasoning and outputs.

**Step 8 — Graduate autonomy deliberately.** Push the slider only as fast as checker + your review can catch failures. For less-quantifiable goals, keep human checkpoints at key decision moments. Build loops to think faster, not to stop thinking.

**Step 9 (new) — Graduate scale deliberately.** Only after a loop is trustworthy at Tier 1 should you consider: Managed Agents deployment (schedules + vaults + Outcomes + webhooks + Console tracing) for org-shaped jobs, or Dynamic Workflows (`ultracode`, first-run confirmation ON) for audit/migration-scale jobs. Both multiply capability *and* token burn *and* blast radius.

## Cadence & benchmarks

- **This week:** one boring bounded job through Steps 0–4 + 7. *Graduate when:* correct with zero human corrections across 3 consecutive supervised runs.
- **This month:** move to a persistent trigger; turn checkpoints off; add dollar/turn ceiling and idempotency; add worktrees if >1 loop. *Expand when:* one week of stable unattended operation, no runaway costs, no bad merges.
- **This quarter:** library of orchestration skills over validated skills; `.claude/skills/` + `.claude/agents/` committed as shared assets; connectors last, least-privilege; consider Managed Agents / Dynamic Workflows per Step 9. *Pull back when:* review bandwidth can't keep pace (comprehension debt rising) or a loop ships a bug you didn't catch — slide autonomy down, tighten verification, then re-expand.
- **Quarterly harness review** (new, per Anthropic's harness-design guidance): for each loop ask *"what can I stop doing?"* — delete scaffolding that compensated for model limitations that no longer exist. Keep the boundaries (verification, permissions, audit); prune the rest.

## The never-do list

- Never let the maker grade its own work (self-preference bias — NeurIPS 2024).
- Never build a loop on an unproven skill.
- Never write a vague finish line ("make it good" / "production-ready").
- Never run unbounded — no iteration cap + no cost ceiling = runaway burn.
- Never skip the memory file; never keep state in the chat.
- Never run parallel agents in the same working directory.
- Never give an unattended loop broad connector permissions; never use `--dangerously-skip-permissions` outside a sandbox.
- Never confuse autonomy with abdication — verification is still your job.
- Never over-engineer: add complexity only when it demonstrably improves outcomes. A single well-verified loop beats a fragile multi-agent cathedral — and note that even the 750k-line Bun rewrite still landed as human-reviewed PRs.

## What would change these recommendations

- **Token-constrained?** Stay single-agent and short; skip Tiers 2–3 parallelism.
- **Low-verifiability tasks** (product strategy, novel design)? Loops help less — keep a human in the generation-verify loop; automate only the verifiable sub-parts. Outcomes' subjective-rubric support narrows this gap but doesn't close it.
- **Version drift.** `/goal` v2.1.139+, scheduled tasks v2.1.72+, worktree isolation v2.1.33+, dynamic workflows GA since ~June 2026. Verify against code.claude.com/docs before relying on exact flags.

## Sources
- Base guide (this series' parent document) + Osmani (Jun 2026)
- Anthropic claude.com/blog, Feb–Jul 2026 (Routines, Harness Design, Managed Agents series, Dynamic Workflows, model/effort guide, code migrations)
- Claude Code docs; Anthropic "Building Effective Agents"

← Back to [00 — README](00-README.md)
