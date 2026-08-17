#!/bin/bash

BAT="/sys/class/power_supply/BAT0"
WARN_LEVEL=15
CRIT_LEVEL=5
POLL_INTERVAL=60

notified_warn=0
notified_crit=0
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

while true; do
    capacity=$(cat "$BAT/capacity" 2>/dev/null)
    status=$(cat "$BAT/status" 2>/dev/null)

    if [[ -z "$capacity" ]]; then
        sleep "$POLL_INTERVAL"
        continue
    fi

    if [[ "$status" == "Charging" || "$status" == "Full" ]]; then
        notified_warn=0
        notified_crit=0
        pkill -f 'battery-warning.py' 2>/dev/null
        sleep "$POLL_INTERVAL"
        continue
    fi

    if (( capacity <= CRIT_LEVEL )); then
        notify-send -u critical -t 0 "Battery Critical" "Battery at ${capacity}% — CHARGE NOW"
        pkill -f 'battery-warning.py' 2>/dev/null
        python3 "$SCRIPT_DIR/battery-warning.py" "$capacity" &
        notified_crit=1
    elif (( capacity <= WARN_LEVEL && notified_warn == 0 )); then
        notify-send -u normal "Battery Low" "Battery at ${capacity}%"
        notified_warn=1
    fi

    if (( capacity > WARN_LEVEL )); then
        notified_warn=0
        notified_crit=0
    elif (( capacity > CRIT_LEVEL )); then
        notified_crit=0
    fi

    sleep "$POLL_INTERVAL"
done
