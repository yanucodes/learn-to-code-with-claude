---
name: learn-to-code-with-claude
description: A study companion for technical topics. Use when the user wants to be quizzed on a programming topic (for general study, deeper understanding, or interview prep), generate spaced-repetition flashcards in their Obsidian vault, or create concept explanation notes for learning. Triggers include "quiz me on X", "test me on X", "interview me on X", "make flashcards on X", "explain X for studying", "study notes for X", "teach me X".
---

# Learn to Code with Claude

Four modes for studying technical topics — quiz yourself, recap what you've already learned, generate flashcards, or write deeper explanation notes. Useful for learning something new, building a study habit, or preparing for an interview. All study material is written to a user-configured Obsidian vault.

## 1. Read configuration

Before doing anything, load configuration from `~/.claude/skills/learn-to-code-with-claude/config.json`.

If the file does not exist:
1. Ask the user three things:
   - The absolute path to their Obsidian vault (suggest `~/Documents/Obsidian` as a default).
   - The languages they want explanation notes generated in (e.g. `["python", "swift"]`).
   - How they want coding problems handled in quiz mode — `coding_mode`, one of:
     - `"claude"` — Claude invents a problem and scaffolds solution + test files locally.
     - `"leetcode"` — Claude suggests a relevant LeetCode problem (name + URL) instead of writing one.
     - `"none"` — skip coding problems entirely; conceptual questions only.
2. Expand `~` to the home directory.
3. Write the config:
   ```json
   {
     "vault_path": "<absolute path>",
     "languages": ["<lang1>", "<lang2>"],
     "coding_mode": "<claude|leetcode|none>"
   }
   ```
4. Confirm the location and continue.

If the config exists but is missing `coding_mode` (older install), default to `"leetcode"` and continue without re-prompting.

For all subsequent operations, treat `vault_path` as the root for study material. Create subdirectories as needed.

## 2. Pick the mode

Decide based on the user's request:

| User says... | Mode |
| --- | --- |
| "quiz me on", "test me on", "interview me on", "mock interview" | **Quiz** |
| "recap", "what do I know about", "test what I know about", "review what I know about" | **Recap** |
| "flashcards", "spaced repetition", "memorize", "anki" | **Flashcards** |
| "explain", "study notes", "notes on", "teach me" | **Explanation notes** |

If unclear, ask which one.

---

## 3. Resolving `$ARGUMENTS`

Several modes accept `$ARGUMENTS` that may be either a **topic name** ("python async", "swift actors") or a **file path** ("auth.py", "src/parser.ts"). Apply this rule consistently across modes:

