# 04 — Skills-First Discipline & Harness Design

## TL;DR
- **No loop without a battle-tested skill behind it.** Osmani: a loop with no reusable skills inside it is a while-true around a stranger.
- Skills are the *progressive-disclosure* context mechanism Anthropic itself recommends: short YAML frontmatter pre-loaded, full body read only when a task calls for it. This is harness pattern #2 ("let Claude assemble its own context") in action.
- **New since the base guide:** the Agent Harness Design post (Apr 2, 2026) supplies the theory and benchmarks behind skills-first discipline, and gives loop engineers a standing maintenance question: *what can I stop doing?*

## Why skills come first

Do the task manually with Claude several times. When it works reliably, capture it as `.claude/skills/<name>/SKILL.md`. Only then is the task a loop candidate. Reasons:

1. **A skill is a tested procedure; a prompt is a hope.** The loop will run at 2 a.m. without you. Everything implicit in your prompting has to become explicit in the skill.
2. **Skills are versioned, shared, and reviewable.** Commit `.claude/skills/` and `.claude/agents/`; your quality criteria become team assets the checker can also read.
3. **The description is the trigger.** Vague skill descriptions never fire. Write tight, trigger-oriented descriptions; keep SKILL.md under ~500 lines; push reference material into adjacent files (progressive disclosure).
4. **Feedback loops multiply quality.** Cherny's documented workflow always gives Claude a way to verify its own work (a bash command, a test suite, browser testing) — improving output quality by his estimate 2–3×. Bake the verification command *into* the skill.

## The harness-design connection (Anthropic, Apr 2026)

The Agent Harness Design post explains *why* skills-first works, with numbers:

- **Skills > giant system prompts.** Pre-loading every instruction depletes the model's attention budget and wastes tokens on rarely-used context. Skills disclose progressively.
- **Code execution > harness orchestration.** Giving Claude a code-execution tool lets it express tool calls *and the logic between them*, keeping bulky intermediate results out of context. Measured effect: Opus 4.6 filtering its own tool outputs went from 45.3% → 61.6% on BrowseComp. For loops: prefer skills that have Claude write a script over skills that enumerate twenty tool calls.
- **Memory & compaction scale with the model.** Sonnet 4.5 stayed flat at 43% on an agentic-search benchmark regardless of compaction budget; Opus 4.5 scaled to 68% and Opus 4.6 to 84% with the same setup. A memory folder lifted Sonnet 4.5 from 60.4% → 67.2% on BrowseComp-Plus. Your loop's memory design (File 06) pays off more with each model generation.
- **Prune dead weight.** Anthropic's context-reset scaffolding for Sonnet 4.5's "context anxiety" became unnecessary by Opus 4.5. Schedule a quarterly review of every loop asking: which parts of this harness exist to compensate for a limitation that's gone?

## Skill-driven development for loops: the ratios

- Aim for roughly **one validator skill per ~4 work skills** (your `/engineer-review`, `/fact-checker`, `/email-review` layer). These plug directly into the checker stage (File 05).
- Keep a git-tracked **CLAUDE.md** (~2–3k tokens) for always-true conventions and documented past mistakes — Cherny's team practice.
- Daily workflows live as slash commands in `.claude/commands/`; loop-grade procedures graduate to `.claude/skills/`.

## Choosing the right container (quick reference)

Synthesizing Smith Horn Group, McNamara, and AntStack:

| You need… | Use |
|---|---|
| Procedure the same agent should follow | **Skill** |
| Fresh context / different model / unbiased judgment | **Subagent** |
| Access to an external system | **MCP connector** |
| The whole loop as a deployable service | **Agent SDK / Managed Agents** |
| One-off instruction, this session only | Just prompt — don't build anything |

## Sources
- Anthropic, "Agent Harness Design: 3 Patterns" (Apr 2, 2026)
- Anthropic skills guidance; Claude Code docs
- Osmani (Jun 2026); Cherny workflow accounts (2026)
- Smith Horn Group (Dec 2025); McNamara (Oct 2025); AntStack (Mar 2026)

→ Next: [05 — Verification: Maker vs. Checker](05-verification.md)
