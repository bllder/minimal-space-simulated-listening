#!/usr/bin/env python3
"""Run MSSL listening-experience pipeline (minimal cleaned version)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_HANDOFF_NAME = "online_ai_listening_handoff.md"
DEFAULT_PROMPT_INPUT_NAME = "original_song_listening_prompt_input.md"


def parse_args():
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input")
    src.add_argument("--profile")
    p.add_argument("--output-dir", default="outputs")
    return p.parse_args()


def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    cmd = [sys.executable, str(script_dir / "run_full_song_analysis.py")]
    if args.input:
        cmd += ["--input", args.input]

    subprocess.run(cmd, check=True)

    handoff = Path(args.output_dir) / DEFAULT_HANDOFF_NAME
    prompt_input = Path(args.output_dir) / DEFAULT_PROMPT_INPUT_NAME

    print(handoff)


if __name__ == "__main__":
    main()
