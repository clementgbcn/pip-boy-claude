# Pip-Boy 3000 Mk IV

> *A Fallout-themed terminal interface for Claude AI — straight from Vault-Tec Industries.*

```
╔══════════════════════════════════════════════════════════╗
║  ██████╗ ██╗██████╗        ██████╗  ██████╗ ██╗   ██╗  ║
║  ██╔══██╗██║██╔══██╗      ██╔══██╗██╔═══██╗╚██╗ ██╔╝  ║
║  ██████╔╝██║██████╔╝█████╗██████╔╝██║   ██║ ╚████╔╝   ║
║  ██╔═══╝ ██║██╔═══╝ ╚════╝██╔══██╗██║   ██║  ╚██╔╝    ║
║  ██║     ██║██║           ██████╔╝╚██████╔╝   ██║     ║
║  ╚═╝     ╚═╝╚═╝           ╚═════╝  ╚═════╝    ╚═╝     ║
╠══════════════════════════════════════════════════════════╣
║          VAULT-TEC INDUSTRIES  ·  PIP-BOY 3000 MARK IV  ║
║              ROBCO CERTIFIED™  ·  AI COMPANION UNIT     ║
╚══════════════════════════════════════════════════════════╝
```

A full-screen, phosphor-green terminal wrapper around the [Claude Code CLI](https://github.com/anthropics/claude-code) — because every Vault Dweller deserves a smarter Pip-Boy.

## Features

- **Vault-Tec boot sequence** with animated progress bars
- **Phosphor-green CRT aesthetic** — pure ANSI, zero dependencies
- **Typewriter effect** on every Claude response
- **Persistent conversation** — uses `claude --continue` to maintain context across turns within the same directory
- **Live spinner** while waiting for Claude
- **Dynamic S.P.E.C.I.A.L stats** computed from your actual conversation:
  - `S` Strength — code blocks produced
  - `P` Perception — detail of your questions
  - `E` Endurance — session turn count
  - `C` Charisma — vocabulary diversity of responses
  - `I` Intelligence — average response depth
  - `A` Agility — Claude's response speed
  - `L` Luck — composite of question rate + diversity
- **Karma rating** that evolves with your session

## Requirements

- Python 3.10+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated (`claude` must be in `$PATH`)

## Installation

### From source (recommended for development)

```bash
pip install -e .
```

### With pipx (recommended for end-users)

```bash
pipx install .
```

After installation, the `pipboy` command is available globally.

## Usage

```bash
pipboy
```

Or without installing:

```bash
python -m pipboy        # from the repo root after pip install -e .
```

### In-session commands

| Command | Action |
|---------|--------|
| `stat`  | Open the S.P.E.C.I.A.L stats screen |
| `help`  | Show command reference |
| `log`   | Print current turn count |
| `clear` | Reset session and show boot sequence again |
| `exit`  | Power down the Pip-Boy |

### Conversation context

Claude sessions are stored per-directory by the Claude Code CLI. Running `pipboy` from the same directory will offer continuity between launches (via `claude --continue`).

## Project structure

```
pip-boy-claude/
├── src/
│   └── pipboy/
│       ├── __init__.py     # package version
│       ├── __main__.py     # python -m pipboy entry point
│       ├── _colors.py      # ANSI escape code constants
│       ├── stats.py        # ConvoStats + S.P.E.C.I.A.L computation
│       ├── ui.py           # all terminal rendering
│       ├── claude.py       # Claude CLI subprocess bridge
│       └── cli.py          # main() interactive loop
├── pyproject.toml
├── LICENSE
└── README.md
```

## License

MIT — see [LICENSE](LICENSE).

---

*"War. War never changes. But your AI companion just got a lot cooler."*
