#!/bin/bash

# Git Worktree Helper Tool - Enhanced script for complete worktree lifecycle management
# Supports creating/opening worktrees, safely closing them, and displaying ticket information
# Usage: ./worktree.sh <command> <ticket_number>
#
# Commands:
#   open  <ticket>  - Create and open worktree for ticket
#   close <ticket>  - Delete branch and remove worktree (safe deletion only)
#   info  <ticket>  - Show ticket details and worktree status
#
# Examples:
#   ./worktree.sh open 42   - Create worktree for ticket #42
#   ./worktree.sh close 42  - Close and cleanup worktree for ticket #42
#   ./worktree.sh info 42   - Show info about ticket #42 and its worktree status

set -e

# Check if we're already in a worktree
if git rev-parse --git-dir 2>/dev/null | grep -q "/\.git/worktrees/"; then
    echo "Error: You are already in a worktree!"
    echo "Cannot create a worktree from within another worktree."
    echo "Please return to the main repository before creating a new worktree."
    exit 1
fi

# Check if command and ticket number are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <command> <ticket_number>"
    echo ""
    echo "Commands:"
    echo "  open  <ticket>  - Create and open worktree for ticket"
    echo "  close <ticket>  - Delete branch and remove worktree"
    echo "  info  <ticket>  - Show ticket details and worktree status"
    echo ""
    echo "Examples:"
    echo "  $0 open 42   - Create worktree for ticket #42"
    echo "  $0 close 42  - Close and cleanup worktree for ticket #42"
    echo "  $0 info 42   - Show info about ticket #42 and its worktree status"
    exit 1
fi

COMMAND="$1"
TICKET_NUMBER="$2"

