#!/bin/bash
# Move GitHub Chrome app windows to the focused workspace when they spawn.
# Runs as a daemon listening to Sway IPC window events.

swaymsg -t subscribe -m '["window"]' | while read -r event; do
    change=$(echo "$event" | jq -r '.change')
    app_id=$(echo "$event" | jq -r '.container.app_id // empty')

    if [[ "$change" == "new" && "$app_id" == "chrome-fjgfadkpfahgllmffkfkmlmbanjamddm-Default" ]]; then
        con_id=$(echo "$event" | jq -r '.container.id')
        focused_ws=$(swaymsg -t get_workspaces | jq -r '.[] | select(.focused) | .name')
        swaymsg "[con_id=$con_id] move to workspace $focused_ws, focus"
    fi
done
