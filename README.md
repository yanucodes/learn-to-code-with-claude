# Learn to Code with Claude

A [Claude Code](https://claude.com/claude-code) skill for learning to code — quiz yourself, recap what you've already learned, generate spaced-repetition flashcards, and write deeper concept explanations, all into your own Obsidian vault.

Useful any time you are:
- Building with an AI assistant - quiz yourself on the code you and Claude wrote together so you don't ship work you can't explain.
- Learning a new language or framework
- Preparing for a technical interview
- Reviewing concepts you've half-forgotten

The skill is built around three observations:

1. The fastest way to learn is to **get questions wrong and then close the gap.**
2. **Spaced repetition** makes what you learned stay learned.
3. Notes, cards, and quiz history should live in **one place you can always access** — your Obsidian vault.

The four modes form a learning loop: quiz yourself on a topic → make flashcards or explanation notes from what you missed → recap a few days later to verify what stuck. Use the whole loop, or any one mode on its own.

---

## What it does

### Quiz me — *probe what you don't yet know*

Three flavors of quiz, all interview-shaped (3 conceptual questions plus a coding portion based on your `coding_mode` setting):

**Topic.**
```
> quiz me on python async
```
Claude looks up which questions you've already answered well (so it doesn't repeat them) and asks fresh ones. Questions you nail get saved to a topic-specific file; the rest become gaps to study.

**File or PR.**
```
> quiz me on src/auth.py
```
Claude reads the file and bases questions on the code, libraries, and design choices visible in it. Great for your own code, learning from code in public repositories, or your study notes.

**This session — the vibe-coding fix.**
```
> quiz me on what we just built
```
Claude pulls questions from the actual code, libraries, and decisions in the current conversation. Great for avoiding comprehension debt and building mental models and deeper understanding as a junior developer.

### Recap — *verify what stuck*
```
> recap python
```
Pulls a handful of questions you previously answered well and re-tests them. If you still know the answer, the entry stays. If you don't, it's removed from the "known" list and offered up as a flashcard candidate.

