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


def land_fix(root):
    """Lands the README fix as a builder does: committed in a checkout of its own, which is then removed, and main fast-forwarded to it."""
    wt = root / ".claude" / "worktrees" / "typo"
    subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", str(wt), "-b", "typo"], check=True)
    (wt / "README.md").write_text((wt / "README.md").read_text().replace("wiht", "with"))
    commit(wt, "Fix the typo")
    subprocess.run(["git", "-C", str(root), "worktree", "remove", str(wt)], check=True)
    subprocess.run(["git", "-C", str(root), "merge", "-q", "--ff-only", "typo"], check=True)


def tool_events(calls, result_text="", denied=()):
    """Canned stream-json events: own tool calls with results, then a result that lists the calls denied."""
    events = []
    for i, (name, args, output) in enumerate(calls):
        events.append({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"t{i}", "name": name, "input": args}]}})
        events.append({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": output}]}})
    events.append({"type": "result", "result": result_text, "permission_denials": [{"tool_use_id": i} for i in denied]})
    return events


# The project itself: its tests pass, and git is clean.
root = project("base")
test = subprocess.run([sys.executable, "-m", "unittest"], cwd=root, capture_output=True, text=True)
expect("tests pass in Tiny Shop", test.returncode, 0)
expect("clean after tests (pycache ignored)", d.git(root, "status", "--porcelain"), "")
expect("default landing", "commit on main." in (root / "CLAUDE.md").read_text(), True)
expect("worktree landing", "branch off main." in (project("landing", d.LANDING["build-branch"]) / "CLAUDE.md").read_text(), True)

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
root = project("build-branch", d.LANDING["build-branch"])
expect("branch: nothing committed is a setup failure", d.landed_on_branch(root, []), ["setup: no branch was committed, so there was nothing to check"])
subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", ".claude/worktrees/cart", "-b", "empty-cart"], check=True)
expect("branch: branch without commits is still setup", d.landed_on_branch(root, []), ["setup: no branch was committed, so there was nothing to check"])
wt = root / ".claude" / "worktrees" / "cart"
(wt / "src" / "cart.py").write_text((wt / "src" / "cart.py").read_text() + "\n\ndef empty(request):\n    return {'status': 200}\n")
commit(wt, "Add DELETE /cart")
expect("checkout: a worktree left behind fails, whoever made it", d.checkout_left_alone(root), ["left a worktree behind"])
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

# checkout_left_alone: the same project, whose main checkout has so far only committed a tracker line.
expect("checkout: a tracker line committed on main passes", d.checkout_left_alone(root), [])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "in-place"], check=True)
expect("checkout: left on another branch fails", d.checkout_left_alone(root), ["left the main checkout off main", "switched the main checkout to another branch"])
subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True)
expect("checkout: switched away and back fails", d.checkout_left_alone(root), ["switched the main checkout to another branch"])
root = project("fast-forward")
land_fix(root)
expect("checkout: fast-forwarding main to a commit made elsewhere passes", d.checkout_left_alone(root), [])
expect("branch: but where the work was to stay on a branch, that fails, and not as setup", d.landed_on_branch(root, []), ["changed README.md"])
with open(root / "TRACKER.md", "a") as f:
    f.write("\n## SHOP-081: Chore in receipts #81\n\nStatus: open\n")
expect("checkout: an uncommitted tracker line passes", d.checkout_left_alone(root), [])
subprocess.run(["git", "-C", str(root), "-c", "user.name=e", "-c", "user.email=e@e", "stash", "-q"], check=True)
expect("checkout: the user's tracker line stashed away fails", d.checkout_left_alone(root), ["left a stash behind"])
subprocess.run(["git", "-C", str(root), "stash", "drop", "-q"], check=True)
(root / "README.md").write_text("edited here, never committed\n")
(root / "notes.md").write_text("new\n")
expect("checkout: uncommitted work left behind fails", d.checkout_left_alone(root), ["left uncommitted changes to README.md, notes.md in the main checkout"])
root = project("built-in-place")
(root / "src" / "cart.py").write_text((root / "src" / "cart.py").read_text() + "# built here\n")
commit(root, "Build in the main checkout")
expect("checkout: work committed in the main checkout fails", d.checkout_left_alone(root), ["committed work in the main checkout"])

