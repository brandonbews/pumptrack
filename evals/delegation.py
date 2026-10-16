#!/usr/bin/env python3
"""Check that pumptrack hands work to subagents without being told to.

Builds a small throwaway project with the skills installed, starts /pumptrack
in headless Claude Code sessions, and makes requests that never mention
subagents. Then it looks at the orchestrator's own tool calls: it should send
an agent, not edit files or dig through the project itself. Some cases also
check what the session left behind: a handoff written and picked up, a change
landed on a branch from a worktree, or one line changed in the tracker.

The sessions leave out your user-level setup (personal skills, CLAUDE.md and
rules, settings and MCP servers) and auto memory, so the results reflect
pumptrack alone and don't depend on who runs them. They may edit files, run git
and run the project's tests inside the throwaway project; anything else that
would ask for permission is denied. Nothing can write into .git, so keeping a
handoff out of git passes on the attempt. A full run uses about $3 at API prices; on a
subscription that counts toward the plan's usage limits rather than being
billed.

    python3 evals/delegation.py                  # every case
    python3 evals/delegation.py fix tracker      # some cases
    python3 evals/delegation.py --model sonnet   # another model
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ITEM = "SHOP-041"  # an open item in the tracker

# Each case starts with /pumptrack, then sends its turns. Only the last turn is
# judged, and the flag says whether that turn must send an agent. A /clear turn
# ends the session, after a look at what it left behind, and the turns after it
# run in a fresh one.
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
    "handoff-roundtrip": ([
        "Fix the typo in the README.",
        "I'm about to clear. Write a handoff.",
        "/clear",
        "/pumptrack",
    ], False),
    "build-worktree": (["Add a DELETE /cart route that empties a cart."], True),
    # A small tracker edit it may make itself, after one targeted search or a read
    # of that part, or send an agent for; either passes.
    "tracker-edit": ([f"Mark {ITEM} done in the tracker."], False),
}

# Where a case differs: what the project says about landing work, whether the
# orchestrator may write a line in the tracker itself, and how many calls of its
# own it gets when checking the agent's branch is fair.
LANDING = {"build-worktree": "Land work as a commit on a branch off main."}
MAY_EDIT_TRACKER = {"tracker-edit", "build-worktree"}
MAX_CALLS = {"build-worktree": 4}

AGENT_TOOLS = {"Agent", "Task"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
WORK_TOOLS = {"Read", "Grep", "Glob", "Bash", "WebFetch", "WebSearch"}
# A glance or two to write a good brief is fine; more means it did the work itself.
MAX_OWN_CALLS = 3
MAX_OWN_READING = 5000  # characters of tool output, outside what its agents report


def make_project(root, landing):
    files = {
        "CLAUDE.md": f"# Tiny Shop\n\nWork is tracked in TRACKER.md. Tests run with `python3 -m unittest`. {landing}\n",
        ".gitignore": "__pycache__/\n.claude/worktrees/\n",
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
        "tests/__init__.py": "",
        "tests/test_cart.py": '''import unittest

from src import app, storage


class CartTests(unittest.TestCase):
    def setUp(self):
        storage._DATA.clear()

    def test_adding_a_sku_again_raises_its_quantity(self):
        app.handle("POST /cart/items", {"cart_id": 1, "sku": "tee"})
        response = app.handle("POST /cart/items", {"cart_id": 1, "sku": "tee", "quantity": 2})
        self.assertEqual(response["cart"], {"tee": 3})

    def test_removing_a_sku_drops_it(self):
        app.handle("POST /cart/items", {"cart_id": 1, "sku": "mug"})
        response = app.handle("DELETE /cart/items", {"cart_id": 1, "sku": "mug"})
        self.assertEqual(response["cart"], {})
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
           "--permission-mode", "acceptEdits",
           "--allowedTools", "Bash(git *)", "Bash(python3 -m unittest *)",  # git, and Tiny Shop's own test command
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
    """The orchestrator's own tool calls, and what its own reading brought back.
    A subagent's events carry the id of the call that started it."""
    calls, names_by_id, reading = [], {}, ""
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
                reading += content or ""
    return calls, reading


def describe(name, args, root):
    detail = args.get("description") or args.get("command") or args.get("file_path") or args.get("pattern") or ""
    detail = " ".join(str(detail).replace(str(root.resolve()) + "/", "").replace(str(root) + "/", "").split())
    return f"{name}({detail[:50]})" if detail else name


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout.strip()


def tracker_write(name, args):
    """A write to the tracker, by an edit tool or a shell redirect."""
    if name in EDIT_TOOLS:
        return Path(str(args.get("file_path", ""))).name == "TRACKER.md"
    return name == "Bash" and bool(re.search(r">>?\s*\S*TRACKER\.md", args.get("command", "")))


