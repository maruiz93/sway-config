#!/bin/bash
# Renumber all workspaces sequentially (1, 2, 3, ...) to close gaps.

ORIGNAMES_UTIL="$HOME/.config/sway/ws-orignames-util.py"

ALL_WS=$(swaymsg -t get_workspaces)
SORTED=$(echo "$ALL_WS" | jq -c '[.[] | select(.num > 0) | {num, name}] | sort_by(.num)')
COUNT=$(echo "$SORTED" | jq 'length')

build_name() {
    local old_name="$1" old_num="$2" new_num="$3"
    local result
    result=$(python3 "$ORIGNAMES_UTIL" build-name "$old_num" "$new_num" "$old_name")
    if [ -n "$result" ]; then
        echo "$result"
    elif [[ "$old_name" == "${old_num}:"* ]]; then
        echo "${new_num}:${old_name#${old_num}:}"
    else
        echo "$new_num"
    fi
}

for i in $(seq 0 $((COUNT - 1))); do
    TARGET=$((i + 1))
    CURRENT_NUM=$(echo "$SORTED" | jq ".[$i].num")
    CURRENT_NAME=$(echo "$SORTED" | jq -r ".[$i].name")

    [ "$CURRENT_NUM" -eq "$TARGET" ] && continue

    NEW_NAME=$(build_name "$CURRENT_NAME" "$CURRENT_NUM" "$TARGET")
    swaymsg "rename workspace \"$CURRENT_NAME\" to \"$NEW_NAME\""
    python3 "$ORIGNAMES_UTIL" move-key "$CURRENT_NUM" "$TARGET"
done
