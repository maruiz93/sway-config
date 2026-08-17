#!/usr/bin/env python3
"""Tests for workspace orignames interactions.

Tests that reorder, renumber, and rename operations correctly preserve
or clear original workspace names when truncation is active.

Run: python3 test-ws-orignames.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

UTIL = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'workspaces',
                    'ws-orignames-util.py')
TRUNCATION = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          '..', 'waybar', 'ws-truncation.py')


class OrigNamesUtilTest(unittest.TestCase):
    """Tests for ws-orignames-util.py commands."""

    def setUp(self):
        self.state_fd, self.state_file = tempfile.mkstemp(suffix='.json')
        os.close(self.state_fd)
        self._orig_state_file = None

    def tearDown(self):
        os.unlink(self.state_file)

    def _run(self, *args, state=None):
        if state is not None:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, UTIL] + list(args),
            capture_output=True, text=True, env=env
        )
        return result

    def _patch_state_file(self):
        """Monkey-patch STATE_FILE in util by running via wrapper."""
        pass

    def _run_with_state(self, *args, state=None):
        """Run the util with a custom STATE_FILE path."""
        wrapper = (
            f"import sys; "
            f"sys.argv = {list(args)!r}; "
            f"import importlib.util; "
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r}); "
            f"mod = importlib.util.module_from_spec(spec); "
            f"spec.loader.exec_module(mod); "
            f"mod.STATE_FILE = {self.state_file!r}; "
            f"mod.main()"
        )
        if state is not None:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        result = subprocess.run(
            [sys.executable, '-c', wrapper],
            capture_output=True, text=True
        )
        return result

    def _read_state(self):
        with open(self.state_file) as f:
            return json.load(f)

    # -- build-name tests --

    def test_build_name_no_orignames(self):
        """Without orignames, build-name uses the current name."""
        r = self._run_with_state(
            'util', 'build-name', '5', '3', '5:my-workspace',
            state={})
        self.assertEqual(r.stdout.strip(), '3:my-workspace')

    def test_build_name_with_truncated_name_uses_original(self):
        """With orignames, build-name restores the original label."""
        r = self._run_with_state(
            'util', 'build-name', '5', '3', '5:my-lo…',
            state={'5': '5:my-long-workspace'})
        self.assertEqual(r.stdout.strip(), '3:my-long-workspace')

    def test_build_name_preserves_marker(self):
        """build-name preserves the current claude-status marker."""
        marker = ' '  # claude-status marker
        r = self._run_with_state(
            'util', 'build-name', '5', '3', f'5:my-lo…{marker}',
            state={'5': '5:my-long-workspace'})
        self.assertEqual(r.stdout.rstrip('\n'), f'3:my-long-workspace{marker}')

    def test_build_name_number_only_workspace(self):
        """Workspace with no label returns just the new number."""
        r = self._run_with_state(
            'util', 'build-name', '5', '3', '5',
            state={})
        self.assertEqual(r.stdout.strip(), '3')

    # -- move-key tests --

    def test_move_key_updates_state(self):
        self._run_with_state(
            'util', 'move-key', '5', '3',
            state={'5': '5:my-long-workspace'})
        state = self._read_state()
        self.assertNotIn('5', state)
        self.assertEqual(state['3'], '3:my-long-workspace')

    def test_move_key_noop_when_missing(self):
        self._run_with_state(
            'util', 'move-key', '5', '3',
            state={'7': '7:other'})
        state = self._read_state()
        self.assertEqual(state, {'7': '7:other'})

    # -- swap-keys tests --

    def test_swap_keys_both_present(self):
        self._run_with_state(
            'util', 'swap-keys', '3', '5',
            state={'3': '3:alpha', '5': '5:beta'})
        state = self._read_state()
        self.assertEqual(state['3'], '3:beta')
        self.assertEqual(state['5'], '5:alpha')

    def test_swap_keys_one_present(self):
        self._run_with_state(
            'util', 'swap-keys', '3', '5',
            state={'3': '3:alpha'})
        state = self._read_state()
        self.assertNotIn('3', state)
        self.assertEqual(state['5'], '5:alpha')

    def test_swap_keys_neither_present(self):
        self._run_with_state(
            'util', 'swap-keys', '3', '5',
            state={'7': '7:other'})
        state = self._read_state()
        self.assertEqual(state, {'7': '7:other'})

    # -- delete-key tests --

    def test_delete_key(self):
        self._run_with_state(
            'util', 'delete-key', '5',
            state={'5': '5:my-workspace', '3': '3:other'})
        state = self._read_state()
        self.assertNotIn('5', state)
        self.assertEqual(state['3'], '3:other')

    def test_delete_key_noop_when_missing(self):
        self._run_with_state(
            'util', 'delete-key', '5',
            state={'3': '3:other'})
        state = self._read_state()
        self.assertEqual(state, {'3': '3:other'})


class TruncationInteractionTest(unittest.TestCase):
    """Integration tests for ws-truncation.py + orignames interactions.

    These test the truncation logic in isolation by calling main() with
    mock swaymsg (since we can't rename workspaces without sway).
    """

    def setUp(self):
        self.state_fd, self.state_file = tempfile.mkstemp(suffix='.json')
        os.close(self.state_fd)
        with open(self.state_file, 'w') as f:
            json.dump({}, f)

    def tearDown(self):
        os.unlink(self.state_file)

    def _make_workspaces(self, names, output='eDP-1', focused_idx=0):
        ws = []
        for i, name in enumerate(names):
            num = int(name.split(':')[0]) if ':' in name else int(name)
            ws.append({
                'num': num,
                'name': name,
                'output': output,
                'focused': i == focused_idx,
                'visible': True,
            })
        return ws

    def _make_outputs(self, width=1920, name='eDP-1'):
        return [{'name': name, 'active': True,
                 'rect': {'width': width, 'x': 0, 'y': 0, 'height': 1080}}]

    def _make_master_config(self):
        return [{'output': 'eDP-1',
                 '_collapse': {
                     'pinned': ['clock'],
                     'collapsible': [],
                     'module_widths': {'clock': 80},
                 },
                 'modules-right': ['clock']}]

    def _run_truncation(self, outputs, workspaces, master_config,
                        char_w=7.2, ws_pad=26, ws_cont=30, safety=100,
                        mod_gap=6):
        """Run ws-truncation.py logic and return (renames, new_orignames)."""
        master_fd, master_file = tempfile.mkstemp(suffix='.json')
        os.close(master_fd)
        with open(master_file, 'w') as f:
            json.dump(master_config, f)

        renames = []
        try:
            wrapper = f"""
import json, sys, os
sys.path.insert(0, os.path.dirname({TRUNCATION!r}))

# Load and patch the module
import importlib.util
spec = importlib.util.spec_from_file_location('trunc', {TRUNCATION!r})
mod = importlib.util.module_from_spec(spec)
mod.STATE_FILE = {self.state_file!r}

# Capture renames instead of calling swaymsg
captured = []
def mock_rename(old, new):
    captured.append((old, new))
mod.sway_rename = mock_rename

spec.loader.exec_module(mod)

# Call with test data
sys.argv = ['ws-truncation.py',
    json.dumps({json.dumps(outputs)!s}),
    json.dumps({json.dumps(workspaces)!s}),
    str({char_w}), str({ws_pad}), str({ws_cont}), str({safety}),
    {master_file!r}, str({mod_gap})]

try:
    mod.main()
except SystemExit as e:
    pass

print(json.dumps({{"renames": captured}}))
"""
            # Fix: we need to pass the actual JSON strings
            wrapper = (
                "import json, sys, os\n"
                f"sys.path.insert(0, os.path.dirname({TRUNCATION!r}))\n"
                "import importlib.util\n"
                f"spec = importlib.util.spec_from_file_location('trunc', {TRUNCATION!r})\n"
                "mod = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(mod)\n"
                f"mod.STATE_FILE = {self.state_file!r}\n"
                "captured = []\n"
                "def mock_rename(old, new):\n"
                "    captured.append((old, new))\n"
                "mod.sway_rename = mock_rename\n"
                f"sys.argv = ['ws-truncation.py',\n"
                f"    {json.dumps(json.dumps(outputs))},\n"
                f"    {json.dumps(json.dumps(workspaces))},\n"
                f"    '{char_w}', '{ws_pad}', '{ws_cont}', '{safety}',\n"
                f"    {master_file!r}, '{mod_gap}']\n"
                "try:\n"
                "    mod.main()\n"
                "except SystemExit:\n"
                "    pass\n"
                "print(json.dumps({'renames': captured}))\n"
            )
            result = subprocess.run(
                [sys.executable, '-c', wrapper],
                capture_output=True, text=True
            )
            if result.returncode != 0 and result.stderr:
                print(f"STDERR: {result.stderr}", file=sys.stderr)

            if result.stdout.strip():
                data = json.loads(result.stdout.strip())
                renames = data.get('renames', [])
        finally:
            os.unlink(master_file)

        with open(self.state_file) as f:
            new_orignames = json.load(f)

        return renames, new_orignames

    def test_origname_survives_focus_unfocus_cycle(self):
        """Origname must not be deleted when the focused workspace is restored.

        Previously, ws-truncation.py deleted the origname on focus and
        re-saved it on unfocus. If anything interrupted the re-save
        (race, error, truncation threshold change), the origname was
        permanently lost. Now the origname persists through focus.
        """
        # Step 1: truncate workspaces on a narrow screen
        outputs = self._make_outputs(width=600)
        ws = self._make_workspaces([
            '1:mail', '2:slack', '3:very-long-workspace-name',
            '4:another-long-name-here', '5:short'
        ], focused_idx=4)  # ws 5 focused
        master = self._make_master_config()

        renames, orignames = self._run_truncation(outputs, ws, master)

        # Verify some workspaces got truncated and orignames saved
        truncated_keys = list(orignames.keys())
        self.assertTrue(len(truncated_keys) > 0, 'expected truncation')

        # Step 2: simulate focusing a truncated workspace
        # Pick a workspace that was truncated
        trunc_key = truncated_keys[0]
        trunc_num = int(trunc_key)
        stored_orig = orignames[trunc_key]

        # Build a workspace list where the truncated ws is now focused
        truncated_names = {}
        for old, new in renames:
            for w in ws:
                if w['name'] == old:
                    truncated_names[w['num']] = new
                    break

        ws_focused = self._make_workspaces([
            truncated_names.get(w['num'], w['name'])
            for w in sorted(ws, key=lambda x: x['num'])
        ], focused_idx=[w['num'] for w in sorted(ws, key=lambda x: x['num'])].index(trunc_num))

        renames2, orignames2 = self._run_truncation(outputs, ws_focused, master)

        # The origname must still exist after focus restoration
        self.assertIn(trunc_key, orignames2,
                      f'origname for ws {trunc_key} must survive focus')
        self.assertEqual(orignames2[trunc_key], stored_orig,
                         'origname value must be unchanged after focus')

        # Step 3: apply the restoration rename, then simulate unfocusing
        # (switch focus back to ws 5 — the truncated ws is unfocused again)
        restored_names = dict(truncated_names)
        for old, new in renames2:
            for w in ws_focused:
                if w['name'] == old:
                    restored_names[w['num']] = new
                    break

        ws_unfocused = self._make_workspaces([
            restored_names.get(w['num'], w['name'])
            for w in sorted(ws, key=lambda x: x['num'])
        ], focused_idx=[w['num'] for w in sorted(ws, key=lambda x: x['num'])].index(5))

        renames3, orignames3 = self._run_truncation(outputs, ws_unfocused, master)

        # Origname must still be there after unfocus
        self.assertIn(trunc_key, orignames3,
                      f'origname for ws {trunc_key} must survive unfocus')

        # Step 4: focus the workspace AGAIN — it must restore to full name
        re_truncated_names = dict(restored_names)
        for old, new in renames3:
            for w in ws_unfocused:
                if w['name'] == old:
                    re_truncated_names[w['num']] = new
                    break

        ws_refocused = self._make_workspaces([
            re_truncated_names.get(w['num'], w['name'])
            for w in sorted(ws, key=lambda x: x['num'])
        ], focused_idx=[w['num'] for w in sorted(ws, key=lambda x: x['num'])].index(trunc_num))

        renames4, orignames4 = self._run_truncation(outputs, ws_refocused, master)

        # Must have generated a rename restoring the full name
        restored_any = any(
            new.startswith(f'{trunc_num}:') and '…' not in new
            for old, new in renames4
        )
        self.assertTrue(restored_any,
                        f'focusing ws {trunc_num} again must restore full name')
        # And origname must still be there
        self.assertIn(trunc_key, orignames4,
                      f'origname for ws {trunc_key} must survive second focus')

    def test_truncation_stores_orignames(self):
        """When names are truncated, originals are stored in state."""
        outputs = self._make_outputs(width=600)
        ws = self._make_workspaces([
            '1:mail', '2:slack', '3:very-long-workspace-name',
            '4:another-long-name-here', '5:short'
        ])
        master = self._make_master_config()

        renames, orignames = self._run_truncation(outputs, ws, master)

        # At least some workspaces should have been truncated
        if renames:
            # Check that truncated names end with ellipsis
            for old, new in renames:
                self.assertIn('…', new)
            # Orignames should have entries for truncated workspaces
            self.assertTrue(len(orignames) > 0)

    def test_scenario_truncate_then_reorder(self):
        """Simulate: truncation happens, then workspace is reordered.

        This is the core bug scenario. After truncation, orignames maps
        old_num -> original_name. Reorder changes the workspace number.
        The utility should carry the origname to the new key.
        """
        # Step 1: Set up orignames as if truncation happened
        with open(self.state_file, 'w') as f:
            json.dump({'5': '5:very-long-workspace-name'}, f)

        # Step 2: Simulate reorder from 5 to 3 using build-name
        wrapper = (
            "import importlib.util, sys, json\n"
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.STATE_FILE = {self.state_file!r}\n"
            "mod.cmd_build_name('5', '3', '5:very-l…')\n"
        )
        result = subprocess.run(
            [sys.executable, '-c', wrapper],
            capture_output=True, text=True
        )
        new_name = result.stdout.strip()
        self.assertEqual(new_name, '3:very-long-workspace-name',
                         'build-name should restore original, not carry truncated')

        # Step 3: move-key should update orignames
        wrapper = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.STATE_FILE = {self.state_file!r}\n"
            "mod.cmd_move_key('5', '3')\n"
        )
        subprocess.run([sys.executable, '-c', wrapper], capture_output=True)
        with open(self.state_file) as f:
            state = json.load(f)
        self.assertNotIn('5', state)
        self.assertEqual(state['3'], '3:very-long-workspace-name')

    def test_scenario_truncate_then_swap(self):
        """Simulate: both workspaces truncated, then swapped."""
        with open(self.state_file, 'w') as f:
            json.dump({
                '3': '3:alpha-long-name',
                '5': '5:beta-long-name',
            }, f)

        wrapper = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.STATE_FILE = {self.state_file!r}\n"
            "mod.cmd_swap_keys('3', '5')\n"
        )
        subprocess.run([sys.executable, '-c', wrapper], capture_output=True)
        with open(self.state_file) as f:
            state = json.load(f)
        self.assertEqual(state['3'], '3:beta-long-name')
        self.assertEqual(state['5'], '5:alpha-long-name')

    def test_scenario_rename_clears_origname(self):
        """After explicit rename, orignames entry should be gone."""
        with open(self.state_file, 'w') as f:
            json.dump({'5': '5:old-long-name'}, f)

        wrapper = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.STATE_FILE = {self.state_file!r}\n"
            "mod.cmd_delete_key('5')\n"
        )
        subprocess.run([sys.executable, '-c', wrapper], capture_output=True)
        with open(self.state_file) as f:
            state = json.load(f)
        self.assertNotIn('5', state)

    def test_scenario_renumber_chain(self):
        """Simulate renumbering: 3,5,8 -> 1,2,3 with orignames."""
        with open(self.state_file, 'w') as f:
            json.dump({
                '5': '5:long-workspace-five',
                '8': '8:long-workspace-eight',
            }, f)

        # Renumber simulates: 3->1 (no origname), 5->2, 8->3
        moves = [('5', '2'), ('8', '3')]
        for old, new in moves:
            wrapper = (
                "import importlib.util, sys\n"
                f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
                "mod = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(mod)\n"
                f"mod.STATE_FILE = {self.state_file!r}\n"
                f"mod.cmd_move_key('{old}', '{new}')\n"
            )
            subprocess.run([sys.executable, '-c', wrapper], capture_output=True)

        with open(self.state_file) as f:
            state = json.load(f)
        self.assertEqual(state['2'], '2:long-workspace-five')
        self.assertEqual(state['3'], '3:long-workspace-eight')
        self.assertNotIn('5', state)
        self.assertNotIn('8', state)

    def test_truncation_does_not_save_already_truncated_as_original(self):
        """If a name already has an ellipsis and no origname, truncation must
        not save it as the 'original' and must not truncate further.

        This is the CWRF scenario: workspace was truncated to 'CW...',
        then reordered (losing origname), leaving a permanently truncated
        name with no way to recover.
        """
        outputs = self._make_outputs(width=600)
        ws = self._make_workspaces([
            '1:mail', '2:slack', '3:already-tru…',
            '4:another-tru…', '5:short'
        ])
        master = self._make_master_config()

        renames, orignames = self._run_truncation(outputs, ws, master)

        # Workspaces 3 and 4 already have ellipsis — orignames must NOT
        # save them as originals (that would cement the truncated name)
        self.assertNotIn('3', orignames,
                         'must not save already-truncated name as original')
        self.assertNotIn('4', orignames,
                         'must not save already-truncated name as original')

        # They must not appear in renames either (no further truncation)
        renamed_sources = [old for old, new in renames]
        for src in renamed_sources:
            self.assertNotIn('already-tru…', src,
                             'must not re-truncate already-truncated name')
            self.assertNotIn('another-tru…', src,
                             'must not re-truncate already-truncated name')

    def test_build_name_without_origname_preserves_ellipsis(self):
        """Without orignames entry, build-name passes through as-is.

        This handles the case where orignames was already lost (the bug
        scenario before the fix). At least we don't make it worse.
        """
        with open(self.state_file, 'w') as f:
            json.dump({}, f)

        wrapper = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('util', {UTIL!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.STATE_FILE = {self.state_file!r}\n"
            "mod.cmd_build_name('5', '3', '5:my-lo…')\n"
        )
        result = subprocess.run(
            [sys.executable, '-c', wrapper],
            capture_output=True, text=True
        )
        # Without orignames, passes through the current name (truncated or not)
        self.assertEqual(result.stdout.strip(), '3:my-lo…')


class TruncationUnitTest(unittest.TestCase):
    """Unit tests for ws-truncation.py helper functions."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('trunc', TRUNCATION)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.mod.STATE_FILE = '/tmp/test-ws-orignames-unit.json'
        self.mod.sway_rename = lambda old, new: None

    def test_strip_marker_no_marker(self):
        base, marker = self.mod.strip_marker('5:workspace')
        self.assertEqual(base, '5:workspace')
        self.assertEqual(marker, '')

    def test_strip_marker_with_marker(self):
        for m in self.mod.MARKERS:
            base, marker = self.mod.strip_marker(f'5:workspace{m}')
            self.assertEqual(base, '5:workspace')
            self.assertEqual(marker, m)

    def test_get_bar_for_output_direct(self):
        bars = [{'output': 'eDP-1'}, {'output': 'DP-6'}]
        self.assertEqual(self.mod.get_bar_for_output(bars, 'eDP-1'), bars[0])
        self.assertEqual(self.mod.get_bar_for_output(bars, 'DP-6'), bars[1])

    def test_get_bar_for_output_negated(self):
        bars = [{'output': '!eDP-1'}]
        self.assertIsNone(self.mod.get_bar_for_output(bars, 'eDP-1'))
        self.assertEqual(self.mod.get_bar_for_output(bars, 'DP-6'), bars[0])


if __name__ == '__main__':
    unittest.main()
