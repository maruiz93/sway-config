#!/bin/bash
PIDFILE="/tmp/sway-opacity.pid"
UNFOCUSED=0.85

# Kill all previous instances
for pid in $(pgrep -f "sway/opacity.sh"); do
    [ "$pid" != "$$" ] && kill "$pid" 2>/dev/null
done
echo $$ > "$PIDFILE"

apply_opacity() {
    swaymsg '[app_id=".*"] opacity '"$UNFOCUSED"
    swaymsg '[class=".*"] opacity '"$UNFOCUSED"
    swaymsg '[con_id="__focused__"] opacity 1'
    swaymsg '[app_id="chrome-kjgfgldnnfoeklkmfkjfagphfepbbdan-Default"] opacity 1'
    swaymsg '[con_mark="^_pin_"] opacity 1'
}

apply_opacity

swaymsg -t subscribe -m '["window", "binding"]' | while read -r event; do
    change=$(echo "$event" | jq -r '.change')
    if [ "$change" = "focus" ] || [ "$change" = "run" ] || [ "$change" = "mark" ]; then
        apply_opacity
    fi
done
