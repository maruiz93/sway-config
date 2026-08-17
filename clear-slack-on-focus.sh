#!/bin/bash
# Clear Slack notifications from swaync when the Slack window gets focus.
# Works with a swaync "receive" script that logs notification IDs to IDFILE.

IDFILE=/tmp/slack-notification-ids

swaymsg -t subscribe -m '["window"]' | while read -r event; do
    change=$(echo "$event" | jq -r '.change // empty')
    app_id=$(echo "$event" | jq -r '.container.app_id // empty')

    if [[ "$change" == "focus" && "$app_id" == "com.slack.Slack" && -s "$IDFILE" ]]; then
        while read -r nid; do
            [[ -n "$nid" ]] && busctl --user call org.erikreider.swaync.cc \
                /org/erikreider/swaync/cc org.erikreider.swaync.cc \
                CloseNotification u "$nid" 2>/dev/null
        done < "$IDFILE"
        : > "$IDFILE"
    fi
done
