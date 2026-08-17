# sway-config

My [Sway](https://swaywm.org/) tiling Wayland compositor configuration. Vim-centric, keyboard-driven, with dynamic workspace management.

## Stack

| Component | Tool |
|-----------|------|
| Compositor | Sway |
| Status bar | Waybar |
| Launcher | Fuzzel |
| Notifications | SwayNotificationCenter |
| Multi-monitor | Kanshi |
| Lock / Idle | Swaylock + Swayidle |
| Night light | WLSunset |
| Terminal | Kitty |
| Theme | Catppuccin Mocha |
| Font | JetBrains Mono |

## Layout

`config` is the entry point and includes modular files from `conf/`:

- **conf/variables.conf** - mod key, vim keys, app variables, screenshot commands
- **conf/devices.conf** - touchpad, keyboard (Spanish layout, caps/escape swap), wallpaper, output delegation to kanshi
- **conf/keymaps.conf** - all keybindings: navigation, layout, media, screenshots, workspace ops, gestures, clipboard history, app launchers
- **conf/workspaces.conf** - workspace switch/move bindings for 1-20 (number row + alt layer)
- **conf/lookAndFeel.conf** - Catppuccin Mocha colors, borders, gaps, font
- **conf/windowrules.conf** - Chrome focus-stealing prevention, PWA borders, popup rules
- **conf/autostart.conf** - services and daemons
- **location.conf** - coordinates for wlsunset (gitignored, stays at root)

Scripts are organized under `scripts/`:

- **scripts/workspaces/** - workspace management (create, rename, reorder, renumber, orignames utility, multi-monitor)
- **scripts/ux/** - daemons and UX helpers (opacity, battery, notifications, font size)
- **scripts/launchers/** - app launchers (Claude Code, GoLand, cheatsheet)

Tests live under `tests/`.

## Workspace management

Supports up to 20 workspaces (Super+1-0 and Super+Alt+1-0). Scripts for dynamic workspace operations:

- **new-workspace.sh** / **move-to-new-workspace.sh** - create at first free number
- **rename-workspace.sh** - fuzzel prompt to rename, with pre-filled current name
- **reorder-workspace.sh** - move workspace left/right, swapping with neighbors
- **renumber-workspaces.sh** - close numbering gaps by renumbering sequentially

All in `scripts/workspaces/`. These scripts coordinate with an "orignames" system (`ws-orignames-util.py`) that preserves workspace display names through renumber/reorder operations. The orignames state lives in `/tmp/ws-orignames.json` and is consumed by waybar's workspace truncation script.

## Waybar customizations

The waybar setup (in `~/.config/waybar/`) includes several custom modules and scripts that integrate with this sway config:

- **Icon font** - the bar uses **Font Awesome 6 Free** for all module icons (battery, network, clock, volume, etc.). This font must be installed for the bar to render correctly.
- **Claude Code status** - a custom COLRv0 font (`create-claude-font.py`) renders the Claude Code mascot as a glyph in the workspace name. `claude-status.sh` monitors Claude Code terminal sessions and appends a colored mascot to the workspace name: red when working, green when idle. The markers are Private Use Area characters (U+E000, U+E001) rendered by the custom font.
- **Workspace auto-collapse** - `waybar-auto-collapse.sh` + `ws-truncation.py` automatically truncate long workspace names when the bar gets crowded, and restore them when space frees up. This coordinates with the orignames system to preserve user-assigned names through truncation cycles.
- **Popup bars** - secondary waybar instances that appear on hover, providing a taskbar and additional controls without cluttering the main bar.
- **Calendar popup** - click the clock to toggle a GTK calendar overlay.
- **Timer** - countdown timer with fuzzel prompt and GTK alert overlay.
- **Night light toggle** - controls wlsunset from the bar.
- **Backup status** - shows Deja Dup backup state.
- **USB status** - monitors connected USB devices.
- **Audio selector** - quick audio output switching.

## Other scripts

- **opacity.sh** - daemon that dims unfocused windows (85%), with pin support via **toggle-pin.sh**
- **battery-monitor.sh** + **battery-warning.py** - low battery notification at 15%, GTK overlay at 5%
- **clear-slack-on-focus.sh** - dismiss Slack notifications from swaync when Slack gets focus
- **focus-notification-app.sh** - focus the window that sent a notification
- **github-workspace-fix.sh** - move GitHub PWA windows to the focused workspace on spawn
- **kitty-font-size.sh** - adjust kitty font size via Ctrl+Shift+scroll
- **cheatsheet.sh** - keybinding reference rendered in fuzzel
- **launch-claude.sh** - fuzzel directory picker to launch Claude Code in kitty
- **goland-launcher.sh** - fuzzel project/worktree picker to open GoLand

## Dependencies

Sway, waybar, fuzzel, swaylock, swayidle, kanshi, swaync, wlsunset, kitty, jq, grim, slurp, swappy, wl-copy, wl-paste, cliphist, wtype, playerctl, brightnessctl, pactl, notify-send, nm-applet, blueman-applet. Python with GTK3 + GtkLayerShell bindings for the battery overlay. Font Awesome 6 Free for waybar module icons.
