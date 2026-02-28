"""Claude CLI bridge – calls `claude` as a subprocess and parses stream-json."""

import json
import subprocess
import threading
import time


_FALLOUT_SUFFIX = (
    " [Respond in the style of a Pip-Boy AI from the Fallout universe: "
    "terse, slightly ironic, post-apocalyptic tone. Use Vault-Tec jargon "
    "and occasional radiation/wasteland metaphors. Keep it brief.]"
)


def call_claude(message: str, first_turn: bool = True, stop_event: threading.Event | None = None) -> tuple[str, float]:
    """Invoke the Claude CLI and return (response_text, elapsed_seconds).

    Uses ``--continue`` on every turn after the first so that the conversation
    history is maintained within the same working directory session.
    """
    cmd = ["claude", "-p", "--verbose", "--output-format", "stream-json"]
    if not first_turn:
        cmd.append("--continue")
    cmd.append(message + (_FALLOUT_SUFFIX if first_turn else ""))

    t0 = time.monotonic()
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        chunks: list[str] = []
        interrupted = False
        for raw in proc.stdout:  # type: ignore[union-attr]
            if stop_event is not None and stop_event.is_set():
                proc.terminate()
                interrupted = True
                break
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
                match obj.get("type", ""):
                    case "content_block_delta":
                        delta = obj.get("delta", {})
                        if delta.get("type") == "text_delta":
                            chunks.append(delta.get("text", ""))
                    case "assistant":
                        for block in obj.get("message", {}).get("content", []):
                            if block.get("type") == "text":
                                chunks.append(block.get("text", ""))
            except json.JSONDecodeError:
                pass
        proc.wait()
        elapsed = time.monotonic() - t0
        if interrupted:
            return "[INTERRUPTED]", elapsed
        if proc.returncode != 0:
            err = proc.stderr.read()  # type: ignore[union-attr]
            return f"[SYSTEM ERROR] {err.strip() or 'Unknown error'}", elapsed
        return "".join(chunks).strip() or "[No response received]", elapsed
    except FileNotFoundError:
        return "[FATAL] 'claude' not found in PATH. Ensure Claude Code is installed.", 0.0
    except Exception as e:
        return f"[FATAL] {e}", 0.0
