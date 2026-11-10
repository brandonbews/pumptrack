---
name: principles
description: Coding principles to follow when writing, reviewing or checking code, and to decide which review findings matter.
---

# Principles

- **Smallest change.** Make the smallest change that solves the problem. Clear out dead code before building on it, and add nothing for cases that haven't come up.
- **Redesign, don't bolt on.** Fit a new requirement in as if it had been there from the start, not as a special case beside the old design. When a new path replaces an old one, move every caller over and delete the old path in the same change.
- **DRY with judgment.** Keep each decision in one place, and remove duplication that would have to change together. Leave code that only looks alike but changes for different reasons. An abstraction that's harder to read than the copies isn't a win.
- **Data shape first.** Choose the data structure before writing the logic, and let it carry the rules (a state machine, a typed model, a lookup table), so wrong states and wrong uses can't be expressed. A growing if/else chain, or a flag that has to stay in sync with another, is the sign to reshape.
- **Easy to follow.** A reader should quickly find where a value comes from and what can change it. Keep layers few and state local, inline wrappers that have only one caller, and keep each interface small compared with the work it hides.
- **Guard the edges.** Check and parse outside input where it enters the system, treat it as hostile there, and keep secrets out of code and logs. Inside the system, trust the types and skip defensive checks.
- **Safe to rerun.** Scripts, migrations, jobs and anything else that changes state and might be retried end in the same state whether they run once, twice, or again after crashing partway through.
- **Match the house style.** Follow the project's stated conventions first, then the code around the change. Don't bring in your own preferences.
- **Prove it works.** Before calling anything done, check the real thing by running it or reading the actual value. "It compiles" or an agent saying it works doesn't count. Work in small steps that each end in a check you can run, such as a test, and script the check when you can so others can rerun it.
- **Fix root causes.** Reproduce the problem, ask why until you reach the cause, and fix it there and everywhere the same pattern appears. Don't add guards that only hide the symptom. If two fixes that rest on the same assumption both fail, question the assumption.
- **Test behavior.** Call the code the way its users do and assert the exact result they'd see. Rewrite or delete any test that would still pass if the code broke.
- **Docs stay true.** After a change, the docs and comments it touches are still true.
- **Code explains itself.** Clarity comes from the code, not comments. Treat every comment in code you're changing, and every urge to write one, as a sign the code should be rewritten: rename, reshape or simplify it until it reads plainly. Comment only a reason that lives outside the code and can't be shown in a name, type or test, such as an outside API's quirk. Formal API docs written as doc comments follow the project's conventions. In review, a comment that explains how code works is a finding against the code.
- **Code stands alone.** Code and comments never point at design docs, plans or tickets, which can be private, move or close. Name the ticket in the commit or PR instead.
