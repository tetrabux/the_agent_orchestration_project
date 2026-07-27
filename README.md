# Agent Orchestration — Paper Trading Assistant

A from-scratch build of an LLM agent that manages a fake stock portfolio.
I built the agent loop by hand first — no framework — then rebuilt the same
agent on top of LangGraph, and grew it step by step: routing across
multiple tools, recovering from a flaky tool without crashing, gating a
dangerous action behind human approval, persisting state across a process
restart, and keeping the prompt from growing unbounded on a long run.
Everything is local and fake — no real brokerage, no real money, ever.

## Setup

```
cp .env.example .env   # fill in OPENROUTER_API_KEY
uv sync
```

## Tools (all fake/local)

- `get_price(ticker)` — random price, fails ~40% of the time (simulates a
  rate-limited API)
- `get_portfolio()` — fixed fake cash + holdings
- `size_position(cash, price)` — pure calculation, no I/O
- `place_order(ticker, qty, side)` — irreversible write to a local
  `.portfolio.json` file

## Layout

- `raw_loop/` — the agent loop, hand-written, no framework: LLM sees
  goal + history + tools, emits a tool call or a final answer, the loop
  executes the tool and appends the result, repeats, with a hard iteration
  cap enforced in code.
- `graph_loop/` — the same agent modeled as a LangGraph graph: a shared
  state, an AI node, a tool node, and a conditional edge that routes
  "tool call → tool node" vs "final answer → END". The back-edge from the
  tool node to the AI node is the loop. Also carries the retry/backoff,
  human-approval gate, and context-compaction logic used by every folder
  below it — they all build the graph from here rather than duplicating it.
- `routing_loop/` — a task that needs all 3 read/calc tools, in an order
  the agent has to figure out itself.
- `resilient_loop/` — forces the flaky `get_price` failure and shows the
  agent recovering via retry instead of crashing.
- `gated_loop/` — `place_order` pauses for human approval before it fires;
  the read-only tools run freely. Uses LangGraph's checkpointing to pause
  and resume the run across the approval step.
- `sqlite_loop/` — same approval gate, but checkpointed to a SQLite file
  instead of memory, so a run can be stopped, the process killed, and
  resumed later by a completely separate process:
  ```
  uv run python -m sqlite_loop.main start    # pauses, exits
  uv run python -m sqlite_loop.main resume   # new process, finishes the run
  ```
- `trimmed_loop/` — once the conversation gets long, older messages get
  summarized into one message instead of being resent in full on every
  call, so the prompt sent to the model stays bounded regardless of how
  long the run runs.

## Notes

**Failure handling.** `get_price` fails on demand; the tool node retries
up to 3 times with exponential backoff before giving up, so a transient
failure doesn't take down the run:

```
[retry] get_price failed on attempt 1/3: rate limited — retrying in 1s

Here's the full summary of your request:
| AAPL Current Price | $279.00 per share |
| Available Cash | $2,318.65 |
| Whole Shares You Can Buy | 8 shares |
```

**Cost of a loop.** A one-shot prompt costs one call over one prompt. An
agent loop costs N calls, and because each call resends the entire running
history rather than just the new turn, the prompt itself grows every call
too — total tokens processed across a run scales closer to N² than N.
`trimmed_loop`'s logs make this concrete: by the fourth model call in a
single task, the full history had grown to 29 messages even though only
one new tool result had been added since the last call — everything before
it gets resent and reprocessed every time. This is exactly the shape
prompt-caching / KV-cache reuse exists for: each call's prompt is
(identical prefix) + (a few new tokens), so a cache-aware provider only
pays fresh compute for the tail instead of recomputing the whole prefix
from scratch. It's also the real argument for trimming — it's not just
about staying under a context-window limit, it's about shrinking what gets
reprocessed on every call in the loop.