# handoff_written
root = project("handoff-roundtrip")
expect("handoff: none written fails", d.handoff_written(root, []), ["wrote no handoff"])
handoff = root / ".pumptrack" / "handoff.md"
handoff.parent.mkdir()
body = "# Handoff\n\nA pumptrack session. Start with /pumptrack.\n\n## Read first\n\n- TRACKER.md\n\n## Open asks\n\n- None\n\n"
handoff.write_text(body + "Delete this file once you've picked it up.\n")
expect("handoff: not ignored fails", d.handoff_written(root, []), ["didn't keep the handoff out of git"])
(handoff.parent / ".gitignore").write_text("*\n")
expect("handoff: a folder that ignores itself passes", d.handoff_written(root, []), [])
expect("handoff: and leaves git clean", d.git(root, "status", "--porcelain"), "")
expect("handoff: a copy was kept", (work / "handoff-roundtrip-handoff.md").read_text() == handoff.read_text(), True)

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

# started_empty
look = ("Bash", {"command": "ls .pumptrack"}, "ls: .pumptrack: No such file or directory")
expect("start: a look for a handoff passes", d.started_empty(root, tool_events([look])), [])
expect("start: sending an agent fails", d.started_empty(root, tool_events([look, ("Agent", {"description": "Read the tracker"}, "launched")])), ["sent an agent before it was asked for anything"])
expect("start: more than a glance fails", d.started_empty(root, tool_events([look, ("Bash", {"command": "head -20 TRACKER.md"}, "x" * 600)])), ["read 641 characters before it was asked for anything"])
refused = ("Bash", {"command": "ls .pumptrack && cat .pumptrack/handoff.md"}, "Permission for this tool use was denied. " + "x" * 800)
expect("start: a denial's own text isn't reading", d.started_empty(root, tool_events([look, refused], denied=["t1"])), [])

# run_case with a stand-in for run_turn: the /clear flow, the edit exception and the call budget.
log = []


def fake_turn(cwd, prompt, session, model, logfile):
    log.append((prompt, session))
    if prompt == d.FIX:
        land_fix(cwd)
        return tool_events([("Agent", {"description": "Fix the typo", "isolation": "worktree"}, "launched")], "Landed.", denied=["a", "b"]), "s1", 0.3, None
    if prompt == "I'm about to clear. Write a handoff.":
        (cwd / ".pumptrack").mkdir(exist_ok=True)
        (cwd / ".pumptrack" / "handoff.md").write_text(body + "Delete this file once you've picked it up.\n")
        (cwd / ".pumptrack" / ".gitignore").write_text("*\n")
        return tool_events([("Write", {"file_path": str(cwd / ".pumptrack/handoff.md")}, "ok"),
                            ("Write", {"file_path": str(cwd / ".pumptrack/.gitignore")}, "ok")], "Handoff ready."), "s1", 0.5, None
    if prompt == "/pumptrack" and session is None and (cwd / ".pumptrack" / "handoff.md").exists():
        text = (cwd / ".pumptrack" / "handoff.md").read_text()
        (cwd / ".pumptrack" / "handoff.md").unlink()
        return tool_events([("Bash", {"command": "ls .pumptrack; cat .pumptrack/handoff.md"}, text),
                            ("Read", {"file_path": str(cwd / "README.md")}, "readme"),
                            ("Bash", {"command": "git log --oneline"}, "abc"),
                            ("Read", {"file_path": str(cwd / "TRACKER.md"), "limit": 20}, "x" * 400),
                            ("Bash", {"command": "rm .pumptrack/handoff.md"}, "")], good, denied=["b", "c"]), "s2", 0.9, None
    if prompt.startswith("Mark "):
        text = (cwd / "TRACKER.md").read_text()
        head, _, rest = text.partition(f"## {d.ITEM}:")
        (cwd / "TRACKER.md").write_text(head + f"## {d.ITEM}:" + rest.replace("Status: open", "Status: done", 1))
        return tool_events([("Grep", {"pattern": d.ITEM}, f"41:## {d.ITEM}"), ("Edit", {"file_path": str(cwd / "TRACKER.md")}, "ok")], "Done."), "s3", 0.1, None
    return tool_events([], "ok"), session or "s0", 0.1, None


