#!/bin/bash
con_id=$(swaymsg -t get_tree | jq -r '.. | select(.focused? == true) | .id')
marks=$(swaymsg -t get_tree | jq -r '.. | select(.focused? == true) | .marks // [] | .[]' 2>/dev/null)

if echo "$marks" | grep -q "^_pin_"; then
    swaymsg "[con_id=${con_id}] unmark _pin_${con_id}"
else
    swaymsg "mark --add _pin_${con_id}"
fi