# Shared function to derive branch name from ticket ID and title
derive_branch_name() {
    local ticket_id="$1"
    local ticket_title="$2"
    
    # Sanitize the title to create branch name
    # 1. Convert to lowercase
    # 2. Replace spaces with single space
    # 3. Replace any non-alphanumeric characters (except hyphens) with hyphens
    # 4. Replace multiple consecutive hyphens with single hyphen
    # 5. Remove leading/trailing hyphens
    local subject=$(echo "$ticket_title" | \
        tr '[:upper:]' '[:lower:]' | \
        sed 's/  */ /g' | \
        sed 's/[^a-z0-9 -]/-/g' | \
        sed 's/ /-/g' | \
        sed 's/-\+/-/g' | \
        sed 's/^-\+\|-\+$//g')
    
    # Create full branch name
    local branch_name="$ticket_id-$subject"
    
    # Trim to 50 characters if longer, trying to break at word boundaries
    if [ ${#branch_name} -gt 50 ]; then
        # Try to cut at last hyphen within 50 chars
        local trimmed=$(echo "$branch_name" | cut -c1-50 | sed 's/-[^-]*$//')
        if [ ${#trimmed} -lt 10 ]; then
            # If too short after trimming, just cut at 50 chars and remove trailing hyphen
            branch_name=$(echo "$branch_name" | cut -c1-50 | sed 's/-$//')
        else
            branch_name="$trimmed"
        fi
    fi
    
    echo "$branch_name"
}

# Info command - show ticket details and worktree status
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
    if [ "$ticket_title" = "null" ] || [ -z "$ticket_title" ]; then
        echo "❌ Error: Could not extract ticket title"
        exit 1
    fi
    
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
    echo ""
}

# Open command - create and open worktree
open_worktree() {
    local ticket_number="$1"
    local ticket_id=$(printf "%04d" "$ticket_number")
    
    echo "Processing ticket #$ticket_id..."
    
    # Get ticket details from GitHub
    local ticket_json=$(gh issue view "$ticket_number" --json title,body)
    if [ $? -ne 0 ]; then
        echo "Error: Could not fetch ticket #$ticket_number from GitHub"
        exit 1
    fi
    
    # Extract ticket title
    local ticket_title=$(echo "$ticket_json" | jq -r '.title')
    if [ "$ticket_title" = "null" ] || [ -z "$ticket_title" ]; then
        echo "Error: Could not extract ticket title"
        exit 1
    fi
    
    echo "Ticket title: $ticket_title"
    
    # Derive branch name using shared function
    local branch_name=$(derive_branch_name "$ticket_id" "$ticket_title")
    echo "Branch name: $branch_name"
    
    # Check if a worktree with this branch name already exists anywhere
    local existing_worktree=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$branch_name" | grep "^worktree" | cut -d' ' -f2)
    if [ -n "$existing_worktree" ]; then
        echo "A worktree with branch '$branch_name' already exists at: $existing_worktree"
        echo -n "Do you want to cd to the existing worktree? (y/n): "
        read -r response
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            echo "Navigating to existing worktree..."
            # Check if venv exists in the existing worktree
            if [ -d "$existing_worktree/venv" ]; then
                echo "✨ Activating Python virtual environment..."
                cd "$existing_worktree" && exec fish -c "source venv/bin/activate.fish; exec fish"
            else
                cd "$existing_worktree" && exec fish
            fi
        else
            echo "Aborted."
            exit 1
        fi
    fi
    
    # Check if worktree directory already exists
    local worktree_path=".worktree/$ticket_id"
    if [ -d "$worktree_path" ]; then
        # Check if this is actually a git worktree
        if git worktree list | grep -q "$worktree_path"; then
            echo "Worktree directory $worktree_path already exists."
            echo -n "Do you want to cd to the existing worktree? (y/n): "
            read -r response
            if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
                echo "Navigating to existing worktree..."
                # Check if venv exists in the existing worktree
                if [ -d "$worktree_path/venv" ]; then
                    echo "✨ Activating Python virtual environment..."
                    cd "$worktree_path" && exec fish -c "source venv/bin/activate.fish; exec fish"
                else
                    cd "$worktree_path" && exec fish
                fi
            else
                echo "Aborted."
                exit 1
            fi
        else
            echo "Error: Directory $worktree_path exists but is not a git worktree"
            exit 1
        fi
    fi
    
    # Check if branch name already exists
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "Error: Branch '$branch_name' already exists in the repository"
        echo "Please choose a different ticket or manually handle the existing branch"
        exit 1
    fi
    
    # Also check remote branches
    if git ls-remote --heads origin "$branch_name" | grep -q "$branch_name"; then
        echo "Error: Branch '$branch_name' already exists on remote"
        echo "Please choose a different ticket or manually handle the existing branch"
        exit 1
    fi
    
    # Create the worktree
    echo "Creating worktree at $worktree_path with branch $branch_name..."
    git worktree add "$worktree_path" -b "$branch_name" dev
    
    if [ $? -eq 0 ]; then
        echo "Worktree created successfully!"
        
        # Files and folders to copy to worktree
        local copy_items=(
            "venv/"
            "db.sqlite3"
            "CLAUDE.md"
            "CLAUDE.local.md"
            ".claude"
        )
        
        echo "Copying required files to worktree..."
        for item in "${copy_items[@]}"; do
            if [ -e "$item" ]; then
                echo "  Copying $item..."
                cp -r "$item" "$worktree_path/"
            else
                echo "  Warning: $item not found, skipping..."
            fi
        done
        
        echo ""
        echo "✅ Worktree created successfully for ticket #$ticket_id"
        echo "📁 Location: $worktree_path"
        echo "🌿 Branch: $branch_name"
        echo ""
        
        # Get absolute path for the worktree
        local worktree_abs_path=$(cd "$worktree_path" && pwd)
        
        echo "Starting fish shell in worktree directory..."
        echo "Type 'exit' to return to the main project directory"
        
        # Check if venv exists in the worktree
        if [ -d "$worktree_path/venv" ]; then
            echo "✨ Activating Python virtual environment..."
        fi
        echo ""
        
        # Spawn a new fish shell in the worktree directory
        # If venv exists, activate it within the fish shell
        if [ -d "$worktree_path/venv" ]; then
            cd "$worktree_path" && exec fish -c "source venv/bin/activate.fish; exec fish"
        else
            cd "$worktree_path" && exec fish
        fi
    else
        echo "Error: Failed to create worktree"
        exit 1
    fi
}

# Close command - safely delete branch and remove worktree
close_worktree() {
    local ticket_number="$1"
    local ticket_id=$(printf "%04d" "$ticket_number")
    
    # Get ticket details to derive branch name
    echo "Fetching ticket #$ticket_number details to derive branch name..."
    local ticket_json=$(gh issue view "$ticket_number" --json title,body 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "Error: Could not fetch ticket #$ticket_number from GitHub"
        exit 1
    fi
    
    local ticket_title=$(echo "$ticket_json" | jq -r '.title')
    if [ "$ticket_title" = "null" ] || [ -z "$ticket_title" ]; then
        echo "Error: Could not extract ticket title"
        exit 1
    fi
    
    # Derive branch name using same logic as open
    local branch_name=$(derive_branch_name "$ticket_id" "$ticket_title")
    local worktree_path=".worktree/$ticket_id"
    
    echo "Branch to close: $branch_name"
    echo "Worktree path: $worktree_path"
    
    # Validate branch exists
    if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "❌ Error: Branch '$branch_name' does not exist"
        exit 1
    fi
    
    # Attempt safe branch deletion
    echo "Attempting to delete branch '$branch_name' (safe deletion only)..."
    if ! git branch -d "$branch_name" 2>/dev/null; then
        echo "❌ Error: Cannot delete branch '$branch_name'"
        echo "Branch is not fully merged. Use 'git status' to check for uncommitted changes."
        echo "Merge the branch into dev first, then try closing again."
        exit 1
    fi
    
    # Remove worktree if exists
    if [ -d "$worktree_path" ]; then
        echo "Removing worktree at $worktree_path..."
        git worktree remove "$worktree_path"
        echo "✅ Worktree removed: $worktree_path"
    fi
    
    echo "✅ Branch '$branch_name' deleted successfully"
    echo "✅ Ticket #$ticket_number worktree closed and cleaned up"
}

# Main command processing
case "$COMMAND" in
    "open")
        open_worktree "$TICKET_NUMBER"
        ;;
    "close")
        close_worktree "$TICKET_NUMBER"
        ;;
    "info")
        info_worktree "$TICKET_NUMBER"
        ;;
    *)
        echo "❌ Error: Unknown command '$COMMAND'"
        echo ""
        echo "Usage: $0 <command> <ticket_number>"
        echo ""
        echo "Commands:"
        echo "  open  <ticket>  - Create and open worktree for ticket"
        echo "  close <ticket>  - Delete branch and remove worktree"
        echo "  info  <ticket>  - Show ticket details and worktree status"
        exit 1
        ;;
esac