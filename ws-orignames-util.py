#!/usr/bin/env python3
"""Utility for managing workspace original names state.

Used by reorder-workspace.sh, renumber-workspaces.sh, and rename-workspace.sh
to keep /tmp/ws-orignames.json consistent when workspace numbers change.

Commands:
  build-name OLD_NUM NEW_NUM CURRENT_NAME
    Print the new workspace name, using the stored original label if the
    current name is truncated.  Preserves claude-status markers.

  move-key OLD_NUM NEW_NUM
    Move the orignames entry from OLD_NUM to NEW_NUM (updating the stored
    number prefix).

  swap-keys NUM1 NUM2
    Swap orignames entries for NUM1 and NUM2.

  delete-key NUM
    Remove the orignames entry for NUM.
"""

import json
import os
import sys

STATE_FILE = '/tmp/ws-orignames.json'
MARKERS = (' ', ' ')


def read_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(data):
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(data, f)
    os.rename(tmp, STATE_FILE)


def strip_marker(name):
    for m in MARKERS:
        if name.endswith(m):
            return name[:-len(m)], m
    return name, ''


def extract_label(full_name, num):
    """Extract the label part after 'NUM:' prefix."""
    prefix = f'{num}:'
    if full_name.startswith(prefix):
        return full_name[len(prefix):]
    return ''


def cmd_build_name(old_num, new_num, current_name):
    """Build a new workspace name, preserving truncation if present."""
    state = read_state()
    key = str(old_num)
    _, marker = strip_marker(current_name)
    base_current, _ = strip_marker(current_name)

    if key in state:
        current_label = extract_label(base_current, old_num)
        if '…' in current_label:
            # Preserve truncated display form, just change the number prefix
            print(f'{new_num}:{current_label}{marker}')
            return
        stored = state[key]
        base_label, _ = strip_marker(stored)
        label = extract_label(base_label, old_num)
    else:
        label = extract_label(current_name, old_num)
        if not label:
            print(str(new_num))
            return
        base_label, _ = strip_marker(f'{old_num}:{label}')
        label = extract_label(base_label, old_num)

    print(f'{new_num}:{label}{marker}')


def cmd_move_key(old_num, new_num):
    state = read_state()
    old_key, new_key = str(old_num), str(new_num)
    if old_key not in state:
        return
    stored = state.pop(old_key)
    old_prefix = f'{old_num}:'
    if stored.startswith(old_prefix):
        stored = f'{new_num}:{stored[len(old_prefix):]}'
    state[new_key] = stored
    write_state(state)


def cmd_swap_keys(num1, num2):
    state = read_state()
    k1, k2 = str(num1), str(num2)
    v1 = state.get(k1)
    v2 = state.get(k2)

    changed = False
    if v1 is not None:
        p1 = f'{num1}:'
        if v1.startswith(p1):
            v1 = f'{num2}:{v1[len(p1):]}'
        state[k2] = v1
        changed = True
    elif k2 in state:
        del state[k2]
        changed = True

    if v2 is not None:
        p2 = f'{num2}:'
        if v2.startswith(p2):
            v2 = f'{num1}:{v2[len(p2):]}'
        state[k1] = v2
        changed = True
    elif k1 in state:
        del state[k1]
        changed = True

    if changed:
        write_state(state)


def cmd_delete_key(num):
    state = read_state()
    key = str(num)
    if key in state:
        del state[key]
        write_state(state)


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'build-name':
        cmd_build_name(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'move-key':
        cmd_move_key(sys.argv[2], sys.argv[3])
    elif cmd == 'swap-keys':
        cmd_swap_keys(sys.argv[2], sys.argv[3])
    elif cmd == 'delete-key':
        cmd_delete_key(sys.argv[2])
    else:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
