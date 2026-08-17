#!/bin/bash
current=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
target=$(swaymsg -t get_outputs | jq -r ".[] | select(.name != \"$current\") | .name" | head -1)
[ -n "$target" ] && swaymsg "${1:-focus} output $target"
