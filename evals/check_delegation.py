#!/usr/bin/env python3
"""Check delegation.py's own pass and fail logic, with no model time.

Builds its throwaway project, puts it in the states a session might leave
behind, feeds canned tool calls through each check, and runs the cases with a
stand-in for the headless session.

    python3 evals/check_delegation.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import delegation as d

work = Path(tempfile.mkdtemp(prefix="check-delegation-"))
failures = []
checks = 0


def expect(label, got, want):
    global checks
    checks += 1
    ok = got == want
    print(("ok  " if ok else "BAD ") + f"{label}: {got}")
    if not ok:
        failures.append(label)


def project(name, landing="Land work as a commit on main."):
    root = work / name
    root.mkdir()
    d.make_project(root, landing)
    return root


def commit(root, message):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=e", "-c", "user.email=e@e", "commit", "-qam", message], check=True)


def tool_events(calls, result_text=""):
    """Canned stream-json events: own tool calls with results, then a result."""
    events = []
    for i, (name, args, output) in enumerate(calls):
        events.append({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": args}]}})
        events.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": output}]}})
    events.append({"type": "result", "result": result_text})
    return events


# The project itself: its tests pass, and git is clean.
root = project("base")
test = subprocess.run([sys.executable, "-m", "unittest"], cwd=root, capture_output=True, text=True)
expect("tests pass in Tiny Shop", test.returncode, 0)
expect("clean after tests (pycache ignored)", d.git(root, "status", "--porcelain"), "")
expect("exclude path is relative to root", (root / d.git(root, "rev-parse", "--git-path", "info/exclude")).exists(), True)
expect("default landing", "commit on main." in (root / "CLAUDE.md").read_text(), True)
expect("worktree landing", "branch off main." in (project("landing", d.LANDING["build-worktree"]) / "CLAUDE.md").read_text(), True)

# tracker_marked
root = project("tracker-edit")
expect("tracker: untouched fails", d.tracker_marked(root, []), [f"{d.ITEM} isn't marked done"])
text = (root / "TRACKER.md").read_text()
head, _, rest = text.partition(f"## {d.ITEM}:")
rest = rest.replace("Status: open", "Status: done", 1)
(root / "TRACKER.md").write_text(head + f"## {d.ITEM}:" + rest)
expect("tracker: marked done passes", d.tracker_marked(root, []), [])
expect(f"tracker: {d.ITEM} was open", "Status: open" in text.partition(f"## {d.ITEM}:")[2][:60], True)
(root / "README.md").write_text("changed\n")
(root / "notes.md").write_text("new\n")
expect("tracker: other changes fail", d.tracker_marked(root, []), ["changed README.md, notes.md"])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "--", "README.md"], check=True)
(root / "notes.md").unlink()
commit(root, "Mark done")
expect("tracker: committed edit still passes", d.tracker_marked(root, []), [])
(root / "TRACKER.md").write_text((root / "TRACKER.md").read_text().replace(f"## {d.ITEM}:", f"## {d.ITEM}x:"))
expect("tracker: item missing fails", d.tracker_marked(root, []), [f"{d.ITEM} isn't marked done"])

# landed_on_branch
root = project("build-worktree", d.LANDING["build-worktree"])
expect("branch: nothing committed is a setup failure", d.landed_on_branch(root, []), ["setup: no branch was committed, so there was nothing to check"])
subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", ".claude/worktrees/cart", "-b", "empty-cart"], check=True)
expect("branch: branch without commits is still setup", d.landed_on_branch(root, []), ["setup: no branch was committed, so there was nothing to check"])
wt = root / ".claude" / "worktrees" / "cart"
(wt / "src" / "cart.py").write_text((wt / "src" / "cart.py").read_text() + "\n\ndef empty(request):\n    return {'status': 200}\n")
commit(wt, "Add DELETE /cart")
expect("branch: worktree left behind fails", d.landed_on_branch(root, []), ["left a worktree behind"])
subprocess.run(["git", "-C", str(root), "worktree", "remove", str(wt)], check=True)
expect("branch: committed, removed, main clean passes", d.landed_on_branch(root, []), [])
(root / "README.md").write_text("dirty\n")
expect("branch: dirty main fails", d.landed_on_branch(root, []), ["changed README.md"])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "--", "README.md"], check=True)
# A tracker entry appended on main and left uncommitted, as the orchestrator leaves it.
with open(root / "TRACKER.md", "a") as f:
    f.write("\n## SHOP-081: Feature in cart #81\n\nStatus: in review\n\nAdd a DELETE /cart route. Built on branch empty-cart, not yet merged.\n")
expect("branch: an uncommitted tracker line on main passes", d.landed_on_branch(root, []), [])
(root / "src" / "cart.py").write_text((root / "src" / "cart.py").read_text() + "# stray\n")
expect("branch: a stray edit to src fails", d.landed_on_branch(root, []), ["changed src/cart.py"])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "--", "src/cart.py"], check=True)
commit(root, "Track SHOP-081")
expect("branch: a committed tracker line on main passes", d.landed_on_branch(root, []), [])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "empty-cart"], check=True)
expect("branch: main checkout on the branch fails", d.landed_on_branch(root, []), ["left the main checkout off main", "changed src/cart.py"])

# handoff_written
root = project("handoff-roundtrip")
expect("handoff: none written fails", d.handoff_written(root, []), ["wrote no handoff"])
handoff = root / ".pumptrack" / "handoff.md"
handoff.parent.mkdir()
body = "# Handoff\n\nA pumptrack session. Start with /pumptrack.\n\n## Read first\n\n- TRACKER.md\n\n## Open asks\n\n- None\n\n"
handoff.write_text(body + "Delete this file once you've picked it up.\n")
expect("handoff: not excluded and not tried fails", d.handoff_written(root, []), ["didn't keep the handoff out of git"])
tried = tool_events([("Bash", {"command": "echo '.pumptrack/' >> .git/info/exclude"}, "Permission denied")])
expect("handoff: a denied attempt passes", d.handoff_written(root, tried), [])
tried_edit = tool_events([("Edit", {"file_path": str(root / ".git/info/exclude"), "old_string": "x", "new_string": "y"}, "Permission denied")])
expect("handoff: a denied edit passes", d.handoff_written(root, tried_edit), [])
sub = tool_events([("Bash", {"command": "echo '.pumptrack/' >> .git/info/exclude"}, "ok")])
sub[0]["parent_tool_use_id"] = "agent"
sub[1]["parent_tool_use_id"] = "agent"
expect("handoff: a subagent's attempt doesn't count", d.handoff_written(root, sub), ["didn't keep the handoff out of git"])
with open(root / ".git" / "info" / "exclude", "a") as f:
    f.write(".pumptrack/\n")
expect("handoff: listed in exclude passes", d.handoff_written(root, []), [])
expect("handoff: a copy was kept", (work / "handoff-roundtrip-handoff.md").read_text() == handoff.read_text(), True)
handoff.write_text(body + "**Delete this file once you’ve picked it up.**\n")
expect("handoff: bold closing line with a curly quote passes", d.handoff_written(root, []), [])
handoff.write_text(body + "That's everything.\n")
expect("handoff: wrong closing line fails", d.handoff_written(root, []), ["the handoff doesn't end by asking to be deleted"])
handoff.write_text(body + "Delete this file once you've picked it up.\n")
d.handoff_written(root, [])  # refresh the copy

# handoff_picked_up
numbered = "\n".join(f"{i + 1:6}\t{line}" for i, line in enumerate(handoff.read_text().splitlines()))
good = "Picked up the handoff: the README typo landed on main, nothing is running.\n\n**Needs you**\n\n1. Nothing.\n\nDetails: ...\n"
read_then_rm = [("Read", {"file_path": str(handoff)}, numbered), ("Bash", {"command": "rm .pumptrack/handoff.md"}, "")]
expect("pickup: handoff still there fails", d.handoff_picked_up(root, tool_events(read_then_rm, good)), ["left the handoff in place"])
handoff.unlink()
expect("pickup: read, removed, good shape passes", d.handoff_picked_up(root, tool_events(read_then_rm, good)), [])
cat = [("Bash", {"command": "cat .pumptrack/handoff.md"}, (work / "handoff-roundtrip-handoff.md").read_text())]
expect("pickup: cat counts as reading", d.handoff_picked_up(root, tool_events(cat, good)), [])
expect("pickup: not read fails", d.handoff_picked_up(root, tool_events([("Bash", {"command": "git log"}, "abc")], good)), ["didn't read the handoff itself"])
sub = tool_events(read_then_rm, good)
for e in sub[:-1]:
    e["parent_tool_use_id"] = "agent"
expect("pickup: an agent reading it doesn't count", d.handoff_picked_up(root, sub), ["didn't read the handoff itself"])
expect("pickup: no Needs you fails", d.handoff_picked_up(root, tool_events(read_then_rm, "Picked up the handoff.\n\nAll good.\n")), ['its first message has no "Needs you" list'])
expect("pickup: paragraph first fails", d.handoff_picked_up(root, tool_events(read_then_rm, "I read the handoff.\nIt said the typo landed.\n\n**Needs you**\n- Nothing\n")), ["its first message doesn't start with a one-line outcome"])
expect("pickup: outcome then Needs you on the next line passes", d.handoff_picked_up(root, tool_events(read_then_rm, "Picked up the handoff.\n**Needs you:** Nothing.\n")), [])
expect("pickup: empty message fails", d.handoff_picked_up(root, tool_events(read_then_rm, "")), ["its first message doesn't start with a one-line outcome", 'its first message has no "Needs you" list'])
expect("pickup: first result judged, not a later one", d.handoff_picked_up(root, tool_events(read_then_rm, good) + [{"type": "result", "result": "no shape"}]), [])

# run_case with a stand-in for run_turn: the /clear flow, the edit exception and the call budget.
log = []


def fake_turn(cwd, prompt, session, model, logfile):
    log.append((prompt, session))
    if prompt == "I'm about to clear. Write a handoff.":
        (cwd / ".pumptrack").mkdir(exist_ok=True)
        (cwd / ".pumptrack" / "handoff.md").write_text(body + "Delete this file once you've picked it up.\n")
        return tool_events([("Write", {"file_path": str(cwd / ".pumptrack/handoff.md")}, "ok"),
                            ("Bash", {"command": "echo .pumptrack/ >> .git/info/exclude"}, "denied")], "Handoff ready."), "s1", 0.5, None
    if prompt == "/pumptrack" and session is None and (cwd / ".pumptrack" / "handoff.md").exists():
        text = (cwd / ".pumptrack" / "handoff.md").read_text()
        (cwd / ".pumptrack" / "handoff.md").unlink()
        return tool_events([("Bash", {"command": "ls .pumptrack; cat .pumptrack/handoff.md"}, text),
                            ("Read", {"file_path": str(cwd / "README.md")}, "readme"),
                            ("Bash", {"command": "git log --oneline"}, "abc"),
                            ("Read", {"file_path": str(cwd / "TRACKER.md"), "limit": 20}, "x" * 400),
                            ("Bash", {"command": "rm .pumptrack/handoff.md"}, "")], good), "s2", 0.9, None
    if prompt.startswith("Mark "):
        text = (cwd / "TRACKER.md").read_text()
        head, _, rest = text.partition(f"## {d.ITEM}:")
        (cwd / "TRACKER.md").write_text(head + f"## {d.ITEM}:" + rest.replace("Status: open", "Status: done", 1))
        return tool_events([("Grep", {"pattern": d.ITEM}, f"41:## {d.ITEM}"), ("Edit", {"file_path": str(cwd / "TRACKER.md")}, "ok")], "Done."), "s3", 0.1, None
    return tool_events([], "ok"), session or "s0", 0.1, None


real_run_turn = d.run_turn
d.run_turn = fake_turn
work2 = Path(tempfile.mkdtemp(prefix="check-delegation-run-"))
name, passed, summary, calls, reading, cost = d.run_case("handoff-roundtrip", *d.CASES["handoff-roundtrip"], None, work2)
expect("run: handoff roundtrip passes end to end", (passed, summary), (True, "stayed light"))
expect("run: both sessions' costs count", round(cost, 2), 1.4)
expect("run: the fresh session had no session id", [s for p, s in log if p == "/pumptrack"], [None, None])
expect("run: /clear was not sent to claude", any(p == "/clear" for p, s in log), False)
expect("run: handoff calls left out of the count, four others counted", "calls of its own work" in summary, False)
expect("run: a copy of the handoff sits beside the logs", (work2 / "handoff-roundtrip-handoff.md").exists(), True)
log.clear()
name, passed, summary, calls, reading, cost = d.run_case("tracker-edit", *d.CASES["tracker-edit"], None, work2)
expect("run: tracker edit by itself passes", (passed, summary), (True, "stayed light"))
name, passed, summary, calls, reading, cost = d.run_case("fix", *d.CASES["fix"], None, work2)
expect("run: other cases unchanged (fix with no agent fails)", (passed, summary), (False, "never sent an agent"))
log.clear()
name, passed, summary, calls, reading, cost = d.run_case("build-worktree", *d.CASES["build-worktree"], None, work2)
expect("run: build-worktree with nothing landed", summary, "never sent an agent; setup: no branch was committed, so there was nothing to check")
expect("run: build-worktree project says branch", "branch off main" in (work2 / "build-worktree" / "CLAUDE.md").read_text(), True)

# Every session allows git and the project's test command, nothing else.
captured = {}


class Done:
    stdout, stderr, returncode = "", "", 0


real_subprocess_run = d.subprocess.run
d.subprocess.run = lambda cmd, **kw: (captured.setdefault("cmd", cmd), Done)[1]
real_run_turn(work2 / "tracker-edit", "/pumptrack", None, None, work2 / "x.jsonl")
d.subprocess.run = real_subprocess_run
cmd = captured["cmd"]
allowed = cmd[cmd.index("--allowedTools") + 1:cmd.index("--permission-prompts")]
expect("run: every session allows git and the tests only", allowed, ["Bash(git *)", "Bash(python3 -m unittest *)"])


# Own edits: the tracker is allowed in tracker-edit and build-worktree, nothing else anywhere.
def editing(path):
    return lambda cwd, prompt, session, model, logfile: (tool_events([("Edit", {"file_path": str(cwd / path)}, "ok")], "ok"), "s", 0.1, None)


d.run_turn = editing("x")
name, passed, summary, *_ = d.run_case("tracker", *d.CASES["tracker"], None, work2)
expect("run: an own edit still fails elsewhere", summary, "edited files itself")
work3 = Path(tempfile.mkdtemp(prefix="check-delegation-edits-"))
d.run_turn = editing("TRACKER.md")
name, passed, summary, *_ = d.run_case("build-worktree", *d.CASES["build-worktree"], None, work3)
expect("run: build-worktree may edit the tracker itself", "edited files itself" in summary, False)
d.run_turn = editing("src/cart.py")
name, passed, summary, *_ = d.run_case("tracker-edit", *d.CASES["tracker-edit"], None, work3)
expect("run: tracker-edit may not edit src itself", "edited files itself" in summary, True)
shutil.rmtree(work3)

# A shell redirect into the tracker is the same allowed write, not a work call.
expect("write: Edit of the tracker", d.tracker_write("Edit", {"file_path": "/p/TRACKER.md"}), True)
expect("write: Edit elsewhere", d.tracker_write("Edit", {"file_path": "/p/src/cart.py"}), False)
expect("write: printf >> TRACKER.md", d.tracker_write("Bash", {"command": "printf '\\n## SHOP-081\\n' >> TRACKER.md && tail -3 TRACKER.md"}), True)
expect("write: redirect with a path", d.tracker_write("Bash", {"command": "echo x >/p/TRACKER.md"}), True)
expect("write: grep of the tracker is not a write", d.tracker_write("Bash", {"command": "grep -n SHOP TRACKER.md | tail -2"}), False)
expect("write: redirect elsewhere", d.tracker_write("Bash", {"command": "echo x >> notes.md"}), False)


# The call budget: 4 for build-worktree, 3 elsewhere. The stand-in lands the branch by hand.
def landing(prompt, cwd):
    if prompt.startswith("Add a DELETE"):
        wt = cwd / ".claude" / "worktrees" / "cart"
        subprocess.run(["git", "-C", str(cwd), "worktree", "add", "-q", str(wt), "-b", "clear-cart-route"], check=True)
        (wt / "src" / "app.py").write_text((wt / "src" / "app.py").read_text() + "# route\n")
        commit(wt, "Add DELETE /cart")
        subprocess.run(["git", "-C", str(cwd), "worktree", "remove", str(wt)], check=True)
        with open(cwd / "TRACKER.md", "a") as f:
            f.write("\n## SHOP-081: Feature in cart #81\n\nStatus: in review\n")


def budget(n):
    def turn(cwd, prompt, session, model, logfile):
        landing(prompt, cwd)
        calls = [("Agent", {"description": "Build"}, "launched")] + [("Bash", {"command": "git log --oneline -1"}, "abc")] * n
        return tool_events(calls, "ok"), "s", 0.1, None
    return turn


for n, want in [(4, "sent an agent"), (5, "made 5 calls of its own work")]:
    d.run_turn = budget(n)
    work4 = Path(tempfile.mkdtemp(prefix="check-delegation-budget-"))
    name, passed, summary, *_ = d.run_case("build-worktree", *d.CASES["build-worktree"], None, work4)
    expect(f"budget: build-worktree with {n} counted calls", summary, want)
    shutil.rmtree(work4)
d.run_turn = budget(4)
work4 = Path(tempfile.mkdtemp(prefix="check-delegation-budget-"))
name, passed, summary, *_ = d.run_case("fix", *d.CASES["fix"], None, work4)
expect("budget: fix with 4 counted calls still fails", summary, "made 4 calls of its own work")
shutil.rmtree(work4)

shutil.rmtree(work)
shutil.rmtree(work2)
print()
if failures:
    print(f"{len(failures)} of {checks} checks failed: " + "; ".join(failures))
    sys.exit(1)
print(f"{checks} checks passed")