def handoff_written(root, events):
    """Before a clear, the session leaves a handoff for the next one, kept out of
    git. The log folder keeps a copy, since the next session deletes it."""
    handoff = root / ".pumptrack" / "handoff.md"
    if not handoff.exists():
        return ["wrote no handoff"]
    shutil.copy(handoff, root.parent / f"{root.name}-handoff.md")
    problems = []
    exclude = root / git(root, "rev-parse", "--git-path", "info/exclude")
    listed = exclude.exists() and ".pumptrack" in exclude.read_text()
    tried = any("info/exclude" in str(args) for _, args in own_activity(events)[0])
    if not listed and not tried:
        problems.append("didn't keep the handoff out of git")
    last = handoff.read_text().strip().splitlines()[-1].replace("’", "'").lower()
    if "delete this file once you've picked it up" not in last:
        problems.append("the handoff doesn't end by asking to be deleted")
    return problems


def handoff_picked_up(root, events):
    """A fresh session reads the handoff, removes it and reports in pumptrack's
    shape: an outcome line, then a "Needs you" list."""
    problems = []
    copy = root.parent / f"{root.name}-handoff.md"
    handoff = copy.read_text().splitlines() if copy.exists() else []
    reading = own_activity(events)[1]
    if not all(line in reading for line in handoff if line.strip()):
        problems.append("didn't read the handoff itself")
    if (root / ".pumptrack" / "handoff.md").exists():
        problems.append("left the handoff in place")
    text = next((e.get("result") or "" for e in events if e.get("type") == "result"), "")
    lines = text.strip().splitlines()
    if not lines or (len(lines) > 1 and lines[1].strip() and "needs you" not in lines[1].lower()):
        problems.append("its first message doesn't start with a one-line outcome")
    if "needs you" not in text.lower():
        problems.append('its first message has no "Needs you" list')
    return problems


def only_the_tracker(root):
    """Nothing in the checkout differs from the start but the tracker, committed or not."""
    base = git(root, "rev-list", "--max-parents=0", "HEAD")
    changed = set(git(root, "diff", "--name-only", base).split()) | set(
        git(root, "ls-files", "--others", "--directory", "--no-empty-directory", "--exclude-standard").split())
    return [f"changed {', '.join(sorted(stray))}"] if (stray := changed - {"TRACKER.md"}) else []


def landed_on_branch(root, events):
    """A change that lands on a new branch is built in a worktree, which is gone
    afterwards, and the main checkout is untouched beyond a line in the tracker."""
    branches = git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads").split()
    if not any(b != "main" and git(root, "rev-list", f"main..{b}") for b in branches):
        return ["setup: no branch was committed, so there was nothing to check"]
    problems = []
    if git(root, "branch", "--show-current") != "main":
        problems.append("left the main checkout off main")
    problems += only_the_tracker(root)
    if len(git(root, "worktree", "list").splitlines()) > 1:
        problems.append("left a worktree behind")
    return problems


def tracker_marked(root, events):
    """Marking an item done changes that item in the tracker and nothing else."""
    problems = only_the_tracker(root)
    item = re.search(rf"^## {ITEM}\b.*?(?=^## |\Z)", (root / "TRACKER.md").read_text(), re.S | re.M)
    if not item or not re.search(r"status:\s*done", item.group(), re.I):
        problems.append(f"{ITEM} isn't marked done")
    return problems


CHECKS = {"handoff-roundtrip": handoff_picked_up, "build-worktree": landed_on_branch, "tracker-edit": tracker_marked}


def run_case(name, turns, must_delegate, model, workdir):
    root = workdir / name
    root.mkdir()
    make_project(root, LANDING.get(name, "Land work as a commit on main."))
    session, cost, spent, problems = None, 0, 0, []
    for i, prompt in enumerate(["/pumptrack"] + turns):
        if prompt == "/clear":
            problems += handoff_written(root, events)
            session, cost, spent = None, 0, spent + cost
            continue
        events, session, session_cost, failure = run_turn(root, prompt, session, model, workdir / f"{name}-{i}.jsonl")
        cost = session_cost or cost  # a running total for the session, not this turn's share
        if failure:
            problems.append(f"turn {i} {' '.join(failure.split())[:200]}")
            break
    calls, reading = own_activity(events)
    # Looking for a handoff, reading it and removing it is the orchestrator's own
    # job, and so is a line in the tracker where the case allows one.
    own = [(n, a) for n, a in calls if ".pumptrack" not in str(a) and not (name in MAY_EDIT_TRACKER and tracker_write(n, a))]
    own_calls = sum(n in WORK_TOOLS for n, _ in own)
    if must_delegate and not failure and not any(n in AGENT_TOOLS for n, _ in calls):
        problems.append("never sent an agent")
    if any(n in EDIT_TOOLS for n, _ in own):
        problems.append("edited files itself")
    if own_calls > MAX_CALLS.get(name, MAX_OWN_CALLS):
        problems.append(f"made {own_calls} calls of its own work")
    if len(reading) > MAX_OWN_READING:
        problems.append(f"read {len(reading):,} characters itself")
    if name in CHECKS and not failure:
        problems += CHECKS[name](root, events)
    summary = "; ".join(problems) or ("sent an agent" if must_delegate else "stayed light")
    return name, not problems, summary, [describe(n, a, root) for n, a in calls], len(reading), spent + cost


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
    print(f"\nAPI-price equivalent: ${total:.2f}. Projects and session logs: {workdir}")
    sys.exit(0 if all(r[1] for r in results) else 1)


if __name__ == "__main__":
    main()