Treat `$ARGUMENTS` as a **file path** if any of the following hold:
- It starts with `~`, `./`, `../`, or `/`.
- It starts with `@` (Claude Code's file-reference convention) — strip the `@` and treat the rest as a relative path.
- It contains a `/`.
- It ends with a known code-file extension (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.swift`, `.rs`, `.go`, `.java`, `.kt`, `.rb`, `.cs`, `.cpp`, `.c`, `.h`, `.hpp`, `.md`, `.json`, `.yaml`, `.yml`, `.toml`, `.sh`) **and** a file with that name exists in the current working directory.
- The literal string, interpreted as a path relative to the current working directory, points to an existing file.

Otherwise, treat `$ARGUMENTS` as a **topic name**.

**Tie-breaking:** if a string could match both (e.g. `cache.swift` could be the phrase "cache in Swift" or a filename in the cwd), prefer the file path **only when the file actually exists**; otherwise treat as topic. If you genuinely cannot tell, ask the user before proceeding rather than guessing.

---

## 4. Resolving the language

All vault-written artifacts (quiz tracking files, flashcards, concept notes) are sorted by programming language. Determine the language `<lang>` like this:

1. **File path** (per section 3): map the extension. `.py` → `python`, `.ts`/`.tsx` → `typescript`, `.js`/`.jsx` → `javascript`, `.swift` → `swift`, `.rs` → `rust`, `.go` → `go`, `.java` → `java`, `.kt` → `kotlin`, `.rb` → `ruby`, `.cs` → `csharp`, `.cpp`/`.cc`/`.h`/`.hpp` → `cpp`, `.c` → `c`.
2. **Topic name with a leading language token** (e.g. "python async", "swift actors", "rust ownership"): use the leading token as the language. Strip it from the slug used in the filename.
3. **Session-based work or empty `$ARGUMENTS`**: infer the dominant language from the conversation. If multiple languages were involved and no single one dominates, ask the user which to file under.
4. **Otherwise** (language-agnostic topics like "Big-O", "REST APIs", or a topic with no detectable language): use `general`.

Use lowercase single-word identifiers (`python`, `typescript`, `cpp` — not `Python` or `c++`).

The remaining slug — the topic minus the language token — is what goes into the filename. If stripping leaves the slug empty (e.g. user said just "python"), use `general` for the slug part (so the file becomes `python/general-questions.md`).

---

## Mode A — Quiz

You are conducting a technical quiz about the topic the user named (the "$TOPIC"). The format is interview-style — three conceptual questions plus optional coding — because that format works well for self-testing whether the user is prepping for an actual interview or just deepening their understanding of a topic. Treat all use cases the same.

### Quiz source — pick one

**(a) Topic quiz** (default). The user named a topic like `python async`, `swift actors`, `system design caching`. Use the procedure below.

**(b) File quiz.** `$ARGUMENTS` resolves to a file path per section 3 — e.g. "quiz me on auth.py", "quiz me on ./src/parser.ts", "quiz me on @lib/cache.swift". In this case:
- **Source of questions:** the file's contents. Read the file first, then ask about the code, libraries used, control flow, error handling, and design choices visible in it. Ask about *why* choices were made, not just *what* the code does.
- **Skip the tracking file** — file-specific quizzes are one-off, not a recurring topic the user revisits.
- **Coding portion:** if `coding_mode` is `"claude"`, instead of inventing a fresh problem, ask the user to re-implement or modify a piece of the file (e.g. "rewrite the `parseTokens` function from this file without looking"). If `coding_mode` is `"leetcode"` or `"none"`, follow the same rules as for topic quizzes.
- Everything else (3 conceptual questions, good/poor evaluation, follow-up offer for flashcards/notes) works the same.

**(c) Session quiz.** The user asked to be quizzed on the work just done in this conversation — phrases like "quiz me on what we just built", "quiz me on this project", "test me on what we just did", "quiz me on this code". This is for users who paired with Claude on a coding task and want to verify they actually understand what was built. In this case:
- **Source of questions:** the conversation history. Pull questions from the actual code written, libraries used, design decisions made, error cases handled, and architectural patterns chosen. Ask about *why* choices were made, not just *what* was done.
- **Skip the tracking file** — these questions are session-specific, not part of a topic the user revisits.
- **Coding portion:** if `coding_mode` is `"claude"`, instead of inventing a fresh problem, ask the user to re-implement or modify a small piece of what was just built (e.g. "rewrite the `parseTokens` function from this session without looking"). If `coding_mode` is `"leetcode"` or `"none"`, follow the same rules as for topic quizzes.
- Everything else (3 conceptual questions, good/poor evaluation, follow-up offer for flashcards/notes) works the same.

### Procedure (topic quiz)

**Tracking file:** `<vault_path>/Quizzes/<lang>/<slug>-questions.md` (e.g. `python/async-questions.md`, `general/algorithms-questions.md`). Resolve `<lang>` and `<slug>` per section 4. Create the directory and an empty file if missing.

1. Read the tracking file. **Do not repeat any listed questions.**
2. Ask 3 conceptual questions. The coding portion depends on `coding_mode`:
   - **`"claude"`** — give 1 coding problem and create a solution file + test file in the **current working directory** (not the vault) so the user can run tests locally:
     - `coding/<topic-slug>/<problem-slug>.<ext>` — empty stub for the user to write in
     - `coding/<topic-slug>/<problem-slug>.test.<ext>` — runnable tests
     - Pick the file extension and test framework that match the topic (e.g. Python → `pytest`, Swift → `XCTest`, JS/TS → `vitest` or `jest`).
   - **`"leetcode"`** — suggest 1 relevant LeetCode problem instead. Give the problem name, difficulty, the canonical URL (`https://leetcode.com/problems/<slug>/`), and 1–2 sentences on why it fits the topic. Do not write any local files. Ask the user to come back when they've attempted it; evaluate based on their explanation of approach + complexity.
   - **`"none"`** — skip the coding portion entirely. The quiz is conceptual only.
3. Wait for answers. Evaluate each as **good** or **poor**, and explain briefly *why*.
4. After the quiz is complete, append only the **good** questions (compressed one-liners, no answers) to the tracking file.
   - If the file would exceed 20 questions after appending, drop entries from the top until it is at or under 20.
   - **Never write poorly answered questions** — those are gaps the user still needs to study.
5. Offer a follow-up: *"Want me to make flashcards or explanation notes for the questions you got wrong?"*

---

## Mode B — Recap

Re-tests questions the user previously answered well, to verify the knowledge has stuck. This is the spaced-repetition layer of the quiz loop — Mode A deliberately avoids repeating "good" questions; Mode B deliberately pulls from them.

**Tracking file:** `<vault_path>/Quizzes/<lang>/<slug>-questions.md` (resolve per section 4). Should already exist with previously well-answered questions.

**Procedure:**

1. Read the tracking file.
   - If missing or empty: tell the user there are no tracked questions for this topic yet, and suggest running a regular quiz first (`quiz me on <topic>`). Do not proceed.
2. Pick up to 5 questions from the file. If the file has more than 5 entries, sample randomly; if fewer, use all of them. **No coding portion in recap.**
3. Reconstruct the full question from each compressed one-liner and ask the user.
4. Wait for answers. Evaluate each as **good** or **poor**, with a brief explanation of *why*.
5. Update the tracking file:
   - For **good** answers — leave the entry in place.
   - For **poor** answers — **remove that entry from the tracking file.** The user no longer reliably knows it, so it should not be filtered out of future quizzes.
6. List the questions answered poorly and offer a follow-up: *"Want me to make flashcards or explanation notes for these?"*

---

## Mode C — Flashcards

**Source:**
- If `$ARGUMENTS` resolves to a file path (per section 3), read that file and base cards on it.
- If `$ARGUMENTS` is a topic name, generate cards directly on that topic.
- If `$ARGUMENTS` is empty, use the conversation history above (typically gaps from a recent quiz).

**Output file:** `<vault_path>/Flashcards/<lang>/<slug>-<YYYY-MM-DD>.md` (resolve `<lang>` and `<slug>` per section 4).

**Format — Obsidian Spaced Repetition plugin default (multi-line basic):**
- The first line is the tag `#flashcards`.
- Each card is `question`, then `?` on its own line, then `answer`.
- Cards are separated by **one blank line**.
- No titles, no headings, no card terminators.
- For code/syntax questions, include only the minimal snippet needed for the answer.

Example file:

```
#flashcards

What does Python's `with` statement do?
?
Wraps a block in a context manager that calls `__enter__` on entry and `__exit__` on exit (even if an exception is raised).

In Swift, what is the difference between `let` and `var`?
?
`let` declares an immutable binding. `var` declares a mutable one.
```

If the user has a different SR plugin separator configured (`::` for single-line, `??` for reversed multi-line), follow whatever they ask for, but default to the format above.

---

## Mode D — Explanation notes

**Source:**
- If `$ARGUMENTS` resolves to a file path (per section 3), read it for context — write notes about the concepts the file is using or implementing, not just a summary of the file itself.
- If `$ARGUMENTS` is a topic name, use it directly.
- If `$ARGUMENTS` is empty, use the conversation history (knowledge gaps you noticed).

**Output:** Write each concept to `<vault_path>/Concepts/<lang>/<concept-slug>.md` (resolve `<lang>` per section 4 — for a multi-language concept like Big-O, file under `general/`). If a file already exists for that concept, show the user a brief summary of the existing note and ask whether to **overwrite**, **append** (add a new section dated `## YYYY-MM-DD` with the new material below the existing content), or **skip**.

These notes are written to **teach the concept**, not just summarize it. The user should be able to learn from the note when the topic is new to them, and still find it useful to skim later as a refresher.

Each file should contain:
- A plain-language explanation of *what* the concept is and, more importantly, *why* it exists — the problem it solves. Use as many sentences as the concept needs; do not pad, but do not cut explanation short for the sake of brevity.
- A minimal code example **in each language listed in `config.json` `languages`**. If the concept is language-agnostic (e.g. Big-O), one example is fine.
- Common gotchas, edge cases, or misconceptions (when relevant).
- A short "relates to" line connecting the concept to neighboring ideas the user likely already knows, when a useful connection exists.

Structure the note with light headings (e.g. `## What it is`, `## Why`, `## Example`, `## Gotchas`) so it can be skimmed later. Skip sections that don't apply rather than padding them.

---

## Closing

After completing any mode, briefly tell the user **what was written and where**, using paths relative to the vault when possible.
