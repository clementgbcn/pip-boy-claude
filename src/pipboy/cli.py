"""Main entry point – the Pip-Boy interactive loop."""

import itertools
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from ._colors import AM, BG, DG, G, R
from .claude import call_claude
from .stats import ConvoStats
from .ui import boot_sequence, divider, print_ai_response, print_header, print_tabs, print_user_msg, show_help, show_stat


def main() -> None:
    def _exit(*_: object) -> None:
        print(f"\n\n{G}  {BG}POWERING DOWN PIP-BOY...{G}")
        print(f"  STAY SAFE OUT THERE, VAULT DWELLER.{R}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, _exit)
    boot_sequence()
    turn = 0
    convo_stats = ConvoStats()

    while True:
        try:
            raw = input(f"{BG}  >> {R}").strip()
        except EOFError:
            _exit()

        if not raw:
            continue

        match raw.lower():
            case "exit" | "quit" | "q":
                _exit()
            case "stat":
                show_stat(convo_stats, turn)
                print_header()
                print_tabs("CHAT")
                divider()
            case "help":
                show_help()
                print_header()
                print_tabs("CHAT")
                divider()
            case "log":
                print(f"\n{G}  Conversation turns: {BG}{turn}{R}\n")
                divider()
            case "clear":
                turn = 0
                convo_stats.reset()
                boot_sequence()
            case _:
                print_user_msg(raw)
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_claude, raw, turn == 0)
                    for symbol in itertools.cycle("|/─\\"):
                        sys.stdout.write(f"\r{DG}  [ PROCESSING {symbol} ]{R}")
                        sys.stdout.flush()
                        time.sleep(0.12)
                        if future.done():
                            break
                    sys.stdout.write(f"\r{' ' * 26}\r")
                    response, elapsed = future.result()
                if response.startswith(("[FATAL]", "[SYSTEM ERROR]")):
                    print(f"\n{AM}  {response}{R}\n")
                else:
                    turn += 1
                    convo_stats.record(raw, response, elapsed)
                    print_ai_response(response)
                divider()
