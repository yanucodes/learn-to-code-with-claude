#!/usr/bin/env python3
"""Setup script for the learn-to-code-with-claude skill.

Installs the skill to ~/.claude/skills/ and writes a user-specific config.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "learn-to-code-with-claude"


def prompt(message: str) -> str:
    try:
        return input(message)
    except EOFError:
        print()
        sys.exit("Aborted.")
    except KeyboardInterrupt:
        print()
        sys.exit("Aborted.")


def resolve_user_path(raw: str) -> Path:
    """
    Expand ~ and environment variables, then resolve to an absolute Path.

    Raises:
        ValueError if the result still contains an unexpanded variable
        (e.g. user typed $FOO and FOO is not set).
    """
    expanded = os.path.expanduser(os.path.expandvars(raw.strip()))
    if not expanded:
        raise ValueError("path is empty")
    if "$" in expanded or expanded.startswith("~"):
        raise ValueError(
            f"path contains an unexpanded variable after expansion: {expanded!r}. "
            "Check that any environment variables you used (e.g. $HOME) are set."
        )
    return Path(expanded).expanduser().resolve()


def ask_vault_path() -> Path:
    print("Step 1 of 3 -- Obsidian vault location\n")
    while True:
        raw = prompt("Path to your Obsidian vault: ")
        if not raw.strip():
            print("Path cannot be empty.")
            continue

        try:
            path = resolve_user_path(raw)
        except ValueError as e:
            print(f"Invalid path: {e}")
            continue

        if path.is_dir():
            print(f"Using existing directory: {path}\n")
            return path

        if path.exists():
            print(f"Path exists but is not a directory: {path}")
            continue

        print(f"Directory does not exist. Resolved path:\n  {path}")
        while True:
            choice = prompt("(c)reate it, or (r)e-enter the path? [c/r] ").strip().lower()
            if choice == "c":
                path.mkdir(parents=True, exist_ok=True)
                print(f"Created: {path}\n")
                return path
            if choice == "r":
                break
            print("Please enter c or r.")


def ask_languages() -> list[str]:
    print("Step 2 of 3 -- Languages for explanation notes")
    print("Enter one per line. Press Enter on a blank line when done.\n")
    languages: list[str] = []
    while True:
        lang = prompt("Language: ").strip()
        if not lang:
            if not languages:
                print("Enter at least one language.")
                continue
            break
        languages.append(lang)
    print(f"Languages: {', '.join(languages)}\n")
    return languages


def ask_coding_mode() -> str:
    print("Step 3 of 3 -- How should quiz mode handle coding problems?\n")
    print("  1. claude    Claude invents a coding problem and writes solution + test files in your project.")
    print("  2. leetcode  Claude suggests a relevant LeetCode problem (name + URL) instead of writing one.")
    print("  3. none      Skip coding problems entirely. Conceptual questions only.\n")
    mapping = {
        "1": "claude", "claude": "claude",
        "2": "leetcode", "leetcode": "leetcode",
        "3": "none", "none": "none",
    }
    while True:
        choice = prompt("Choose [1/2/3 or claude/leetcode/none]: ").strip().lower()
        if choice in mapping:
            mode = mapping[choice]
            print(f"Coding mode: {mode}\n")
            return mode
        print("Enter 1, 2, 3, claude, leetcode, or none.")


def install_skill(script_dir: Path) -> Path:
    src = script_dir / ".claude" / "skills" / SKILL_NAME
    dest = Path.home() / ".claude" / "skills" / SKILL_NAME

    if not src.is_dir():
        sys.exit(
            f"Error: cannot find skill source at {src}\n"
            "Run this script from the cloned repo root, or via its full path."
        )

    print(f"Setting up {SKILL_NAME}")
    print("------------------------------------\n")

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        confirm = prompt(f"Skill already installed at {dest}. Overwrite? [y/N] ").strip().lower()
        if confirm != "y":
            sys.exit("Aborted.")
        shutil.rmtree(dest)

    shutil.copytree(src, dest)
    print(f"Installed skill to {dest}\n")
    return dest


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    dest = install_skill(script_dir)
    config_path = dest / "config.json"

    vault_path = ask_vault_path()
    languages = ask_languages()
    coding_mode = ask_coding_mode()

    config = {
        "vault_path": str(vault_path),
        "languages": languages,
        "coding_mode": coding_mode,
    }
    config_path.write_text(json.dumps(config, indent=2) + "\n")

    print("Setup complete.")
    print(f"Config written to: {config_path}\n")
    print("Try it from any project in Claude Code:")
    print(f"  > quiz me on {languages[0]}")
    print("  > explain decorators for studying")


if __name__ == "__main__":
    main()
