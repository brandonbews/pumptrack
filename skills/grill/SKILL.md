---
name: grill
description: Interview the user about a plan or design in rounds of questions, each with a recommended answer, until nothing is left open, then write the plan and its tickets. Use when the user wants to stress-test a plan before building, or asks to be grilled.
---

# Grill

**Your goal:** reach a shared understanding of a plan with the user, with every decision theirs and nothing silently assumed, and leave it written down as a plan and tickets.

## Before asking

Read the plan, the code it touches, the tracker, and the project's glossary if it keeps one: its instructions say where, or there's a `GLOSSARY.md`. Finding facts is your job, never the user's. Look up anything the code, docs or tools can answer, and send an agent for searches that would fill your context.

## Ask in rounds

Map the plan as a tree of decisions, each branching into the ones that hang off it. Each round, ask every question whose prerequisites are settled, and none that turns on another still open. Number each, and give your recommended answer the way `communication` says. Ask only about decisions the plan turns on; when the user says a thing doesn't matter, record that as their call and move on.

Each round's answers open the decisions that hung on them, so ask those next. A lookup still running holds back only the questions that need it.

## Sharpen the words

As you go:

- When the user uses a word the glossary defines differently, say so and ask which they mean.
- When a word is fuzzy or covers two things, offer one precise word for each.
- Make up concrete edge cases that test where one thing ends and the next begins.
- When the user says how something works, check the code, and raise it if the code disagrees.

When a term is settled and the project keeps a glossary, write it there right away: the term, a line or two on what it is (not what it does), and the words to avoid. Only terms specific to the project, never implementation details.

## Finish

You're done when no decision is left open and the user confirms you understand each other. Then write the plan where the project keeps docs and its tickets where it tracks work, and ask if its instructions say neither. The plan holds the goal, each decision with its reason, and what's out of scope. Each ticket is a step small enough to build and check on its own. Don't build any of it.

## Report

Report the way `communication` says, with an outcome such as "Plan written, 4 tickets". Then where the plan and tickets are, and the terms added to the glossary.
