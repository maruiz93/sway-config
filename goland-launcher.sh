#!/bin/bash
GOLAND=$(ls -d /opt/JetBrains/GoLand-*/bin/goland.sh 2>/dev/null | sort -V | tail -1)
[ -z "$GOLAND" ] && exit 1

if ! pgrep -f "goland" > /dev/null 2>&1; then
    "$GOLAND" &
    exit 0
fi

declare -A repo_paths
DEV_ENVS=(
    "fullsend:$HOME/Workspace/fullsend/fullsend-dev-env/repos"
    "k9e:$HOME/Workspace/k9e/k9e-dev-env/repos"
)

for entry in "${DEV_ENVS[@]}"; do
    prefix="${entry%%:*}"
    dir="${entry#*:}"
    [ -d "$dir" ] || continue
    for repo in "$dir"/*/; do
        [ -d "$repo/.git" ] || [ -f "$repo/.git" ] || continue
        name=$(basename "$repo")
        repo_paths["$prefix / $name"]="${repo%/}"
    done
done

while IFS= read -r dir; do
    in_dev_env=false
    for entry in "${DEV_ENVS[@]}"; do
        dev_dir="${entry#*:}"
        [[ "$dir" == "$dev_dir"* ]] && { in_dev_env=true; break; }
    done
    $in_dev_env && continue
    name=$(basename "$dir")
    repo_paths["$name"]="$dir"
done < <(find ~/Workspace -maxdepth 4 -name "go.mod" -not -path "*/vendor/*" -not -path "*/.worktrees/*" -printf '%h\n' 2>/dev/null | sort -u)

choice=$(printf '%s\n' "${!repo_paths[@]}" | sort | fuzzel --dmenu --prompt "GoLand: project")
[ -z "$choice" ] && exit 0
repo="${repo_paths[$choice]}"

mapfile -t wt_lines < <(git -C "$repo" worktree list 2>/dev/null)
if [ "${#wt_lines[@]}" -le 1 ]; then
    "$GOLAND" "$repo" &
    exit 0
fi

declare -A wt_map
for line in "${wt_lines[@]}"; do
    path=$(echo "$line" | awk '{print $1}')
    [ -d "$path" ] || continue
    if [[ "$line" =~ \[([^]]+)\] ]]; then
        label="${BASH_REMATCH[1]}"
    else
        label="(detached) $(basename "$path")"
    fi
    wt_map["$label"]="$path"
done

wt=$(printf '%s\n' "${!wt_map[@]}" | sort | fuzzel --dmenu --prompt "GoLand: worktree")
[ -z "$wt" ] && exit 0

"$GOLAND" "${wt_map[$wt]}" &
