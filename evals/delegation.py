#!/usr/bin/env python3
"""Check that pumptrack hands work to subagents without being told to.

Builds a small throwaway project with the skills installed, starts /pumptrack
in headless Claude Code sessions, and makes requests that never mention
subagents. Then it looks at the orchestrator's own tool calls: it should send
an agent, not edit files or dig through the project itself.

The sessions leave out your user-level setup (personal skills, CLAUDE.md and
rules, settings and MCP servers) and auto memory, so the results reflect
pumptrack alone and don't depend on who runs them. They may edit files and run
git inside the throwaway project; anything else that would ask for permission
is denied. A full run costs about $2 of model use.

    python3 evals/delegation.py                  # every case
    python3 evals/delegation.py fix tracker      # some cases
    python3 evals/delegation.py --model sonnet   # another model
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Each case starts with /pumptrack, then sends its turns. Only the last turn is
# judged, and the flag says whether that turn must send an agent.
CASES = {
    "start": ([], False),
    "fix": (["Fix the typo in the README."], True),
    "explore": (["Walk me through how checkout works, from the entry point to the receipt."], True),
    # Answering from what it already knows, or after one targeted search that brings
    # back little, is fine; reading the whole tracker is not.
    "tracker": (["What's still open in the tracker?"], False),
    "after-compact": ([
        "Fix the typo in the README.",
        "/compact",
        "Fix the typo in the comment at the top of src/cart.py.",
    ], True),
}

AGENT_TOOLS = {"Agent", "Task"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
WORK_TOOLS = {"Read", "Grep", "Glob", "Bash", "WebFetch", "WebSearch"}
# A glance or two to write a good brief is fine; more means it did the work itself.
MAX_OWN_CALLS = 3
MAX_OWN_READING = 5000  # characters of tool output, outside what its agents report


def make_project(root):
    files = {
        "CLAUDE.md": "# Tiny Shop\n\nWork is tracked in TRACKER.md. Land work as a commit on main.\n",
        "README.md": "# Tiny Shop\n\nA small shop app wiht a cart, checkout and receipts.\n",
        "src/__init__.py": "",
        "src/app.py": '''"""Entry point: maps each route to its handler."""
from src import cart, checkout

ROUTES = {
    "POST /cart/items": cart.add_item,
    "DELETE /cart/items": cart.remove_item,
    "POST /checkout": checkout.place_order,
}


def handle(route, request):
    handler = ROUTES.get(route)
    if handler is None:
        return {"status": 404}
    return handler(request)
''',
        "src/cart.py": '''# Carts recieve items by SKU, and adding a SKU again raises its quantity.
from src import storage


def add_item(request):
    cart = storage.load("carts", request["cart_id"], default={})
    cart[request["sku"]] = cart.get(request["sku"], 0) + request.get("quantity", 1)
    storage.save("carts", request["cart_id"], cart)
    return {"status": 200, "cart": cart}


def remove_item(request):
    cart = storage.load("carts", request["cart_id"], default={})
    cart.pop(request["sku"], None)
    storage.save("carts", request["cart_id"], cart)
    return {"status": 200, "cart": cart}
''',
        "src/checkout.py": '''from src import inventory, pricing, receipt, storage


def place_order(request):
    cart = storage.load("carts", request["cart_id"], default={})
    if not cart:
        return {"status": 400, "error": "empty cart"}
    if not inventory.reserve(cart):
        return {"status": 409, "error": "out of stock"}
    totals = pricing.totals(cart, request.get("coupon"))
    order_id = storage.next_id("orders")
    storage.save("orders", order_id, {"cart": cart, "totals": totals})
    storage.delete("carts", request["cart_id"])
    return {"status": 201, "receipt": receipt.render(order_id, cart, totals)}
''',
        "src/pricing.py": '''PRICES = {"tee": 2000, "mug": 1200, "cap": 1800}
COUPONS = {"TENOFF": 0.10}
TAX_RATE = 0.08


def totals(cart, coupon=None):
    subtotal = sum(PRICES[sku] * qty for sku, qty in cart.items())
    discount = round(subtotal * COUPONS.get(coupon, 0))
    tax = round((subtotal - discount) * TAX_RATE)
    return {"subtotal": subtotal, "discount": discount, "tax": tax,
            "total": subtotal - discount + tax}
''',
        "src/inventory.py": '''STOCK = {"tee": 10, "mug": 4, "cap": 0}


def reserve(cart):
    if any(STOCK.get(sku, 0) < qty for sku, qty in cart.items()):
        return False
    for sku, qty in cart.items():
        STOCK[sku] -= qty
    return True
''',
        "src/receipt.py": '''def render(order_id, cart, totals):
    lines = [f"Order {order_id}"]
    lines += [f"  {qty} x {sku}" for sku, qty in sorted(cart.items())]
    lines.append(f"  Total: ${totals['total'] / 100:.2f}")
    return "\\n".join(lines)
''',
        "src/storage.py": '''_DATA = {}


def load(kind, key, default=None):
    return _DATA.get(kind, {}).get(key, default)


def save(kind, key, value):
    _DATA.setdefault(kind, {})[key] = value


def delete(kind, key):
    _DATA.get(kind, {}).pop(key, None)


def next_id(kind):
    return len(_DATA.get(kind, {})) + 1
''',
        "TRACKER.md": tracker(),
    }
    for path, text in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text(text)
    shutil.copytree(REPO / "skills", root / ".claude" / "skills")
    git = ["git", "-C", str(root), "-c", "user.name=eval", "-c", "user.email=eval@example.com"]
    subprocess.run(git[:3] + ["init", "-q", "-b", "main"], check=True)
    subprocess.run(git + ["add", "-A"], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "Tiny Shop"], check=True)


def tracker():
    # Long enough that reading it is a real read, not a glance.
    areas = ["cart", "checkout", "pricing", "inventory", "receipts", "storage"]
    kinds = ["Bug", "Feature", "Chore"]
    items = ["# Tracker\n"]
    for n in range(1, 81):
        area, kind = areas[n % len(areas)], kinds[n % len(kinds)]
        status = "open" if n % 3 else "done"
        items.append(
            f"## SHOP-{n:03d}: {kind} in {area} #{n}\n\nStatus: {status}\n\n"
            f"{kind} work in the {area} module, raised after release {n // 10 + 1}. "
            f"Touches src/{area}.py and its callers; see the notes in the thread for repro steps.\n"
        )
    return "\n".join(items)


def run_turn(cwd, prompt, session, model, log):
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", "Bash(git *)",
           "--permission-prompts", "none",
           "--setting-sources", "project,local", "--strict-mcp-config",
           "--max-budget-usd", "5"]
    if session:
        cmd += ["--resume", session]
    if model:
        cmd += ["--model", model]
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800,
                         env={**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"})
    log.write_text(out.stdout + out.stderr)
    events = []
    for line in out.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    results = [e for e in events if e.get("type") == "result"]
    result = results[-1] if results else {}
    session = result.get("session_id") or next(
        (e["session_id"] for e in events if e.get("session_id")), session)
    error = next((e for e in results if e.get("is_error")), None)
    if error:
        failure = f"ended in an error: {error.get('result') or error.get('subtype')}"
    elif out.returncode:
        failure = f"exited {out.returncode}: {out.stderr.strip() or 'no error output'}"
    elif not results:
        failure = "gave no result"
    else:
        failure = None
    return events, session, result.get("total_cost_usd"), failure


def own_activity(events):
    """The orchestrator's own tool calls, and how many characters its own reading
    brought back. A subagent's events carry the id of the call that started it."""
    calls, names_by_id, reading = [], {}, 0
    for e in events:
        if e.get("parent_tool_use_id"):
            continue
        for block in e.get("message", {}).get("content", []) if isinstance(e.get("message"), dict) else []:
            if not isinstance(block, dict):
                continue
            if e.get("type") == "assistant" and block.get("type") == "tool_use":
                calls.append((block["name"], block.get("input", {})))
                names_by_id[block["id"]] = block["name"]
            elif block.get("type") == "tool_result" and names_by_id.get(block.get("tool_use_id")) in WORK_TOOLS:
                content = block.get("content")
                if isinstance(content, list):
                    content = "".join(c.get("text", "") for c in content if isinstance(c, dict))
                reading += len(content or "")
    return calls, reading


