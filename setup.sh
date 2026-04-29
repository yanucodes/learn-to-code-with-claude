#!/usr/bin/env bash
#
# Setup script for the learn-to-code-with-claude skill.
# Installs the skill to ~/.claude/skills/ and writes a user-specific config.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="learn-to-code-with-claude"
SKILL_SRC="$SCRIPT_DIR/.claude/skills/$SKILL_NAME"
SKILL_DEST="$HOME/.claude/skills/$SKILL_NAME"
CONFIG_PATH="$SKILL_DEST/config.json"

if [[ ! -d "$SKILL_SRC" ]]; then
  echo "Error: cannot find skill source at $SKILL_SRC"
  echo "Run this script from the cloned repo root, or via its full path."
  exit 1
fi

echo "Setting up $SKILL_NAME"
echo "------------------------------------"
echo

# 1. Install the skill into ~/.claude/skills/
mkdir -p "$HOME/.claude/skills"
if [[ -d "$SKILL_DEST" ]]; then
  read -r -p "Skill already installed at $SKILL_DEST. Overwrite? [y/N] " confirm
  if [[ "$confirm" =~ ^[yY]$ ]]; then
    rm -rf "$SKILL_DEST"
  else
    echo "Aborted."
    exit 1
  fi
fi
cp -r "$SKILL_SRC" "$SKILL_DEST"
echo "Installed skill to $SKILL_DEST"
echo

# 2. Obsidian vault path
echo "Step 1 of 3 -- Obsidian vault location"
echo
while true; do
  read -r -p "Path to your Obsidian vault: " vault_input
  vault_input="${vault_input/#\~/$HOME}"

  if [[ -z "$vault_input" ]]; then
    echo "Path cannot be empty."
    continue
  fi

  if [[ -d "$vault_input" ]]; then
    vault_abs="$(cd "$vault_input" && pwd)"
    echo "Using existing directory: $vault_abs"
    break
  fi

  echo "Directory does not exist: $vault_input"
  while true; do
    read -r -p "(c)reate it, or (r)e-enter the path? [c/r] " choice
    case "$choice" in
      c|C)
        mkdir -p "$vault_input"
        vault_abs="$(cd "$vault_input" && pwd)"
        echo "Created: $vault_abs"
        break 2
        ;;
      r|R)
        break
        ;;
      *)
        echo "Please enter c or r."
        ;;
    esac
  done
done
echo

# 3. Languages
echo "Step 2 of 3 -- Languages for explanation notes"
echo "Enter one per line. Press Enter on a blank line when done."
echo
languages=()
while true; do
  read -r -p "Language: " lang
  if [[ -z "$lang" ]]; then
    if [[ ${#languages[@]} -eq 0 ]]; then
      echo "Enter at least one language."
      continue
    fi
    break
  fi
  languages+=("$lang")
done
echo "Languages: ${languages[*]}"
echo

# 4. coding_mode
echo "Step 3 of 3 -- How should quiz mode handle coding problems?"
echo
echo "  1. claude    Claude invents a coding problem and writes solution + test files in your project."
echo "  2. leetcode  Claude suggests a relevant LeetCode problem (name + URL) instead of writing one."
echo "  3. none      Skip coding problems entirely. Conceptual questions only."
echo
while true; do
  read -r -p "Choose [1/2/3 or claude/leetcode/none]: " mode_input
  case "$mode_input" in
    1|claude)   coding_mode="claude";   break ;;
    2|leetcode) coding_mode="leetcode"; break ;;
    3|none)     coding_mode="none";     break ;;
    *) echo "Enter 1, 2, 3, claude, leetcode, or none." ;;
  esac
done
echo "Coding mode: $coding_mode"
echo

# 5. Write config
langs_json=""
for lang in "${languages[@]}"; do
  esc="${lang//\"/\\\"}"
  langs_json+="\"$esc\","
done
langs_json="[${langs_json%,}]"

cat > "$CONFIG_PATH" <<EOF
{
  "vault_path": "$vault_abs",
  "languages": $langs_json,
  "coding_mode": "$coding_mode"
}
EOF

echo "Setup complete."
echo "Config written to: $CONFIG_PATH"
echo
echo "Try it from any project in Claude Code:"
echo "  > quiz me on ${languages[0]}"
echo "  > explain decorators for studying"
