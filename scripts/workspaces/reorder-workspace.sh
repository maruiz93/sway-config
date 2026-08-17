#!/bin/bash
# Reorder the focused workspace one position left or right within its output.
# Finds a free number in the gap if available, otherwise swaps with the neighbor.
DIRECTION="${1:?Usage: reorder-workspace.sh left|right}"
ORIGNAMES_UTIL="$HOME/.config/sway/scripts/workspaces/ws-orignames-util.py"

ALL_WS=$(swaymsg -t get_workspaces)
FOCUSED_NUM=$(echo "$ALL_WS" | jq '[.[] | select(.focused)][0].num')
FOCUSED_NAME=$(echo "$ALL_WS" | jq -r '[.[] | select(.focused)][0].name')
FOCUSED_OUTPUT=$(echo "$ALL_WS" | jq -r '[.[] | select(.focused)][0].output')

SAME_OUTPUT=$(echo "$ALL_WS" | jq -c "[.[] | select(.output == \"$FOCUSED_OUTPUT\")] | sort_by(.num)")
COUNT=$(echo "$SAME_OUTPUT" | jq 'length')
POS=$(echo "$SAME_OUTPUT" | jq "[.[].num] | index($FOCUSED_NUM)")

case "$DIRECTION" in
    left)  [ "$POS" -eq 0 ] && exit 0; NEIGHBOR_IDX=$((POS - 1)) ;;
    right) [ "$POS" -eq $((COUNT - 1)) ] && exit 0; NEIGHBOR_IDX=$((POS + 1)) ;;
    *)     exit 1 ;;
esac

NEIGHBOR_NUM=$(echo "$SAME_OUTPUT" | jq ".[$NEIGHBOR_IDX].num")
NEIGHBOR_NAME=$(echo "$SAME_OUTPUT" | jq -r ".[$NEIGHBOR_IDX].name")
USED_NUMS=$(echo "$ALL_WS" | jq '[.[].num]')

if [ "$DIRECTION" = "left" ]; then
    if [ "$NEIGHBOR_IDX" -gt 0 ]; then
        LOWER=$(echo "$SAME_OUTPUT" | jq ".[$((NEIGHBOR_IDX - 1))].num")
    else
        LOWER=0
    fi
    UPPER=$NEIGHBOR_NUM
else
    if [ "$NEIGHBOR_IDX" -lt $((COUNT - 1)) ]; then
        UPPER=$(echo "$SAME_OUTPUT" | jq ".[$((NEIGHBOR_IDX + 1))].num")
    else
        UPPER=21
    fi
    LOWER=$NEIGHBOR_NUM
fi

# Pick the free number closest to the neighbor for natural ordering
FREE_NUM=""
if [ "$DIRECTION" = "left" ]; then
    for i in $(seq $((UPPER - 1)) -1 $((LOWER + 1))); do
        if ! echo "$USED_NUMS" | jq -e "index($i)" > /dev/null 2>&1; then
            FREE_NUM=$i; break
        fi
    done
else
    for i in $(seq $((LOWER + 1)) $((UPPER - 1))); do
        if ! echo "$USED_NUMS" | jq -e "index($i)" > /dev/null 2>&1; then
            FREE_NUM=$i; break
        fi
    done
fi

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

if [ -n "$FREE_NUM" ]; then
    NEW_NAME=$(build_name "$FOCUSED_NAME" "$FOCUSED_NUM" "$FREE_NUM")
    swaymsg "rename workspace \"$FOCUSED_NAME\" to \"$NEW_NAME\""
    python3 "$ORIGNAMES_UTIL" move-key "$FOCUSED_NUM" "$FREE_NUM"
else
    TEMP=99
    while echo "$USED_NUMS" | jq -e "index($TEMP)" > /dev/null 2>&1; do
        TEMP=$((TEMP + 1))
    done

    TEMP_NAME=$(build_name "$FOCUSED_NAME" "$FOCUSED_NUM" "$TEMP")
    NEW_FOCUSED=$(build_name "$FOCUSED_NAME" "$FOCUSED_NUM" "$NEIGHBOR_NUM")
    NEW_NEIGHBOR=$(build_name "$NEIGHBOR_NAME" "$NEIGHBOR_NUM" "$FOCUSED_NUM")

    swaymsg "rename workspace \"$FOCUSED_NAME\" to \"$TEMP_NAME\""
    swaymsg "rename workspace \"$NEIGHBOR_NAME\" to \"$NEW_NEIGHBOR\""
    swaymsg "rename workspace \"$TEMP_NAME\" to \"$NEW_FOCUSED\""
    python3 "$ORIGNAMES_UTIL" swap-keys "$FOCUSED_NUM" "$NEIGHBOR_NUM"
fi
