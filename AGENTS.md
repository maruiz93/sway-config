# Agents

Instructions for AI agents working on this sway configuration.

## Project overview

This is a Sway (Wayland tiling compositor) desktop environment configuration. It is a personal dotfiles repo — the user runs this config daily on Fedora Linux.

The config is modular: `config` is the entry point and includes `.conf` files for devices, keymaps, workspaces, appearance, window rules, and autostart services. Helper scripts (bash and Python) handle workspace management, UX features, and app launchers.

## Architecture

### Config files

All `.conf` files are included from `config`. Sway uses i3-compatible config syntax. The mod key is Super. Navigation uses vim keys (h/j/k/l). Keyboard layout is Spanish with caps/escape swap.

### Workspace management system

The workspace scripts (`new-workspace.sh`, `rename-workspace.sh`, `reorder-workspace.sh`, `renumber-workspaces.sh`) form a coordinated system. They share an "orignames" mechanism via `ws-orignames-util.py` that preserves user-assigned workspace names through reorder and renumber operations.

State is stored in `/tmp/ws-orignames.json`. The orignames utility is also consumed by waybar's `ws-truncation.py` (in `~/.config/waybar/`) to restore display names after truncation.

When modifying any workspace script, consider the impact on orignames consistency across all operations.

### Companion configs

This config works alongside other dotfiles that live in separate directories:

- `~/.config/waybar/` - status bar config, modules, and scripts (including `ws-truncation.py` which reads orignames state)
- `~/.config/swaync/` - notification center config and scripts
- `~/.config/kanshi/` - multi-monitor profiles
- `~/.config/kitty/` - terminal config

Changes here may require coordinated changes in those directories, especially waybar.

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
pytest test-ws-orignames.py -v
```

Tests cover: focus/unfocus cycles, reorder, swap, rename, renumber chains, and truncation edge cases.

## Common tasks

- **Adding a keybinding**: edit `keymaps.conf` (or `workspaces.conf` for workspace bindings). Update `cheatsheet.sh` if the binding is user-facing.
- **Adding an autostart service**: edit `autostart.conf`. Use `exec` for one-shot, `exec_always` for reload-safe.
- **Adding a window rule**: edit `windowrules.conf`.
- **Changing theme colors**: edit `lookAndFeel.conf`. The Catppuccin Mocha values are defined there.
- **Adding a new workspace script**: coordinate with `ws-orignames-util.py` if it affects workspace numbering or naming.
