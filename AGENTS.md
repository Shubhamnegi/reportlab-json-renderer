# Agent Instructions

This file defines how coding agents must work in this repository.
Make sure that we are building python3 library which other python projects can easily extend and use as per their requirement. 

## Working Principles

- Treat `pdf-generator.md` as the source of truth for library behavior.
- Do not re-open locked decisions unless the user explicitly asks to change them.
- Keep implementation choices boring, stable, and easy to maintain.
- Prefer clear bounded contexts over clever shared abstractions.
- Make small, reviewable changes.
- Preserve user changes. Do not revert unrelated work.

## Coding Standard

- Constants must be contained in a single file per package or bounded context.
- Each Python file must do exactly one domain task.
- Folders must be logically grouped by responsibility.
- Always prefer the most stable, reputed, security-aware third-party dependencies.
- Each function must do one granular task, such as:
    - merging data
    - fetching data
    - validating data
    - transforming data
    - processing data
    - mutating data
- Keep functions around 50 lines or less.
- Any function with control flow must have a test case.
- The pre-commit hook must run:
    - linting
    - tests
    - coverage

## Dependency Policy

Before adding a dependency:

1. Prefer platform or framework built-ins.
2. Prefer existing project dependencies.
3. If a new dependency is needed, choose stable, reputed, actively maintained, security-aware npm packages.
4. Avoid niche packages for small utilities.
5. Avoid unmaintained packages.
6. Avoid packages with unnecessary runtime weight.

Security-sensitive areas such as ZIP parsing, markdown rendering, auth, and validation require conservative dependency choices.



## Git And Change Hygiene

- Check current files before editing.
- Keep changes scoped to the request.
- Do not reformat unrelated files.
- Do not rename or reorganize folders unless required by the task.
- Do not commit unless the user asks.
- Do not remove user changes.

## Pre-Commit Requirement

The repository must eventually include a pre-commit hook that runs:

- linting
- tests
- coverage

Do not bypass the hook to land changes.

If the project has not been scaffolded yet, preserve this requirement for the initial setup.

## Documentation Rules

- Update this file when coding workflow, repository conventions, or test standards change.
- Make sure Readme.md clearly explains what problem it solves and how to install, test and run and use the library.