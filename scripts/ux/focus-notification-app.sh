#!/bin/bash
# Focus the sway window that sent a notification.
# Called by swaync via the "scripts" config with SWAYNC_* env vars.

APP="${SWAYNC_APP_NAME:-}"
DESKTOP="${SWAYNC_DESKTOP_ENTRY:-}"
SUMMARY="${SWAYNC_SUMMARY:-}"
BODY="${SWAYNC_BODY:-}"

LOG=/tmp/focus-notification-app.log
env | grep ^SWAYNC_ | sort >> "$LOG"
echo "---" >> "$LOG"

[[ -z "$APP" && -z "$DESKTOP" ]] && exit 0

# Score each candidate window and focus the best match.
# $1: jq regex for app_id, $2: text to match against window titles
focus_best_match() {
    local aid_pattern="$1" search="$2"
    [[ -z "$search" ]] && return 1

    local best_id="" best_score=0
    while IFS=$'\t' read -r wid title; do
        local score=0
        local tl="${title,,}" sl="${search,,}"

        if [[ "$tl" == *"$sl"* ]]; then
            score=100
        elif [[ "$sl" == *"$tl"* ]]; then
            score=90
        else
            for word in $sl; do
                [[ ${#word} -le 2 ]] && continue
                [[ "$tl" == *"$word"* ]] && (( score += 10 ))
            done
        fi

        if (( score > best_score )); then
            best_score=$score
            best_id=$wid
        fi
    done < <(swaymsg -t get_tree | jq -r \
        --arg p "$aid_pattern" \
        '.. | select(.app_id? and (.app_id | test($p)) and .type? == "con")
         | "\(.id)\t\(.name)"' 2>/dev/null)

    echo "$(date +%T)   best_id=$best_id score=$best_score" >> "$LOG"
    [[ -n "$best_id" && $best_score -gt 0 ]] &&
        swaymsg "[con_id=$best_id] focus" 2>/dev/null
}

# Try desktop-entry first — for PWAs this often matches the app_id directly
if [[ -n "$DESKTOP" ]]; then
    swaymsg "[app_id=\"$DESKTOP\"] focus" 2>/dev/null && exit 0
    swaymsg "[class=\"$DESKTOP\"] focus" 2>/dev/null && exit 0
fi

case "$APP" in
    kitty)
        # Kitty's OSC 99 protocol handles focusing the right tab natively
        # via ActionInvoked — don't interfere by focusing the wrong window.
        ;;
    "Google Chrome"|Chromium)
        focus_best_match '^(google-chrome|chrome-)' "$SUMMARY" && exit 0
        swaymsg '[app_id="google-chrome"] focus'
        ;;
    Slack)
        swaymsg '[app_id="com.slack.Slack"] focus' ;;
    "Telegram Desktop")
        swaymsg '[app_id="org.telegram.desktop"] focus' ;;
    Firefox|firefox)
        swaymsg '[app_id="firefox"] focus' ;;
    *)
        lower=$(echo "$APP" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        swaymsg "[app_id=\"$lower\"] focus" 2>/dev/null ||
            swaymsg "[class=\"$APP\"] focus" 2>/dev/null
        ;;
esac
