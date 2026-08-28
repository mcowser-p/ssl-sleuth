---
name: conventional-commits
description: >
  Write every commit message and PR title in this collection's required
  format. Use when committing, when amending, and when opening or renaming a
  PR — squash merges turn the PR title into the commit, and semantic-release
  reads these messages to decide the version and write the changelog. A
  mislabeled commit ships a mislabeled release; an unscoped one ships nothing.
---

# Conventional commits in this collection

Every commit reads `type(scope): description`. Release automation reads these
messages, so the format is not ceremony — it is the input to versioning.

## A scope is MANDATORY here

`.releaserc.js` opens its `releaseRules` with:

```js
{ scope: null, release: false }   // ignore commits without a scope
```

So `fix: stop the crash` is silently ignored and **no release is cut**. It must
be `fix(inspect): stop the crash`. This is stricter than the upstream
Conventional Commits spec, where the scope is optional, and it is the single
easiest way to land a real fix that never ships.

## Types and what they do to the version

Taken from `.releaserc.js`, not from the general convention — `docs` differs.

| type | use for | release effect |
| --- | --- | --- |
| `feat` | a new capability a user can see or use | **minor** |
| `fix` | repairing broken behaviour | **patch** |
| `docs` | documentation only | **patch** (not "none" — this repo releases docs) |
| `chore` | upkeep that fits nothing above | none |
| `refactor`, `test`, `build`, `ci`, `perf` | as named | none |

Breaking changes add `!` after the type/scope **and** a `BREAKING CHANGE:`
footer, which becomes the migration note in the changelog:

```
feat(handler)!: require an explicit ca_bundle

BREAKING CHANGE: an absent ca_bundle no longer falls back to the system store.
```

## Scopes in use

Take the scope from the part of the collection being changed, matching what is
already in `git log`: the role area (`install`, `issue`, `account`, `inspect`,
`handler`, `windows`), or the supporting machinery (`ci`, `lint`, `deps`,
`readme`, `collection`, `skills`).

## Writing good ones

- Imperative, lowercase description, no trailing period.
- The body explains *why*. The reader is you, months later, wondering what
  this was for — and for a fix, what the symptom looked like, because that is
  what the next person will search for.
- One logical change per commit. If the description needs the word "and",
  split it.

Bad → good:

- `fix: fixed windows` → `fix(windows): resolve the IIS site id from its name`
- `chore: stuff` → `chore(deps): bump actions/checkout from 4 to 7`
- `fix(issue): update flags and add a channel and fix logging` → three commits

## When a fix is already merged unreleased

A correct change merged under a non-conventional message is on `main` and
invisible to semantic-release — the workflow runs, succeeds, and cuts nothing.
Rewriting `main` is not the fix. Land a follow-up commit carrying the right
type and scope, with a body naming the SHA it releases, so the changelog ends
up describing what actually changed.
