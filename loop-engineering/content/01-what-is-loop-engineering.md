# 01 — What Is Loop Engineering?

## TL;DR
- Loop engineering is **replacing yourself as the person who prompts the agent**: you design a system that finds work, executes it, verifies it, records progress, and decides what happens next — then attach it to a trigger.
- The term was named by **Addy Osmani** (Director, Google Cloud AI) in a June 7, 2026 essay, republished by O'Reilly Radar on June 22, 2026. It crystallized statements by **Boris Cherny** (head of Claude Code) and **Peter Steinberger** (creator of OpenClaw). *Common misattribution to "Aditya Agrawal" is wrong.*
- The shift is happening now because the building blocks that used to require custom bash scripts ship inside the products: `/goal`, `/loop`, cloud Routines, Skills, subagents with worktree isolation, hooks, MCP — and, since spring 2026, platform-level features like **Outcomes**, **Dreaming**, and **Dynamic Workflows** that productize entire loop patterns.

## From prompting to loops

For roughly two years, the way you got value from a coding agent was: write a good prompt, supply context, read the output, prompt again. **You** were the engine of the loop; the agent was the tool inside it.

Loop engineering inverts that. The canonical quotes:

- **Boris Cherny** (Acquired Unplugged, hosted by WorkOS, June 2, 2026): he no longer prompts Claude directly — he writes the loops that prompt Claude and figure out what to do next.
- **Peter Steinberger** (X, June 7–8, 2026, ~6.5M views): stop prompting coding agents; start designing the loops that prompt them.
- **Andrej Karpathy** supplies the counterweight: keep AI "on the leash" — partial autonomy, human in the generation–verification loop, and move the autonomy slider rightward only as fast as your verification can catch what breaks.

Osmani's key observation: this is *not really a tool thing*. The same loop shape works in Claude Code and Codex because both expose the same primitives. What changed in 2026 is that the primitives became first-class.

## The 2026 inflection: loops became product features

The base pattern (trigger → work → verify → remember → repeat) used to be something you assembled from cron and shell scripts. As of mid-2026, each stage has a native implementation:

| Loop stage | Hand-rolled (2024–25) | Native (2026) |
|---|---|---|
| Trigger | cron + `claude -p` | `/loop`, Routines (`/schedule`), Desktop scheduled tasks, Managed Agents schedules |
| Execute | prompt files | Skills (`SKILL.md`), slash commands, plugins |
| Verify | eyeball the diff | `/goal` evaluator, **Outcomes** graders, dynamic-workflow refuter agents |
| Remember | copy-paste context | CLAUDE.md, auto-memory, memory tool, **Dreaming** |
| Parallelize | multiple terminals | `--worktree`, `isolation: worktree`, `/batch`, multiagent orchestration, **Dynamic Workflows** |

The arXiv survey "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems" (2604.14228, Apr 2026) frames the same point academically: the design space of agent systems has consolidated around a small set of composable primitives, and the differentiation has moved to *how you compose them* — which is exactly what loop engineering is.

## What loop engineering is NOT

- **Not autonomy for its own sake.** The hard part is verification, stop conditions, and cost control — not getting the agent to run unattended.
- **Not a replacement for judgment.** Karpathy's framing holds: if you can't evaluate the output, you can't safely automate producing it.
- **Not "set and forget."** Every serious practitioner account (Cherny, Osmani, Anthropic's own migration write-ups) keeps a human in the review seat and treats unattended operation as something a loop *earns*.

## Attribution corrections (carried forward from the base guide)

- "Loop engineering" → **Addy Osmani**, not "Aditya Agrawal." (High confidence.)
- "The agent forgets, the repo doesn't" → also Osmani's line.
- Cherny's exact wording varies across secondary coverage; the substance is verified, the punctuation is approximate.

## Sources
- Osmani (Jun 2026); O'Reilly Radar republication (Jun 22, 2026)
- Acquired Unplugged / WorkOS conversation with Boris Cherny (Jun 2, 2026)
- arXiv:2604.14228 (Apr 16, 2026)
- Anthropic, "Building Effective Agents"

→ Next: [02 — Anatomy of a Loop](02-anatomy-of-a-loop.md)
