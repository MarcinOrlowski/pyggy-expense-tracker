#!/bin/bash

# Git Worktree script to create isolated working directories for parallel development
# Creates a new worktree from a GitHub ticket to enable working on multiple branches simultaneously
# Usage: ./worktree.sh <ticket_number>
#
#
# To merge from worktree (directly)
# - go back from worktree to main tree:
#   cd <PROJECT ROOT>
#   git co dev  # lub inny branch z ktorego worktree odchodzilo
#   git merge --squash <TICKET ID>-<SUBJECT>  # merge your branch from worktree
#
# - delete worktree
#   git worktree remove <PATH TO WORKTREE>

set -e

# Check if we're already in a worktree
if git rev-parse --git-dir 2>/dev/null | grep -q "/\.git/worktrees/"; then
    echo "Error: You are already in a worktree!"
    echo "Cannot create a worktree from within another worktree."
    echo "Please return to the main repository before creating a new worktree."
    exit 1
fi

# Check if ticket number is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <ticket_number>"
    echo "Example: $0 21"
    exit 1
fi

TICKET_ID=$(printf "%04d" "$1")
echo "Processing ticket #$TICKET_ID..."

# Get ticket details from GitHub
TICKET_JSON=$(gh issue view "$1" --json title,body)
if [ $? -ne 0 ]; then
    echo "Error: Could not fetch ticket #$1 from GitHub"
    exit 1
fi

# Extract ticket title
TICKET_TITLE=$(echo "$TICKET_JSON" | jq -r '.title')
if [ "$TICKET_TITLE" = "null" ] || [ -z "$TICKET_TITLE" ]; then
    echo "Error: Could not extract ticket title"
    exit 1
fi

echo "Ticket title: $TICKET_TITLE"

# Sanitize the title to create branch name
# 1. Convert to lowercase
# 2. Replace spaces with single space
# 3. Replace any non-alphanumeric characters (except hyphens) with hyphens
# 4. Replace multiple consecutive hyphens with single hyphen
# 5. Remove leading/trailing hyphens
SUBJECT=$(echo "$TICKET_TITLE" | \
    tr '[:upper:]' '[:lower:]' | \
    sed 's/  */ /g' | \
    sed 's/[^a-z0-9 -]/-/g' | \
    sed 's/ /-/g' | \
    sed 's/-\+/-/g' | \
    sed 's/^-\+\|-\+$//g')

# Create full branch name
BRANCH_NAME="$TICKET_ID-$SUBJECT"

# Trim to 50 characters if longer, trying to break at word boundaries
if [ ${#BRANCH_NAME} -gt 50 ]; then
    # Try to cut at last hyphen within 50 chars
    TRIMMED=$(echo "$BRANCH_NAME" | cut -c1-50 | sed 's/-[^-]*$//')
    if [ ${#TRIMMED} -lt 10 ]; then
        # If too short after trimming, just cut at 50 chars and remove trailing hyphen
        BRANCH_NAME=$(echo "$BRANCH_NAME" | cut -c1-50 | sed 's/-$//')
    else
        BRANCH_NAME="$TRIMMED"
    fi
fi

echo "Branch name: $BRANCH_NAME"

# Check if a worktree with this branch name already exists anywhere
EXISTING_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$BRANCH_NAME" | grep "^worktree" | cut -d' ' -f2)
if [ -n "$EXISTING_WORKTREE" ]; then
    echo "A worktree with branch '$BRANCH_NAME' already exists at: $EXISTING_WORKTREE"
    echo -n "Do you want to cd to the existing worktree? (y/n): "
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo "Navigating to existing worktree..."
        # Check if venv exists in the existing worktree
        if [ -d "$EXISTING_WORKTREE/venv" ]; then
            echo "✨ Activating Python virtual environment..."
            cd "$EXISTING_WORKTREE" && exec fish -c "source venv/bin/activate.fish; exec fish"
        else
            cd "$EXISTING_WORKTREE" && exec fish
        fi
    else
        echo "Aborted."
        exit 1
    fi
fi

# Check if worktree directory already exists
WORKTREE_PATH=".worktree/$TICKET_ID"
if [ -d "$WORKTREE_PATH" ]; then
    # Check if this is actually a git worktree
    if git worktree list | grep -q "$WORKTREE_PATH"; then
        echo "Worktree directory $WORKTREE_PATH already exists."
        echo -n "Do you want to cd to the existing worktree? (y/n): "
        read -r response
        if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
            echo "Navigating to existing worktree..."
            # Check if venv exists in the existing worktree
            if [ -d "$WORKTREE_PATH/venv" ]; then
                echo "✨ Activating Python virtual environment..."
                cd "$WORKTREE_PATH" && exec fish -c "source venv/bin/activate.fish; exec fish"
            else
                cd "$WORKTREE_PATH" && exec fish
            fi
        else
            echo "Aborted."
            exit 1
        fi
    else
        echo "Error: Directory $WORKTREE_PATH exists but is not a git worktree"
        exit 1
    fi
fi

# Check if branch name already exists
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    echo "Error: Branch '$BRANCH_NAME' already exists in the repository"
    echo "Please choose a different ticket or manually handle the existing branch"
    exit 1
fi

# Also check remote branches
if git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
    echo "Error: Branch '$BRANCH_NAME' already exists on remote"
    echo "Please choose a different ticket or manually handle the existing branch"
    exit 1
fi

# Create the worktree
echo "Creating worktree at $WORKTREE_PATH with branch $BRANCH_NAME..."
git worktree add "$WORKTREE_PATH" -b "$BRANCH_NAME" dev

if [ $? -eq 0 ]; then
    echo "Worktree created successfully!"
    
    # Files and folders to copy to worktree
    COPY_ITEMS=(
        "venv/"
        "db.sqlite3"
        "CLAUDE.md"
        "CLAUDE.local.md"
        ".claude"
    )
    
    echo "Copying required files to worktree..."
    for item in "${COPY_ITEMS[@]}"; do
        if [ -e "$item" ]; then
            echo "  Copying $item..."
            cp -r "$item" "$WORKTREE_PATH/"
        else
            echo "  Warning: $item not found, skipping..."
        fi
    done
    
    echo ""
    echo "✅ Worktree created successfully for ticket #$TICKET_ID"
    echo "📁 Location: $WORKTREE_PATH"
    echo "🌿 Branch: $BRANCH_NAME"
    echo ""
    
    # Get absolute path for the worktree
    WORKTREE_ABS_PATH=$(cd "$WORKTREE_PATH" && pwd)
    
    echo "Starting fish shell in worktree directory..."
    echo "Type 'exit' to return to the main project directory"
    
    # Check if venv exists in the worktree
    if [ -d "$WORKTREE_PATH/venv" ]; then
        echo "✨ Activating Python virtual environment..."
    fi
    echo ""
    
    # Spawn a new fish shell in the worktree directory
    # If venv exists, activate it within the fish shell
    if [ -d "$WORKTREE_PATH/venv" ]; then
        cd "$WORKTREE_PATH" && exec fish -c "source venv/bin/activate.fish; exec fish"
    else
        cd "$WORKTREE_PATH" && exec fish
    fi
else
    echo "Error: Failed to create worktree"
    exit 1
fi
