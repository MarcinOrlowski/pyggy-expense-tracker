# Worktree Helper Tool Enhancement PRD v1.0

**GitHub Issue**: [Rework worktree.sh into helper tool with open/close commands](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/42)

## Problem Statement

Developers using the current worktree.sh script can only create/open worktrees but cannot cleanly
close them, leading to accumulation of unused branches and worktrees. Manual cleanup requires
multiple git commands and is error-prone. This creates repository clutter and increases cognitive
overhead for developers managing multiple ticket branches simultaneously.

## Solution Overview

Enhance worktree.sh to support both `open` and `close` commands, providing a complete worktree
lifecycle management tool. The `close` command will safely delete merged branches and remove
associated worktrees automatically. Success means developers can manage worktree lifecycle with
simple, memorable commands while maintaining git repository cleanliness.

## User Stories

1. As a developer, I want to open a worktree using `worktree.sh open <ticket>`, so that I can
   quickly start working on a ticket with an isolated environment
2. As a developer, I want to close a worktree using `worktree.sh close <ticket>`, so that I can
   automatically clean up branches and worktrees when done
3. As a developer, I want to get ticket information using `worktree.sh info <ticket>`, so that I can
   see ticket details and worktree status without creating anything
4. As a developer, I want safe branch deletion (only merged branches), so that I don't accidentally
   lose unmerged work
5. As a developer, I want clear error messages when cleanup fails, so that I can understand and
   resolve issues manually

## Acceptance Criteria

- [ ] Script supports `worktree.sh open <ticket_number>` command with current functionality
- [ ] Script supports `worktree.sh close <ticket_number>` command for cleanup
- [ ] Script supports `worktree.sh info <ticket_number>` command for ticket information and worktree status
- [ ] Info command shows ticket title, branch name, and whether worktree exists
- [ ] Close command uses `git branch -d` (safe delete) to prevent unmerged branch deletion
- [ ] Close command removes worktree directory using `git worktree remove` after successful branch deletion
- [ ] Clear error messages when branch cannot be deleted (not merged, has uncommitted changes)
- [ ] Updated help/usage documentation in script comments

## Out of Scope

- Force deletion of unmerged branches (`git branch -D`)
- Automatic merging of branches before deletion
- Batch operations (closing multiple worktrees at once)
- Integration with GitHub PR status checking
- Backup or archival of deleted branches

## Success Metrics

1. Developers can complete full worktree lifecycle (open → work → close) using only worktree.sh commands
2. Zero manual git commands needed for standard worktree cleanup workflows
3. No accidental loss of unmerged work due to safe deletion approach
