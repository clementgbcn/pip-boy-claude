"""All terminal display: header, boot sequence, response rendering, screens."""

import shutil
import sys
import time
from datetime import datetime

from ._colors import B, BG, CLS, DG, G, HC, INV, R, SC
from .stats import ConvoStats, karma, stat_bar

LOGO = [
    r" ██████╗ ██╗██████╗        ██████╗  ██████╗ ██╗   ██╗",
    r" ██╔══██╗██║██╔══██╗      ██╔══██╗██╔═══██╗╚██╗ ██╔╝",
    r" ██████╔╝██║██████╔╝█████╗██████╔╝██║   ██║ ╚████╔╝ ",
    r" ██╔═══╝ ██║██╔═══╝ ╚════╝██╔══██╗██║   ██║  ╚██╔╝  ",
    r" ██║     ██║██║           ██████╔╝╚██████╔╝   ██║   ",
    r" ╚═╝     ╚═╝╚═╝           ╚═════╝  ╚═════╝    ╚═╝   ",
]


BOOT_MSGS: list[tuple[str, float]] = [
    ("ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM", 0.04),
    ("COPYRIGHT 2075-2077 ROBCO INDUSTRIES", 0.04),
    ("", 0.08),
    ("*** BOOT SEQUENCE INITIATED ***", 0.30),
    ("", 0.05),
    ("LOADING VAULT-TEC FIRMWARE v3.14 ........", 0.15),
    (f"[{'█' * 20}] 100%  OK", 0.25),
    ("", 0.05),
    ("INITIALIZING CLAUDE AI SUBSYSTEM ........", 0.20),
    (f"[{'█' * 20}] 100%  OK", 0.35),
    ("", 0.05),
    ("CALIBRATING PERSONALITY MATRICES ........", 0.15),
    (f"[{'█' * 20}] 100%  OK", 0.25),
    ("", 0.05),
    ("SYNCING OVERSEER UPLINK ........", 0.20),
    (f"[{'█' * 20}] 100%  OK", 0.30),
    ("", 0.10),
    ("ALL SYSTEMS NOMINAL.", 0.40),
    ("WELCOME, VAULT DWELLER.", 0.50),
]


def terminal_width() -> int:
    return shutil.get_terminal_size().columns


def _center(s: str) -> str:
    return s.center(terminal_width())


def _border_row(s: str) -> str:
    return "║" + s.center(terminal_width() - 2) + "║"


def divider() -> None:
    print(f"{G}{'─' * terminal_width()}{R}")


def print_header() -> None:
    w = terminal_width()
    print(f"{BG}{B}")
    print("╔" + "═" * (w - 2) + "╗")
    for line in LOGO:
        print(_border_row(line))
    print("╠" + "═" * (w - 2) + "╣")
    print(_border_row("VAULT-TEC INDUSTRIES  ·  PIP-BOY 3000 MARK IV"))
    print(_border_row("ROBCO CERTIFIED™  ·  AI COMPANION UNIT"))
    print("╚" + "═" * (w - 2) + "╝")
    print(R)


def print_tabs(active: str = "CHAT") -> None:
    tabs = ["STAT", "CHAT", "LOG", "HELP"]
    row = "  ".join(
        f"{INV} {t} {R}{BG}" if t == active else f"{DG}[{t}]{R}{BG}"
        for t in tabs
    )
    print(f"\n{BG}  {row}{R}")


def boot_sequence() -> None:
    print(CLS + HC)
    print(f"\n{G}")
    for msg, delay in BOOT_MSGS:
        print(_center(msg) if msg else "")
        sys.stdout.flush()
        time.sleep(delay)
    time.sleep(0.6)
    print(CLS + SC, end="")
    print_header()
    print_tabs("CHAT")
    divider()
    now = datetime.now().strftime("%Y.%m.%d  %H:%M")
    print(f"\n{G}  STATUS: {BG}ONLINE{G}  |  COMPANION: {BG}CLAUDE AI{G}  |  {now}{R}\n")
    print(f"{DG}  Type your message and press ENTER. Commands: {BG}help{DG} · {BG}stat{DG} · {BG}exit{R}\n")
    divider()


def open_response_box() -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    sys.stdout.write(HC)
    print(f"\n{G}  ┌─[ {BG}CLAUDE-BOY{G} ]─[ {DG}{ts}{G} ]{R}")
    sys.stdout.write(f"{G}  │ {R}")
    sys.stdout.flush()


def write_chunk(chunk: str) -> None:
    for ch in chunk:
        if ch == "\n":
            sys.stdout.write(f"\n{G}  │ {R}")
        else:
            sys.stdout.write(ch)
    sys.stdout.flush()


def close_response_box() -> None:
    sys.stdout.write(SC)
    print(f"\n{G}  └{'─' * (terminal_width() - 4)}{R}\n")


def print_user_msg(text: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{BG}  ┌─[ DWELLER ]─[ {DG}{ts}{BG} ]{R}")
    print(f"{BG}  │ {text}{R}")
    print(f"{BG}  └{'─' * (terminal_width() - 4)}{R}")


def show_stat(convo_stats: ConvoStats, turns: int) -> None:
    print(CLS, end="")
    print_header()
    print_tabs("STAT")
    divider()
    print(f"\n{BG}  S.P.E.C.I.A.L — CLAUDE AI COMPANION STATS\n{R}")
    for abbr, name, val, note in convo_stats.compute(turns):
        print(f"{BG}  {abbr}{G} · {name:<14}{BG}{stat_bar(val)}{G} {val:>2}/10  {DG}{note}{R}")
    k = karma(convo_stats, turns)
    print(f"\n{DG}  XP: {BG}{turns * 100:>5}{DG}   LVL: {BG}{max(1, turns):<3}{DG}  KARMA: {k}{R}\n")
    divider()
    input(f"{DG}  [ press ENTER to return ]{R} ")


def show_help() -> None:
    print(CLS, end="")
    print_header()
    print_tabs("HELP")
    divider()
    cmds = [
        ("help",  "Show this help screen"),
        ("stat",  "Display S.P.E.C.I.A.L stats"),
        ("log",   "Show conversation count"),
        ("clear", "Clear screen and restart session"),
        ("exit",  "Power down Pip-Boy"),
    ]
    print(f"\n{BG}  PIP-BOY COMMAND REFERENCE\n{R}")
    for cmd, desc in cmds:
        print(f"{BG}  > {cmd:<10}{G}  {desc}{R}")
    print()
    divider()
    input(f"{DG}  [ press ENTER to return ]{R} ")
