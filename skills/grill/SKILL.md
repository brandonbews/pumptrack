---
name: grill
description: Interview the user about how a feature or change will work and what done looks like, in rounds of questions, each with a recommended answer, until nothing is left open, then write its tickets. Use when the user wants to stress-test a plan before building, or asks to be grilled.
---

# Grill

**Your goal:** reach a shared understanding with the user of how a feature or change will work and what done looks like, with nothing silently assumed, and leave it written down as tickets.

## Before asking

Read the plan, the code it touches, the tracker, and the project's glossary if it keeps one: its instructions say where, or there's a `GLOSSARY.md`. Finding facts is your job, never the user's. Send an agent for searches that would fill your context.

## Ask in rounds

Map what's undecided about how it will work as a tree of decisions, each branching into the ones that hang off it: what happens when the user does each thing, what they see, and the edge cases. How to build it is yours to decide, so ask about that only where it changes what the user gets. Each round, ask every question whose prerequisites are settled, and none that turns on another still open. Number each, and give your recommended answer the way `communication` says. Ask only about decisions the behavior turns on; when the user says a thing doesn't matter, record that as their call and move on.

Each round's answers open the decisions that hung on them, so ask those next. A lookup still running holds back only the questions that need it.

## Sharpen the words

As you go:

- When the user uses a word the glossary defines differently, say so and ask which they mean.
- When a word is fuzzy or covers two things, offer one precise word for each.
- Make up concrete edge cases that test where one thing ends and the next begins.
- When the user says how something works, check the code, and raise it if the code disagrees.

When a term is settled and the project keeps a glossary, write it there right away: the term, a line or two on what it is (not what it does), and the words to avoid. Only terms specific to the project, never implementation details.

## Finish

You're done when no decision is left open and the user confirms you understand each other. Then write the tickets where the project tracks work, asking where if its instructions don't say. Each is a step small enough to build and check on its own, and the full record of that step, detailed enough for a fresh agent to pick up with nothing else:

- What it's for, and how it behaves: each decision made, and what's out of scope.
- Where in the code it lands, and what it waits on.
- How to tell it's done, as behavior a test can check.

A page showing the result to the user is a view of the tickets, not the record, so nothing lives only there. Don't build any of it.

## Report

Report the way `communication` says, with an outcome such as "4 tickets written". Then where they are, and any terms added to the glossary.
