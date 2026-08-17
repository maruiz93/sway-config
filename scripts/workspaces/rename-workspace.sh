#!/bin/bash
ORIGNAMES_UTIL="$HOME/.config/sway/scripts/workspaces/ws-orignames-util.py"

CURRENT=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused)')
NUM=$(echo "$CURRENT" | jq -r '.num')
CURRENT_NAME=$(echo "$CURRENT" | jq -r '.name | split(":") | if length > 1 then .[1:] | join(":") else "" end')
if [ -n "$CURRENT_NAME" ]; then
    (sleep 0.1 && wtype "$CURRENT_NAME") &
fi
NAME=$(printf '' | fuzzel --dmenu --prompt 'Rename workspace ' --lines 1)

[ $? -ne 0 ] && exit 0

python3 "$ORIGNAMES_UTIL" delete-key "$NUM"

if [ -z "$NAME" ]; then
    swaymsg "rename workspace to $NUM"
else
    swaymsg "rename workspace to $NUM:$NAME"
fi
