# Worktree Helper Tool Enhancement TRD v1.0

**PRD Reference**: 0042_worktree_helper_tool_PRD.md v1.0

## Technical Approach

We'll rewrite worktree.sh as a command-based tool requiring explicit `open` or `close` commands. The script will use standard command parsing with `$1` for command and `$2` for ticket number. Implementation will split existing functionality into separate functions and add new close logic using git's native `git branch -d` and `git worktree remove` commands with proper error handling.

## Command Interface Design

```bash
# Required command structure (no defaults)
./worktree.sh open <ticket_number>    # Create/open worktree
./worktree.sh close <ticket_number>   # Close/cleanup worktree
./worktree.sh info <ticket_number>    # Show ticket info and worktree status
./worktree.sh                         # Shows usage error

# Usage validation
if [ $# -ne 2 ]; then
    echo "Usage: $0 <command> <ticket_number>"
    echo "Commands:"
    echo "  open  <ticket>  - Create and open worktree for ticket"
    echo "  close <ticket>  - Delete branch and remove worktree"
    echo "  info  <ticket>  - Show ticket details and worktree status"
    exit 1
fi

COMMAND="$1"
TICKET_NUMBER="$2"

case "$COMMAND" in
    "open")  open_worktree "$TICKET_NUMBER" ;;
    "close") close_worktree "$TICKET_NUMBER" ;;
    "info")  info_worktree "$TICKET_NUMBER" ;;
    *) echo "Error: Unknown command '$COMMAND'"; exit 1 ;;
esac
```

## Info Command Implementation

```bash
info_worktree() {
    local ticket_number="$1"
    local ticket_id=$(printf "%04d" "$ticket_number")
    
    # Get ticket details from GitHub
    echo "Fetching ticket #$ticket_number from GitHub..."
    local ticket_json=$(gh issue view "$ticket_number" --json title,body 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "❌ Error: Could not fetch ticket #$ticket_number from GitHub"
        exit 1
    fi
    
    # Extract ticket title and derive branch name
    local ticket_title=$(echo "$ticket_json" | jq -r '.title')
    local branch_name=$(derive_branch_name "$ticket_id" "$ticket_title")
    local worktree_path=".worktree/$ticket_id"
    
    # Display ticket information
    echo ""
    echo "📋 Ticket #$ticket_number Information:"
    echo "   Title: $ticket_title"
    echo "   Branch: $branch_name"
    echo ""
    
    # Check worktree status
    if [ -d "$worktree_path" ] && git worktree list | grep -q "$worktree_path"; then
        echo "✅ Worktree exists at: $worktree_path"
    else
        echo "❌ No worktree found"
    fi
    
    # Check if branch exists
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "✅ Branch exists: $branch_name"
    else
        echo "❌ Branch does not exist: $branch_name"
    fi
}
```

## Close Command Implementation

```bash
close_worktree() {
    local ticket_number="$1"
    local ticket_id=$(printf "%04d" "$ticket_number")
    
    # Derive branch name using same logic as open
    local branch_name="$ticket_id-$subject"  # Same derivation as open
    local worktree_path=".worktree/$ticket_id"
    
    # Validate branch exists
    if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "Error: Branch '$branch_name' does not exist"
        exit 1
    fi
    
    # Attempt safe branch deletion
    if ! git branch -d "$branch_name" 2>/dev/null; then
        echo "Error: Cannot delete branch '$branch_name'"
        echo "Branch is not fully merged. Use 'git status' to check."
        exit 1
    fi
    
    # Remove worktree if exists
    if [ -d "$worktree_path" ]; then
        git worktree remove "$worktree_path"
        echo "✅ Worktree removed: $worktree_path"
    fi
    
    echo "✅ Branch '$branch_name' deleted successfully"
}
```

## Error Handling Strategy

- **Missing arguments**: Show usage and exit with code 1
- **Unknown command**: Clear error message and exit with code 1  
- **Non-existent branch**: Inform user and exit with code 1
- **Unmerged branch**: Explain safe deletion policy and exit with code 1
- **Worktree removal failure**: Git will handle error reporting

## Security & Performance

- **File Safety**: Only removes files in `.worktree/` directory with explicit path validation
- **Git Safety**: Uses `git branch -d` (not `-D`) to prevent accidental deletion of unmerged work
- **Validation**: Strict command validation with clear error messages

## Technical Risks & Mitigations

1. **Risk**: Branch name derivation differs between open/close → **Mitigation**: Extract branch naming into shared function
2. **Risk**: User confusion about command requirement → **Mitigation**: Clear usage message with examples
3. **Risk**: Losing work due to unmerged branches → **Mitigation**: Safe delete only with clear error explanation

## Implementation Plan

- Phase 1 (S): Rewrite argument parsing with command validation
- Phase 2 (M): Extract `open_worktree()` function from existing code
- Phase 3 (S): Create shared `derive_branch_name()` function
- Phase 4 (M): Implement `info_worktree()` for ticket information display
- Phase 5 (M): Implement `close_worktree()` with branch name derivation
- Phase 6 (S): Add usage help and error messages
- Phase 7 (S): Test all three commands with various scenarios

Dependencies: None

## Monitoring & Rollback

- **Testing**: Manual testing with existing tickets and new worktrees
- **Key validations**: Ensure branch naming consistency between open/close
- **Rollback**: Simple git revert since changes are contained to single script file
