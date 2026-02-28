"""Claude CLI bridge – calls `claude` as a subprocess and parses stream-json."""

import json
import subprocess
import threading
from collections.abc import Iterator

_FALLOUT_SUFFIX = (
    " [Respond in the style of a Pip-Boy AI from the Fallout universe: "
    "terse, slightly ironic, post-apocalyptic tone. Use Vault-Tec jargon "
    "and occasional radiation/wasteland metaphors. Keep it brief.]"
)


def stream_claude(
    message: str,
    first_turn: bool = True,
    stop_event: threading.Event | None = None,
) -> Iterator[str]:
    """Yield text chunks as they arrive from the claude subprocess."""
    cmd = ["claude", "-p", "--verbose", "--output-format", "stream-json"]
    if not first_turn:
        cmd.append("--continue")
    cmd.append(message + (_FALLOUT_SUFFIX if first_turn else ""))

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        yield "[FATAL] 'claude' not found in PATH. Ensure Claude Code is installed."
        return
    except Exception as e:
        yield f"[FATAL] {e}"
        return

    for raw in proc.stdout:  # type: ignore[union-attr]
        if stop_event is not None and stop_event.is_set():
            proc.terminate()
            proc.wait()
            return
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            match obj.get("type", ""):
                case "content_block_delta":
                    delta = obj.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            yield text
                case "assistant":
                    for block in obj.get("message", {}).get("content", []):
                        if block.get("type") == "text":
                            text = block.get("text", "")
                            if text:
                                yield text
        except json.JSONDecodeError:
            pass

    proc.wait()
    if proc.returncode != 0:
        err = proc.stderr.read()  # type: ignore[union-attr]
        yield f"[SYSTEM ERROR] {err.strip() or 'Unknown error'}"
