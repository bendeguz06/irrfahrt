# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

Uses a Python virtual environment in `env/`. Activate it before running:

```bash
source env/bin/activate
pip install -r reqs.txt
```

## Running

```bash
python main.py
```

Quit with `Q` key or close the window.

## Architecture

Single-file pygame application (`main.py`) that simulates a 1D random walk. Each frame, `X` is incremented or decremented by 1 with equal probability via `walk()`, and the current value is rendered on screen at 120 FPS.

Assets: `OpenSans-Bold.ttf` (font), `rw_logo.png` (window icon).
