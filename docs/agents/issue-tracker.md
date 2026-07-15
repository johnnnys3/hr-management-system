# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --limit 500 --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters. `--limit` defaults to **30** on every `gh issue list` and `gh search` command; pass it whenever the result is used to reason about the set as a whole rather than to eyeball a few recent items, because a truncated list is indistinguishable from a complete one in the output.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `authorAssociation` is **not** a `gh pr list --json` field — that command exposes `author` but no association, so the filter has to come from `gh search prs`, which does:

  ```bash
  gh search prs --repo "$(gh repo view --json nameWithOwner --jq .nameWithOwner)" \
    --state open --limit 200 \
    --json number,title,body,labels,author,authorAssociation \
    --jq '[.[] | select(.authorAssociation | IN("CONTRIBUTOR","FIRST_TIME_CONTRIBUTOR","NONE"))]'
  ```

  Keeps `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, `NONE`; drops `OWNER`, `MEMBER`, `COLLABORATOR`. `gh search prs` needs an explicit `--repo` and carries a narrower field set than `gh pr list` — notably `commentsCount` rather than `comments`, so fetch bodies per PR with `gh pr view <number> --comments` where triage needs them.

  **`--limit` is not optional here.** It defaults to **30**, and the `--jq` filter runs on whatever was fetched, so the fetch is truncated *before* the association filter is applied — a repo with more than 30 open PRs silently drops external ones from triage, and the output looks like a complete result. Raise it past the open-PR count; `gh search prs` caps at 1000, and a repo above that needs narrowing by `--label` or date rather than a larger number.
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either — resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies** — the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). The REST issue payload reports `issue_dependencies_summary` (`gh api repos/<owner>/<repo>/issues/<n>`), whose `blocked_by` counts **open** blockers — the live gate — against `total_blocked_by` for all of them. That is a REST field, not a `--json` selector: `gh issue list`/`gh issue view` will not return it. Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: the `gh` path uses `blockedBy`, which `gh issue list --json` does expose — one call, no per-issue fan-out. Its nodes carry `state`, so filter on open blockers rather than on the presence of an edge, since a closed blocker still leaves one:

  ```bash
  gh issue list --state open --limit 500 --json number,title,assignees,blockedBy \
    --jq '[.[] | select((.assignees|length) == 0)
             | select(.blockedBy.totalCount == (.blockedBy.nodes|length))
             | select([.blockedBy.nodes[] | select(.state == "OPEN")] | length == 0)]'
  ```

  Scope to the map's sub-issues / task list; first in map order wins.

  Two truncations to respect, both of which fail towards *silently claiming a blocked ticket*:

  - **`--limit` defaults to 30.** Set it above the open-issue count. Unlike `gh search prs` this paginates rather than capping, so a generous number is safe.
  - **`blockedBy` is fetched `first:50`.** The `totalCount` guard above is what makes the filter honest: where the nodes are truncated, the query cannot see whether the blockers beyond the first 50 are open, and a ticket with 50+ blockers is therefore **excluded from the frontier rather than assumed unblocked**. That is the safe direction — the alternative is claiming a ticket whose real blocker was never fetched. A ticket that trips this guard needs paging through its blockers by hand, but at that count it wants a human look regardless.
- **Claim**: `gh issue edit <n> --add-assignee @me` — the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.
