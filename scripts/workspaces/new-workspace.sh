#!/bin/bash
USED=$(swaymsg -t get_workspaces | jq -r '.[].num')
for i in $(seq 1 20); do
    if ! echo "$USED" | grep -qx "$i"; then
        swaymsg workspace number "$i"
        exit 0
    fi
done
