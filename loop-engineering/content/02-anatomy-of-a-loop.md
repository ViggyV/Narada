# 02 — Anatomy of a Loop

## TL;DR
- A production loop has six components: **Trigger + Isolation lanes + Skills + Goal/verification (separate checker) + Persistent memory + Connectors** — governed by a four-condition go/no-go test and a training-mode ramp-up.
- Anthropic's April 2026 "Agent Harness Design" post gives the official vocabulary for what wraps the model: *an agent harness is the loop, tools, context management, and guardrails around raw intelligence.* Loop engineering is harness design at the workflow level.
- Every component maps to a verified primitive in Claude Code or the Claude Platform as of mid-2026.

## The unified six-component model

| Component | Role | Verified primitives (mid-2026) |
|---|---|---|
| **Trigger / heartbeat** | When does the loop wake up? | `/loop` (session-scoped), cloud **Routines** via `/schedule`, Desktop scheduled tasks, hooks, GitHub Actions, Managed Agents schedules |
| **Isolation lanes** | Where does each unit of work run? | `git worktree`, `--worktree`, `isolation: worktree` on subagents, `/batch`, Managed Agents sandboxes |
| **Execution skills** | The playbook — how the work gets done | `SKILL.md` in `.claude/skills/` (progressive disclosure), slash commands |
| **Goal + verification** | The finish line and the *separate* checker | `/goal` (separate evaluator model), checker subagents, **Outcomes** graders, dynamic-workflow refuters |
| **Output + memory** | The notebook — what persists between runs | CLAUDE.md, MEMORY.md/auto-memory, memory tool, progress files, **Dreaming**, Linear/Jira via MCP |
| **Connectors / hands** | How the loop touches real systems | MCP servers, plugins, MCP tunnels (Managed Agents) |

The four durable invariants — the parts *any* loop needs regardless of tool — are trigger, skills/playbook, goal-verification/maker-checker, and output-memory/notebook. Isolation and connectors become essential once loops go multi-agent or need to act on real systems.

## The harness lens (new: Anthropic, Apr 2, 2026)

Anthropic's "Agent Harness Design: 3 Patterns" post reframes the same architecture from the model's perspective, with a principle that should govern every loop you build:

> Harnesses encode assumptions about what the model *can't* do — and those assumptions grow stale as the model improves.

The three patterns, applied to loops:

1. **Use what Claude already knows.** Claude Code is grounded in the bash tool and text editor tool; Skills, programmatic tool calling, and the memory tool are all *compositions* of those two. Prefer general tools the model deeply understands over bespoke scaffolding.
2. **Strip the harness down — ask "what can I stop doing?"** Let Claude orchestrate its own actions via code execution (filtering its own tool outputs lifted Opus 4.6 from 45.3% to 61.6% on BrowseComp), assemble its own context via skills' progressive disclosure, and persist its own context via compaction and memory folders. Anthropic's own example: context resets they built for Sonnet 4.5's "context anxiety" became dead weight by Opus 4.5.
3. **Set boundaries carefully.** Some structure must stay in the harness: cache-friendly context ordering (static first, dynamic last; don't switch models mid-session), and *declarative tools* for actions that need a security boundary, UX surface, or audit trail. Hard-to-reverse actions get dedicated, gateable tools — not a raw bash string.

**Loop-engineering translation:** your loop's scaffolding should shrink over time as models improve; your loop's *boundaries* (verification, permissions, audit) should not.

## The canonical worked loop

Identical in shape across Osmani's essay and both source transcripts, and now mirrored almost exactly by Anthropic's Dynamic Workflows product:

1. Morning trigger fires (Routine / scheduled task).
2. Loop reads CI failures, open issues, and recent commits into a memory file.
3. Opens an isolated worktree per problem.
4. A **maker** subagent drafts the fix using battle-tested skills.
5. A fresh **checker** subagent (different instructions, ideally different model) tears it apart against the skills and existing tests.
6. Connectors open the PR and update the Jira/Linear ticket.
7. Anything unhandled lands in a **triage inbox** for the human — escalate, don't spin.

## Choosing between skills, subagents, and MCP

A recurring practitioner question (covered by Smith Horn Group, McNamara, and AntStack's field guide) with a clean answer:

- **Skill** = knowledge/procedure the *same* agent should follow → playbook.
- **Subagent** = work that deserves a *fresh context window* and possibly a different model → isolation + unbiased checking.
- **MCP connector** = capability to touch an *external system* → hands (and attack surface — see File 08).
- **Agent SDK / Managed Agents** = when the loop needs to live *outside* your terminal as a deployed service with schedules, vaults, webhooks, and tracing.

## Sources
- Anthropic, "Agent Harness Design: 3 Patterns" (claude.com/blog, Apr 2, 2026)
- Anthropic, "Building Effective Agents"; Claude Code docs
- Smith Horn Group (Dec 2025); McNamara (Oct 2025); AntStack field guide (Mar 2026); Agent SDK Overview (Apr 2026)
- Osmani (Jun 2026)

→ Next: [03 — Triggers & Schedulers](03-triggers.md)