real_run_turn = d.run_turn
d.run_turn = fake_turn
work2 = Path(tempfile.mkdtemp(prefix="check-delegation-run-"))
name, passed, summary, calls, reading, cost, denied = d.run_case("handoff-roundtrip", *d.CASES["handoff-roundtrip"], None, work2)
expect("run: handoff roundtrip passes end to end", (passed, summary), (True, "stayed light"))
expect("run: denied calls are counted once each, across turns", denied, 3)
shop = d.folder(work2, "handoff-roundtrip")
expect("run: the project sits in the case's folder", [p for p in work2.iterdir() if p.is_dir()], [shop])
expect("run: whose path doesn't name the case", "handoff" in str(shop), False)
expect("run: each case gets a folder of its own", len({d.folder(work2, case) for case in d.CASES}), len(d.CASES))
expect("run: both sessions' costs count", round(cost, 2), 1.4)
expect("run: the fresh session had no session id", [s for p, s in log if p == "/pumptrack"], [None, None])
expect("run: /clear was not sent to claude", any(p == "/clear" for p, s in log), False)
expect("run: handoff calls left out of the count, four others counted", "calls of its own work" in summary, False)
expect("run: a copy of the handoff sits beside the logs", (work2 / f"{shop.name}-handoff.md").exists(), True)
log.clear()
name, passed, summary, *_ = d.run_case("tracker-edit", *d.CASES["tracker-edit"], None, work2)
expect("run: tracker edit by itself passes", (passed, summary), (True, "stayed light"))
name, passed, summary, *_ = d.run_case("fix", *d.CASES["fix"], None, work2)
expect("run: a fix sent to an agent and landed on main passes", (passed, summary), (True, "sent an agent"))
name, passed, summary, *_ = d.run_case("start", *d.CASES["start"], None, work2)
expect("run: start with nothing done passes", (passed, summary), (True, "stayed light"))
log.clear()
name, passed, summary, *_ = d.run_case("build-branch", *d.CASES["build-branch"], None, work2)
expect("run: build-branch with nothing landed", summary, "never sent an agent; setup: no branch was committed, so there was nothing to check")
expect("run: build-branch project says branch", "branch off main" in (d.folder(work2, "build-branch") / "CLAUDE.md").read_text(), True)

# Every session allows git and the project's test command, nothing else.
captured = {}


class Done:
    stdout, stderr, returncode = "", "", 0


real_subprocess_run = d.subprocess.run
d.subprocess.run = lambda cmd, **kw: (captured.setdefault("cmd", cmd), Done)[1]
real_run_turn(d.folder(work2, "tracker-edit"), "/pumptrack", None, None, work2 / "x.jsonl")
d.subprocess.run = real_subprocess_run
cmd = captured["cmd"]
allowed = cmd[cmd.index("--allowedTools") + 1:cmd.index("--permission-prompts")]
expect("run: every session allows git and the tests only", allowed, ["Bash(git *)", "Bash(python3 -m unittest *)"])


# Own edits: a line in the tracker is allowed in every case, nothing else anywhere.
def editing(path):
    return lambda cwd, prompt, session, model, logfile: (tool_events([("Edit", {"file_path": str(cwd / path)}, "ok")], "ok"), "s", 0.1, None)


d.run_turn = editing("x")
name, passed, summary, *_ = d.run_case("tracker", *d.CASES["tracker"], None, work2)
expect("run: an own edit still fails elsewhere", summary, "edited files itself")
work3 = Path(tempfile.mkdtemp(prefix="check-delegation-edits-"))
sent = lambda cwd, prompt, session, model, logfile: (tool_events([("Agent", {"description": "Do it"}, "launched")], "ok"), "s", 0.1, None)
d.run_turn = sent
name, passed, summary, *_ = d.run_case("fix", *d.CASES["fix"], None, work3)
expect("run: a fix sent to an agent in the user's checkout, which never landed, fails", summary, "didn't start the build in a checkout of its own; the README typo is still on main")
name, passed, summary, *_ = d.run_case("start", *d.CASES["start"], None, work3)
expect("run: start that sends an agent fails", summary, "sent an agent before it was asked for anything")
shutil.rmtree(work3)  # the fix case's project and its origin
work3.mkdir()
by_hand = [("Bash", {"command": "git worktree add .claude/worktrees/typo -b typo"}, ""), ("Agent", {"description": "Fix the typo", "isolation": "worktree"}, "launched")]
d.run_turn = lambda cwd, prompt, session, model, logfile: (prompt == d.FIX and land_fix(cwd), (tool_events(by_hand, "ok"), "s", 0.1, None))[1]
name, passed, summary, *_ = d.run_case("fix", *d.CASES["fix"], None, work3)
expect("run: a worktree the orchestrator made by hand fails", summary, "made a worktree by hand")
shutil.rmtree(work3)  # the fix case's project and its origin
work3.mkdir()
d.run_turn = editing("TRACKER.md")
name, passed, summary, *_ = d.run_case("fix", *d.CASES["fix"], None, work3)
expect("run: any case may edit the tracker itself", "edited files itself" in summary, False)
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


