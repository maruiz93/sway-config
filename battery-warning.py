#!/usr/bin/env python3
"""Catppuccin-themed battery warning overlay using gtk-layer-shell."""

import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, GLib, GtkLayerShell

TIMEOUT_S = 30
PCT = sys.argv[1] if len(sys.argv) > 1 else "?"

CSS = b"""
window {
    background-color: transparent;
}
#warning-box {
    background-color: rgba(30, 30, 46, 0.95);
    border: 2px solid #f38ba8;
    border-radius: 16px;
    padding: 40px 60px;
}
#pct-label {
    color: #f38ba8;
    font-family: "JetBrains Mono";
    font-size: 48px;
    font-weight: bold;
}
#msg-label {
    color: #cdd6f4;
    font-family: "JetBrains Mono";
    font-size: 18px;
    margin-top: 8px;
}
#hint-label {
    color: #585b70;
    font-family: "JetBrains Mono";
    font-size: 11px;
    margin-top: 16px;
}
"""

def main():
    win = Gtk.Window()

    GtkLayerShell.init_for_window(win)
    GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
    GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.ON_DEMAND)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.TOP, False)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.BOTTOM, False)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.LEFT, False)
    GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.RIGHT, False)

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        win.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)
    box.set_name("warning-box")

    pct_label = Gtk.Label(label=f"{PCT}%")
    pct_label.set_name("pct-label")
    box.pack_start(pct_label, False, False, 0)

    msg_label = Gtk.Label(label="charge now")
    msg_label.set_name("msg-label")
    box.pack_start(msg_label, False, False, 0)

    hint_label = Gtk.Label(label="click to dismiss")
    hint_label.set_name("hint-label")
    box.pack_start(hint_label, False, False, 0)

    event_box = Gtk.EventBox()
    event_box.add(box)
    event_box.connect("button-press-event", lambda *_: Gtk.main_quit())
    win.add(event_box)

    win.connect("destroy", Gtk.main_quit)
    win.connect("key-press-event", lambda *_: Gtk.main_quit())
    GLib.timeout_add_seconds(TIMEOUT_S, Gtk.main_quit)

    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
