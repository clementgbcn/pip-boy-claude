"""Main entry point – the Pip-Boy interactive loop."""

import os
import queue
import readline
import select
import signal
import sys
import termios
import threading
import time
import tty

_HISTORY_FILE = os.path.expanduser("~/.pipboy/history")

from ._colors import AM, BG, DG, G, R
from .claude import stream_claude
from .log import LOG_FILE, append_turn, total_turns
from .stats import ConvoStats
from .ui import boot_sequence, close_response_box, divider, open_response_box, print_header, print_tabs, print_user_msg, show_help, show_stat, write_chunk


def main() -> None:
    os.makedirs(os.path.dirname(_HISTORY_FILE), exist_ok=True)
    try:
        readline.read_history_file(_HISTORY_FILE)
    except FileNotFoundError:
        pass
    readline.set_history_length(500)

    _needs_redraw = False

    def _exit(*_: object) -> None:
        readline.write_history_file(_HISTORY_FILE)
        print(f"\n\n{G}  {BG}POWERING DOWN PIP-BOY...{G}")
        print(f"  STAY SAFE OUT THERE, VAULT DWELLER.{R}\n")
        sys.exit(0)

    def _handle_resize(*_: object) -> None:
        nonlocal _needs_redraw
        _needs_redraw = True

    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGWINCH, _handle_resize)
    boot_sequence()
    turn = 0
    convo_stats = ConvoStats()

    while True:
        if _needs_redraw:
            _needs_redraw = False
            print_header()
            print_tabs("CHAT")
            divider()
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
                total = total_turns()
                print(f"\n{G}  Session turns: {BG}{turn}{G}  |  Total logged: {BG}{total}{G}  |  Log: {DG}{LOG_FILE}{R}\n")
                divider()
            case "clear":
                turn = 0
                convo_stats.reset()
                boot_sequence()
            case _:
                print_user_msg(raw)
                stop_event = threading.Event()
                chunk_q: queue.Queue[str | None] = queue.Queue()

                def _produce(msg: str = raw, ft: bool = (turn == 0)) -> None:
                    for chunk in stream_claude(msg, ft, stop_event):
                        chunk_q.put(chunk)
                    chunk_q.put(None)

                threading.Thread(target=_produce, daemon=True).start()
                open_response_box()

                full_text: list[str] = []
                interrupted = False
                t0 = time.monotonic()
                old_settings = termios.tcgetattr(sys.stdin)
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    while True:
                        if select.select([sys.stdin], [], [], 0)[0]:
                            sys.stdin.read(1)
                            stop_event.set()
                            interrupted = True
                            break
                        try:
                            chunk = chunk_q.get(timeout=0.05)
                            if chunk is None:
                                break
                            full_text.append(chunk)
                            write_chunk(chunk)
                        except queue.Empty:
                            pass
                finally:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    close_response_box()

                elapsed = time.monotonic() - t0
                response = "".join(full_text)

                if interrupted:
                    print(f"\n{DG}  [ TRANSMISSION ABORTED — SIGNAL LOST IN THE WASTELAND ]{R}\n")
                elif not response.startswith(("[FATAL]", "[SYSTEM ERROR]")):
                    turn += 1
                    convo_stats.record(raw, response, elapsed)
                    append_turn(raw, response, elapsed)
                divider()
