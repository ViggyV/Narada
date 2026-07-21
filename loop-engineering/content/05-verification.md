# 05 — Verification: Maker vs. Checker

## TL;DR
- **Never let the maker grade its own work.** Self-preference bias is measured, peer-reviewed reality (Panickssery, Bowman & Feng, NeurIPS 2024 Oral: self-recognition capability correlates linearly with self-preference strength).
- Two native implementations now exist: **`/goal`** in Claude Code (a separate small/fast model — default Haiku — reads the transcript each turn and answers yes/no) and **Outcomes** in Claude Managed Agents (a rubric-driven grader in its *own context window*, so it isn't influenced by the maker's reasoning).
- **New since the base guide:** Outcomes shipped with benchmark evidence — up to **+10 points task success** over a standard prompting loop, +8.4% on docx generation, +10.1% on pptx — and Dynamic Workflows added a third pattern: *adversarial* agents that actively try to refute findings before they reach you.

## `/goal`: the in-session checker (Claude Code v2.1.139+)

Mechanics that matter for loop design:

- After every turn, a separate small model judges your condition **against what Claude has surfaced in the conversation** — it doesn't run commands or read files independently. So the loop must *surface its proof*: print test output, exit codes, lint results.
- **Write machine-checkable finish lines.** Good: `/goal all tests in test/auth pass and the lint step is clean`. Bad: `/goal the app is production-ready`.
- **Bound it.** There is no built-in token budget; include `or stop after 15 turns` (or a time clause) in the condition. Interrupt with Ctrl+C or `/goal clear`.
- Pair with **auto mode** for substantial autonomous runs so goal turns don't stop for per-tool prompts.

## Outcomes: the productized grader (Managed Agents, May 2026)

Outcomes generalizes the maker/checker split beyond code:

- You write a **rubric** describing success; a **separate grader in its own context window** evaluates output against it, pinpoints what's wrong, and the agent takes another pass — no human reviewing each attempt.
- It works for exhaustive-coverage tasks *and* subjective quality (brand voice, visual guidelines) — with the caveat that subjective rubrics should still be decomposed toward binary checks for unattended runs.
- Evidence: up to +10 points task success, largest gains on the hardest problems; +8.4% (docx) and +10.1% (pptx) file-generation success in Anthropic's internal benchmarks.
- Field results: **Wisedocs** grades document reviews against internal guidelines — reviews run 50% faster while staying aligned with team standards. **Spiral** (by Every) scores every draft against a rubric of editorial principles and user voice pulled from memory; only drafts that clear the bar are returned.
- Pair with **webhooks**: define an outcome, let the agent run, get notified when it's done.

## The adversarial tier: Dynamic Workflows refuters (May 2026)

For critical work checked twice, Dynamic Workflows adds a stronger pattern than a single grader: agents attack the problem from independent angles, **other agents try to refute what they found**, and the run iterates until answers converge. Use this tier when the cost of a wrong answer is high (security audits, migrations, plans you're about to commit quarters to). Details in File 07.

## The verification ladder (choose deliberately)

| Tier | Mechanism | Use when |
|---|---|---|
| 0 | Tests/lint in the skill itself | Always — the floor |
| 1 | `/goal` transcript evaluator | In-session loops with verifiable output |
| 2 | Checker subagent (different instructions, ideally **different model family**) | Anything unattended |
| 3 | Outcomes rubric + separate grader | Non-code quality bars; deployed agents |
| 4 | Dynamic-workflow independent attempts + refuters | High-stakes, expensive-to-be-wrong work |

## Rubric discipline for unattended loops

- **Convert subjective rubrics to binary checks** two agents would agree on. A 1–5 scale is fine for humans; unreliable at 2 a.m.
- **Different model family as judge** is the stronger version of maker ≠ checker. Model/effort selection is now an explicit design axis (Anthropic's Jul 7, 2026 model-and-effort guide): cheap fast evaluators (Haiku) for frequent binary gates; heavyweight models only where a second opinion is worth paying for.
- **Force evidence, not self-assessment.** The loop emits test results, screenshots, exit codes; the checker judges artifacts, not claims.
- **Escalate, don't spin.** On a blocker: describe the problem, drop it in the triage inbox, stop.

## Sources
- Panickssery, Bowman & Feng, NeurIPS 2024
- Claude Code `/goal` docs (v2.1.139+)
- Anthropic, "New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration" (May 2026)
- Anthropic, "Introducing dynamic workflows in Claude Code" (May 28, 2026)
- Anthropic, "Choosing a Claude model and effort level in Claude Code" (Jul 7, 2026)
- Anthropic, "Building Effective Agents" (evaluator–optimizer pattern)

→ Next: [06 — Memory & State](06-memory.md)
