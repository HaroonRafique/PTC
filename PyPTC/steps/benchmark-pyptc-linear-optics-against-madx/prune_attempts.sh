#!/usr/bin/env bash
set -euo pipefail

step_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
repo_root=$(cd "$step_dir/../.." && pwd -P)
runs_root="$step_dir/runs"
ledger="$step_dir/review_ledger.csv"
feedback="$step_dir/feedback"
keep=3
apply=false

while (($#)); do
    case "$1" in
        --keep) (($# >= 2)) || { echo "--keep requires a positive integer" >&2; exit 2; }; keep=$2; shift 2 ;;
        --apply) apply=true; shift ;;
        *) echo "usage: $0 [--keep COUNT] [--apply]" >&2; exit 2 ;;
    esac
done
[[ $keep =~ ^[1-9][0-9]*$ ]] || { echo "--keep requires a positive integer" >&2; exit 2; }
[[ -d $runs_root ]] || { echo "No benchmark run directory: $runs_root" >&2; exit 1; }

mapfile -t attempt_ids < <(find "$runs_root" -mindepth 1 -maxdepth 1 -type d -name 'attempt-*' -printf '%f\n' | sort -r)
if ((${#attempt_ids[@]} <= keep)); then
    echo "Found ${#attempt_ids[@]} attempt bundles; retaining all (limit $keep)."
    exit 0
fi
for ((index=keep; index<${#attempt_ids[@]}; index++)); do
    attempt_id=${attempt_ids[index]}
    [[ $attempt_id =~ ^attempt-[0-9]{3}$ ]] || { echo "Refusing unexpected directory: $attempt_id" >&2; exit 1; }
    rg -Fq "$attempt_id" "$ledger" || { echo "Add ledger row before pruning $attempt_id." >&2; exit 1; }
    rg -l -F "$attempt_id" "$feedback" >/dev/null || { echo "Record $attempt_id in feedback before pruning." >&2; exit 1; }
done
if [[ $apply != true ]]; then
    echo "Dry run; would prune these older bundles:"
    for ((index=keep; index<${#attempt_ids[@]}; index++)); do printf '  %s\n' "${attempt_ids[index]}"; done
    echo "Pass --apply to remove them."
    exit 0
fi
for ((index=keep; index<${#attempt_ids[@]}; index++)); do
    attempt_id=${attempt_ids[index]}
    rm -rf -- "$runs_root/$attempt_id"
    printf 'Pruned %s\n' "$attempt_id"
done
