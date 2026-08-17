#!/bin/bash
fuzzel --dmenu --prompt "Sway Keybindings " --width 60 --lines 30 <<'EOF'
Super+Return         Open terminal (kitty)
Super+d              App launcher (fuzzel)
Super+h/j/k/l        Move focus (vim keys)
Super+Shift+h/j/k/l  Move window (vim keys)
Super+Tab            Next workspace (this screen)
Super+Shift+Tab      Prev workspace (this screen)
Super+1-0            Switch to workspace 1-10
Super+Shift+1-0      Move window to workspace 1-10
Super+o              Focus other monitor
Super+Shift+o        Move window to other monitor
Super+Ctrl+o         Move workspace to other monitor
Super+Ctrl+h/l       Reorder workspace left/right
Super+Shift+Q        Close window
Super+f              Fullscreen
Super+v / Super+b    Split vertical / horizontal
Super+w              Tabbed layout
Super+s              Stacking layout
Super+e              Toggle split layout
Super+Shift+Space    Toggle floating
Super+Space          Toggle focus tiling/floating
Super+r              Resize mode (then h/j/k/l)
Super+Escape         Lock screen
Super+Shift+C        Reload config
Super+Shift+E        Exit sway
Print                Screenshot (full to clipboard)
Super+Print          Screenshot (region to clipboard)
Super+Shift+Print    Screenshot (edit with flameshot)
Super+n              New workspace
Super+Shift+n        Move window to new workspace
Super+Ctrl+n         Renumber workspaces (close gaps)
Super+,              Rename workspace
Super+Shift+,        Reset workspace name
Super+c              Clipboard history
Super+Shift+minus    Move window to scratchpad
Super+minus          Show scratchpad
Super+a              Focus parent
Super+p              Pin window (stay opaque unfocused)
3-finger swipe       Cycle workspaces
Super+t              Start timer
Super+?              This cheatsheet
Alt+c                Copy URL (any Chrome/PWA window)
EOF