# built_on_main: the project's origin is a commit behind main, and a build has to start from main.
root = project("unpushed")
d.make_unpushed(root)
expect("base: main starts one commit ahead of origin, with the checkout left alone", (d.git(root, "rev-list", "--count", "origin/main..main"), d.checkout_left_alone(root)), ("1", []))
expect("base: nothing built yet passes", d.built_on_main(root), [])
land_fix(root)
expect("base: a fix built on main and fast-forwarded passes", d.built_on_main(root), [])
stale = root / ".claude" / "worktrees" / "stale"
subprocess.run(["git", "-C", str(root), "worktree", "add", "-q", "--no-track", str(stale), "-b", "stale", "origin/main"], check=True)
subprocess.run(["git", "-C", str(root), "branch", "--no-track", "tool-made", "origin/main"], check=True)
expect("base: branches left where origin is, with nothing built on them, pass", d.built_on_main(root), [])
(stale / "src" / "cart.py").write_text((stale / "src" / "cart.py").read_text() + "# built on origin\n")
commit(stale, "Build on origin's main")
subprocess.run(["git", "-C", str(root), "worktree", "remove", str(stale)], check=True)
expect("base: a branch built on origin's main fails", d.built_on_main(root), ["built on origin's main, not on main as committed"])
subprocess.run(["git", "-C", str(root), "-c", "user.name=e", "-c", "user.email=e@e", "merge", "-q", "--no-edit", "stale"], check=True)
subprocess.run(["git", "-C", str(root), "branch", "-q", "-D", "stale"], check=True)
expect("base: and still fails once merged into main and deleted", d.built_on_main(root), ["built on origin's main, not on main as committed"])

# Finishing a build's landing is the orchestrator's job too, so it isn't counted as work of its own.
expect("finish: fast-forwarding to a builder's commit", d.finishes_a_build("Bash", {"command": "git merge --ff-only 71c3dc8 && git log --oneline -2"}), True)
expect("finish: removing a builder's checkout", d.finishes_a_build("Bash", {"command": "git worktree remove .claude/worktrees/agent-a1 && git branch -d worktree-agent-a1"}), True)
expect("finish: a look at the worktrees is still a call of its own", d.finishes_a_build("Bash", {"command": "git worktree list"}), False)
expect("finish: a quiet fast-forward", d.finishes_a_build("Bash", {"command": "git merge -q --ff-only typo"}), True)
expect("finish: a merge that isn't a fast-forward is still a call of its own", d.finishes_a_build("Bash", {"command": "git merge typo"}), False)

# The call budget: 4 calls of its own. The stand-in lands the branch by hand.
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
        calls = [("Agent", {"description": "Build", "isolation": "worktree"}, "launched"), ("Bash", {"command": "git worktree remove .claude/worktrees/agent-a1"}, "")]
        calls += [("Bash", {"command": "git log --oneline -1"}, "abc")] * n
        return tool_events(calls, "ok"), "s", 0.1, None
    return turn


for n, want in [(4, "sent an agent"), (5, "made 5 calls of its own work")]:
    d.run_turn = budget(n)
    work4 = Path(tempfile.mkdtemp(prefix="check-delegation-budget-"))
    name, passed, summary, *_ = d.run_case("build-branch", *d.CASES["build-branch"], None, work4)
    expect(f"budget: build-branch with {n} counted calls", summary, want)
    shutil.rmtree(work4)

shutil.rmtree(work)
shutil.rmtree(work2)
print()
if failures:
    print(f"{len(failures)} of {checks} checks failed: " + "; ".join(failures))
    sys.exit(1)
print(f"{checks} checks passed")