### Flashcards — *make what you learned stick*
```
> make flashcards from this conversation
```
Generates cards in your vault using the **default format of the [Obsidian Spaced Repetition plugin](https://github.com/st3v3nmw/obsidian-spaced-repetition)** (multi-line basic, `?` separator, blank line between cards). No conversion needed — open Obsidian and start reviewing.

### Concept explanations — *go deeper, not just review*
```
> explain decorators for studying
```
Writes a learning-oriented note to your vault: the *why* of the concept, a minimal code example in each language you configured, common gotchas, and how it relates to ideas you likely already know. 

---

## Install

```bash
git clone https://github.com/<you>/learn-to-code-with-claude.git
cd learn-to-code-with-claude
python3 setup.py
```

The setup script copies the skill into `~/.claude/skills/` (so any Claude Code session, in any project, can invoke it) and walks you through the configuration interactively. It requires Python 3.8+ (no third-party dependencies).

> Prefer to skip the script? Copy `.claude/skills/learn-to-code-with-claude/` to `~/.claude/skills/` manually. The first time you ask Claude to quiz you, it'll prompt for the same answers and write the config itself.

---

## Configure

`setup.py` asks three things and writes them to `~/.claude/skills/learn-to-code-with-claude/config.json`:

- **Your Obsidian vault path** — anywhere on disk, e.g. `~/Documents/Obsidian` or `~/Notes`. The script checks the path exists; if it doesn't, it offers to create the directory or have you re-enter the path. It loops until the path is valid.
- **Languages for explanation notes** — entered one per line (press Enter on a blank line to finish). Notes will include a minimal example in each.
- **How you want coding problems handled** (`coding_mode`):
  - `claude` — Claude invents a problem and scaffolds a solution file + runnable tests in your current project. Best when you want to practice writing fresh code.
  - `leetcode` — Claude suggests a relevant LeetCode problem (name + URL) instead. Best when you're already grinding LeetCode and want the quiz to match.
  - `none` — no coding problems. Conceptual questions only. Best for quick refreshers or when you only have 10 minutes.

You can re-run `setup.py` to reconfigure, or edit `config.json` directly. A reference is at [`config.example.json`](.claude/skills/learn-to-code-with-claude/config.example.json).

---

## What gets written where

```
<your vault>/
├── Quizzes/
│   ├── python/
│   │   └── async-questions.md       # rolling list of questions you answered well (capped at 20)
│   └── swift/
│       └── actors-questions.md
├── Flashcards/
│   └── python/
│       └── async-2026-04-29.md      # ready for the SR plugin
└── Concepts/
    ├── python/
    │   └── decorators.md            # learning note: explanation, examples per language, gotchas
    └── general/
        └── big-o.md                 # language-agnostic concepts go under general/

<your project>/
└── coding/
    └── python/
        ├── reverse-linked-list.py
        └── reverse-linked-list.test.py
```

Everything in the vault is sorted by programming language. Topics with no clear language (Big-O, REST, system design) land under `general/`. Coding problems are written to your **current project**, not the vault — so you can `pytest` them in place.

---

## How it works

A Claude Code "skill" is a markdown file with a frontmatter description. When your prompt matches, Claude loads the skill and follows its instructions for the rest of the turn. The whole skill is one file: [`.claude/skills/learn-to-code-with-claude/SKILL.md`](.claude/skills/learn-to-code-with-claude/SKILL.md).

A few design choices worth calling out:

- **One skill, four modes (quiz, recap, flashcards, explain)** instead of three slash commands. Skills can branch on intent, which means the same prompt can flow naturally from "quiz me" to "now make flashcards on what I missed" without me having to type a new command.
- **The "questions answered well" file caps at 20.** It's a rolling window — old wins fall off so the quizzer keeps seeing fresh questions.
- **Flashcards use the SR plugin default format.** Makes them easy to use with the Spaced Repetition plugin.
- **Explanation notes.** Useful to learn a new concept and skim later when you just want a refresher.
- **Coding problems write real test files** in your project. You can immediately test your solution.

---

## A note on accuracy

Claude can be wrong — and study material is exactly the kind of place where wrong answers are dangerous, because they get encoded into flashcards and reviewed for months. Treat everything this skill produces as a draft, not a source of truth:

- **Quiz evaluations.** The "good / poor" judgment is Claude's, based on its own model of the topic. If something gets marked poor but you think you're right, push back and verify against docs.
- **Flashcards.** Spot-check the answer side before you start reviewing. A confidently wrong card you review thirty times is worse than no card at all.
- **Concept explanations.** Cross-check anything load-bearing against authoritative sources — language docs, official guides, original papers.

This skill is a study accelerant, not a textbook. Use it the way you'd use a smart study partner: helpful, fast, occasionally wrong.

---

## Why this exists

I'm a software developer who studies a lot, builds a lot, and — as a former scientist — values gaining a deep understanding of everything I'm learning. I don't blindly trust AI, but I use it as a tool to organize my notes, find my knowledge gaps, and identify areas where I could widen my expertise. I found that asking chatbots to quiz me is a great way to do this, so I created this skill for myself and expanded the functionality by adding modes to create flashcards and Obsidian notes.

I also believe it's important to keep my skills sharp, even when I use AI assistance for coding. [Studies show](https://arxiv.org/html/2601.20245v1) that coding with AI assistance can be detrimental to learning, but if used right, it can actually have a positive impact. I kept this in mind when creating this skill.

Day-to-day I use Claude Code for engineering work, write notes in my Obsidian vault when I learn new concepts, and create flashcards — so making a skill to automate the process felt like a great use case for Claude Code skills.

If you find it useful — or if you fork it for a different study domain — I'd love to hear about it.

---

## License

BSD-3-Clause. Use it, modify it, whatever helps.
