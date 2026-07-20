#!/usr/bin/env python3
"""Chrystal 2 agent terminal (Gradio) — stream what agents/scripts are doing.

Launch (repo root):
  python chrystal_2/ui/agent_terminal.py

Open: http://127.0.0.1:7860
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def _header(title: str) -> str:
    return f"\n{'=' * 72}\n[{_ts()}] {title}\n{'=' * 72}\n"


def stream_command(cmd: list[str], cwd: Path = ROOT) -> Iterator[str]:
    """Run a command and yield stdout/stderr lines for Gradio streaming."""
    yield _header(" ".join(cmd))
    yield f"cwd: {cwd}\n\n"
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
        )
    except OSError as exc:
        yield f"ERROR launching process: {exc}\n"
        return

    assert proc.stdout is not None
    for line in proc.stdout:
        yield line
    code = proc.wait()
    yield f"\n[{_ts()}] exit_code={code}\n"


def run_step(
    step: str,
    qid: str,
    domain_id: str,
    log: str,
) -> Iterator[str]:
    qid = (qid or "").strip().upper()
    domain_id = (domain_id or "").strip()
    if not qid.startswith("Q"):
        yield (log or "") + "Need a QID like Q17167\n"
        return
    if not domain_id:
        yield (log or "") + "Need a domain_id like roman_republic\n"
        return

    scripts = {
        "pack_library": [
            PY,
            str(ROOT / "chrystal_2" / "harvest" / "build_pack_library.py"),
            "--qid",
            qid,
        ],
        "schema_propose": [
            PY,
            str(ROOT / "chrystal_2" / "agents" / "schema_specialist" / "__main__.py"),
            "propose",
            "--qid",
            qid,
            "--domain-id",
            domain_id,
        ],
        "schema_dry_context": [
            PY,
            str(ROOT / "chrystal_2" / "agents" / "schema_specialist" / "__main__.py"),
            "propose",
            "--qid",
            qid,
            "--domain-id",
            domain_id,
            "--dry-run",
        ],
        "apply_dry": [
            PY,
            str(ROOT / "chrystal_2" / "agents" / "domain" / "apply_schema.py"),
            "--qid",
            qid,
            "--domain-id",
            domain_id,
            "--dry-run",
        ],
        "apply_review": [
            PY,
            str(ROOT / "chrystal_2" / "agents" / "domain" / "apply_schema.py"),
            "--qid",
            qid,
            "--domain-id",
            domain_id,
            "--review-only",
        ],
        "apply_review_write": [
            PY,
            str(ROOT / "chrystal_2" / "agents" / "domain" / "apply_schema.py"),
            "--qid",
            qid,
            "--domain-id",
            domain_id,
            "--review-write",
        ],
    }
    if step not in scripts:
        yield (log or "") + f"Unknown step: {step}\n"
        return

    buf = log or ""
    for chunk in stream_command(scripts[step]):
        buf += chunk
        yield buf
        time.sleep(0)  # allow Gradio to flush


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Chrystal 2 agent terminal") as demo:
        gr.Markdown(
            """
# Chrystal 2 — agent terminal
Streaming console for pack harvest / schema propose / Domain apply review.
Not a full product UI — a **detour spike** so you can watch agents work.
            """.strip()
        )
        with gr.Row():
            qid = gr.Textbox(label="QID", value="Q17167", scale=1)
            domain_id = gr.Textbox(
                label="domain_id", value="roman_republic", scale=2
            )
        with gr.Row():
            b_pack = gr.Button("1 · Pack library", variant="secondary")
            b_ctx = gr.Button("2 · Schema context (dry)", variant="secondary")
            b_propose = gr.Button("3 · Schema propose (LLM)", variant="primary")
            b_dry = gr.Button("4 · Apply dry-run", variant="secondary")
            b_review = gr.Button("5 · Apply review (LLM)", variant="primary")
            b_write = gr.Button("6 · Review + write Neo", variant="stop")
        log = gr.Textbox(
            label="Terminal",
            lines=28,
            max_lines=40,
            autoscroll=True,
            elem_id="agent_terminal",
        )
        clear = gr.Button("Clear log")

        clear.click(lambda: "", outputs=log)

        def bind(step: str):
            def _fn(q, d, existing):
                yield from run_step(step, q, d, existing)

            return _fn

        b_pack.click(bind("pack_library"), [qid, domain_id, log], log)
        b_ctx.click(bind("schema_dry_context"), [qid, domain_id, log], log)
        b_propose.click(bind("schema_propose"), [qid, domain_id, log], log)
        b_dry.click(bind("apply_dry"), [qid, domain_id, log], log)
        b_review.click(bind("apply_review"), [qid, domain_id, log], log)
        b_write.click(bind("apply_review_write"), [qid, domain_id, log], log)

        gr.Markdown(
            "Tip: step **6** writes Aura `7fe339d2` after Domain LLM review. "
            "Use 4–5 first."
        )
    return demo


def main() -> None:
    demo = build_ui()
    demo.queue().launch(server_name="127.0.0.1", server_port=7860, share=False)


if __name__ == "__main__":
    main()
