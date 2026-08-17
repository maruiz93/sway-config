# Agents

Instructions for AI agents working on this sway configuration.

## Project overview

This is a Sway (Wayland tiling compositor) desktop environment configuration. It is a personal dotfiles repo — the user runs this config daily on Fedora Linux.

The config is modular: `config` is the entry point and includes `.conf` files for devices, keymaps, workspaces, appearance, window rules, and autostart services. Helper scripts (bash and Python) are organized under `scripts/`:

- `scripts/workspaces/` - workspace management (create, rename, reorder, renumber, orignames, multi-monitor)
- `scripts/ux/` - daemons and UX helpers (opacity, battery, notifications, font size)
- `scripts/launchers/` - app launchers (Claude Code, GoLand, cheatsheet)

Tests live under `tests/`.

## Architecture

### Config files

All `.conf` files live in `conf/` and are included from `config` in explicit order (variables must load first). Sway uses i3-compatible config syntax. The mod key is Super. Navigation uses vim keys (h/j/k/l). Keyboard layout is Spanish with caps/escape swap.

### Workspace management system

The workspace scripts in `scripts/workspaces/` (`new-workspace.sh`, `rename-workspace.sh`, `reorder-workspace.sh`, `renumber-workspaces.sh`) form a coordinated system. They share an "orignames" mechanism via `ws-orignames-util.py` that preserves user-assigned workspace names through reorder and renumber operations.

State is stored in `/tmp/ws-orignames.json`. The orignames utility is also consumed by waybar's `ws-truncation.py` (in `~/.config/waybar/`) to restore display names after truncation.

When modifying any workspace script, consider the impact on orignames consistency across all operations.

### Companion configs

This config works alongside other dotfiles that live in separate directories:

- `~/.config/waybar/` - status bar config, modules, and scripts (including `ws-truncation.py` which reads orignames state)
- `~/.config/swaync/` - notification center config and scripts
- `~/.config/kanshi/` - multi-monitor profiles
- `~/.config/kitty/` - terminal config

Changes here may require coordinated changes in those directories, especially waybar.

### PR monitor

The `$mod+m` keybinding (in `keymaps.conf`) launches a tmux-based PR monitor, and `$mod+Shift+m` shows its legend. The scripts live in `~/.local/bin/`:

- `pr-monitor-launch.sh` — opens or attaches to the monitor tmux session in kitty
- `pr-monitor.sh` — creates a tmux session with three panes: authored PRs, assigned PRs, and all org PRs
- `pr-monitor-legend.sh` — shows a quick-reference popup for the column meanings
- `pr-list.sh` — the core script that fetches PR data via `gh` GraphQL and renders the status table (used by all panes)

## Conventions

- Scripts use `#!/bin/bash` and are made executable.
- Scripts use `swaymsg` and `jq` for querying/controlling sway.
- User interaction (prompts, pickers) goes through `fuzzel --dmenu`.
- The Catppuccin Mocha palette is used throughout (see `lookAndFeel.conf` for the color values).
- Variables like `$mod`, `$left`, `$right`, `$up`, `$down`, `$term`, `$menu` are defined in `variables.conf` and used across config files.
- `location.conf` is gitignored — it contains coordinates for wlsunset. Use the template: `LAT=<lat>`, `LON=<lon>`, `TEMP_NIGHT=3500`, `TEMP_DAY=6500`.

## Testing

`test-ws-orignames.py` contains unit and integration tests for the orignames utility. Run with:

```
pytest tests/test-ws-orignames.py -v
```

Tests cover: focus/unfocus cycles, reorder, swap, rename, renumber chains, and truncation edge cases.

## Common tasks

- **Adding a keybinding**: edit `conf/keymaps.conf` (or `conf/workspaces.conf` for workspace bindings). Update `scripts/launchers/cheatsheet.sh` if the binding is user-facing.
- **Adding an autostart service**: edit `conf/autostart.conf`. Use `exec` for one-shot, `exec_always` for reload-safe.
- **Adding a window rule**: edit `conf/windowrules.conf`.
- **Changing theme colors**: edit `conf/lookAndFeel.conf`. The Catppuccin Mocha values are defined there.
- **Adding a new workspace script**: add to `scripts/workspaces/` and coordinate with `ws-orignames-util.py` if it affects workspace numbering or naming.
- **Adding a new UX script**: add to `scripts/ux/`.
- **Adding a new launcher**: add to `scripts/launchers/`.
