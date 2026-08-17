#!/bin/bash
pid=$(swaymsg -t get_tree | jq '.. | select(.focused? == true) | .pid')
[ -S "/tmp/kitty-$pid" ] && kitty @ --to "unix:/tmp/kitty-$pid" set-font-size -- "$1"
