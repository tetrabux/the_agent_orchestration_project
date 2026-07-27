"""
Demo entry point for A1.

Acceptance (scope.md): a task needing >= 2 tool calls in sequence, solved
purely by the hand-written loop in loop.py — no framework.

Run with: uv run python -m raw_loop.main
"""

from .loop import run

GOAL = (
    "I have $2000 in cash. Look up AAPL's price, then tell me how many "
    "whole shares that covers."
)

if __name__ == "__main__":
    print(run(GOAL))