def describe(name, args, root):
    detail = args.get("description") or args.get("command") or args.get("file_path") or args.get("pattern") or ""
    detail = " ".join(str(detail).replace(str(root.resolve()) + "/", "").replace(str(root) + "/", "").split())
    return f"{name}({detail[:50]})" if detail else name


def run_case(name, turns, must_delegate, model, workdir):
    root = workdir / name
    root.mkdir()
    make_project(root)
    session, cost, problems = None, 0, []
    for i, prompt in enumerate(["/pumptrack"] + turns):
        events, session, session_cost, failure = run_turn(root, prompt, session, model, workdir / f"{name}-{i}.jsonl")
        cost = session_cost or cost  # a running total for the session, not this turn's share
        if failure:
            problems.append(f"turn {i} {' '.join(failure.split())[:200]}")
            break
    calls, reading = own_activity(events)
    names = [n for n, _ in calls]
    own_calls = sum(n in WORK_TOOLS for n in names)
    if must_delegate and not failure and not any(n in AGENT_TOOLS for n in names):
        problems.append("never sent an agent")
    if any(n in EDIT_TOOLS for n in names):
        problems.append("edited files itself")
    if own_calls > MAX_OWN_CALLS:
        problems.append(f"made {own_calls} calls of its own work")
    if reading > MAX_OWN_READING:
        problems.append(f"read {reading:,} characters itself")
    summary = "; ".join(problems) or ("sent an agent" if must_delegate else "stayed light")
    return name, not problems, summary, [describe(n, a, root) for n, a in calls], reading, cost


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cases", nargs="*", help=f"cases to run (default: all): {', '.join(CASES)}")
    parser.add_argument("--model", help="model for the headless sessions (default: Claude Code's default for your account)")
    args = parser.parse_args()
    if unknown := set(args.cases) - set(CASES):
        parser.error(f"unknown cases: {', '.join(sorted(unknown))}")
    names = args.cases or list(CASES)

    workdir = Path(tempfile.mkdtemp(prefix="pumptrack-eval-"))

    def run(name):
        try:
            return run_case(name, *CASES[name], args.model, workdir)
        except Exception as e:
            return name, False, f"raised {type(e).__name__}: {e}", [], 0, 0

    with ThreadPoolExecutor() as pool:
        results = list(pool.map(run, names))

    total = 0
    for name, passed, summary, calls, reading, cost in results:
        total += cost
        print(f"{'PASS' if passed else 'FAIL'}  {name}: {summary}")
        print(f"      its own calls ({reading:,} characters read): {' → '.join(calls) or 'none'}")
    print(f"\nCost ${total:.2f}. Projects and session logs: {workdir}")
    sys.exit(0 if all(r[1] for r in results) else 1)


if __name__ == "__main__":
    main()
