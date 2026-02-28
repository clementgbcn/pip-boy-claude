"""Main entry point – the Pip-Boy interactive loop."""

import itertools
import select
import signal
import sys
import termios
import threading
import time
import tty
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
                stop_event = threading.Event()
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_claude, raw, turn == 0, stop_event)
                    interrupted = False
                    old_settings = termios.tcgetattr(sys.stdin)
                    try:
                        tty.setcbreak(sys.stdin.fileno())
                        for symbol in itertools.cycle("|/─\\"):
                            sys.stdout.write(f"\r{DG}  [ PROCESSING {symbol} · any key to stop ]{R}")
                            sys.stdout.flush()
                            if select.select([sys.stdin], [], [], 0.12)[0]:
                                sys.stdin.read(1)
                                stop_event.set()
                                interrupted = True
                                break
                            if future.done():
                                break
                    finally:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    sys.stdout.write(f"\r{' ' * 46}\r")
                    response, elapsed = future.result()
                if interrupted:
                    print(f"\n{DG}  [ TRANSMISSION ABORTED — SIGNAL LOST IN THE WASTELAND ]{R}\n")
                elif response.startswith(("[FATAL]", "[SYSTEM ERROR]")):
                    print(f"\n{AM}  {response}{R}\n")
                else:
                    turn += 1
                    convo_stats.record(raw, response, elapsed)
                    print_ai_response(response)
                divider()
