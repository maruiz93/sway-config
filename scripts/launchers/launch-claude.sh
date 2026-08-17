#!/bin/bash
# Launch Claude Code in a chosen directory with a dedicated app_id
dir=$(
    {
        echo ~/.claude
        echo ~/.config/sway
        echo ~/Workspace/claude-projects/claude-projects-dev-env
        find ~ -maxdepth 4 -name .git -type d 2>/dev/null \
            | grep -v '\.cache/pre-commit' \
            | sed 's|/\.git$||'
    } \
    | sort -u \
    | sed "s|^$HOME|~|" \
    | fuzzel --dmenu --prompt "Claude directory "
)
[ -n "$dir" ] && kitty --class claude-code --directory "${dir/#\~/$HOME}" -e claude
