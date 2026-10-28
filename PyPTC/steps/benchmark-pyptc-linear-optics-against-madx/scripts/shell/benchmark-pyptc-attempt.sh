#!/usr/bin/env bash
# Step-level PyPTC/MAD-X benchmark orchestrator.
set -Eeuo pipefail

mode=user-run
if (($#)); then
  [[ $# == 1 && $1 == --smoke ]] || { printf 'Usage: %s [--smoke]\n' "$0" >&2; exit 2; }
  mode=agent-diagnostic
fi

script_path=$(readlink -f "${BASH_SOURCE[0]}")
script_dir=$(cd "$(dirname "$script_path")" && pwd -P)
step_root=$(cd "$script_dir/../.." && pwd -P)
repo_root=$(cd "$step_root/../.." && pwd -P)
python="$step_root/.venv/bin/python"
workflow="$step_root/scripts/python/benchmark_pyptc.py"
runs_root="$step_root/runs"
run_id=
run_dir=
stage=preflight
active_command=
active_log=

log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
run_logged() {
  local logfile=$1
  shift
  active_command=$(printf '%q ' "$@")
  active_log=$logfile
  log "Command: $active_command"
  "$@" 2>&1 | tee "$logfile"
  active_command=
  active_log=
}
failure_handler() {
  local exit_code=$? failed_command=${active_command:-${BASH_COMMAND:-unknown}}
  trap - ERR
  if [[ -n $run_dir && -d $run_dir ]]; then
    printf 'status=failed\nfailed_stage=%s\nfailed_command=%s\nfailed_log=%s\nexit_code=%s\n' \
      "$stage" "$failed_command" "${active_log:-not-applicable}" "$exit_code" >> "$run_dir/manifest.env" || true
    cat > "$run_dir/failure.md" <<EOF
# Run failed

- Run: $run_id
- Stage: $stage
- Command: $failed_command
- Log: ${active_log:-not-applicable}
- Exit code: $exit_code
- Partial evidence: $run_dir
EOF
    log "FAILED at $stage (exit $exit_code); inspect $run_dir/failure.md."
  else
    log "Preflight failed at $stage; no attempt was allocated."
  fi
  exit "$exit_code"
}
trap failure_handler ERR

[[ -x $python && -s $workflow ]] || { echo 'Benchmark environment or workflow module is missing; run ./scripts/shell/setup-benchmark.sh.' >&2; exit 3; }
mkdir -p "$runs_root"
highest=0
for directory in "$runs_root"/attempt-*; do
  [[ -d $directory ]] || continue
  number=${directory##*/attempt-}
  [[ $number =~ ^[0-9]+$ ]] || continue
  ((10#$number > highest)) && highest=$((10#$number))
done
number=$((highest + 1))
while :; do
  printf -v run_id 'attempt-%03d' "$number"
  run_dir="$runs_root/$run_id"
  if mkdir "$run_dir" 2>/dev/null; then break; fi
  number=$((number + 1))
done

run_type=user-skill-test
[[ $mode == agent-diagnostic ]] && run_type=agent-diagnostic
cat > "$run_dir/manifest.env" <<EOF
run_id=$run_id
status=running
run_type=$run_type
output_path=$run_dir
orchestrator=$script_path
orchestrator_sha256=$(sha256sum "$script_path" | awk '{print $1}')
workflow_module=$workflow
workflow_module_sha256=$(sha256sum "$workflow" | awk '{print $1}')
EOF
log "Allocated $run_id at $run_dir ($run_type)."

stage=run-pyptc-optics-workflow
run_logged "$run_dir/workflow.log" env \
  PYPTC_BENCHMARK_RUN_CLASS="$mode" \
  PYPTC_BENCHMARK_RUN_DIR="$run_dir" \
  PYPTC_BENCHMARK_ATTEMPT_ID="$run_id" \
  MPLCONFIGDIR="$step_root/.mplconfig" \
  "$python" "$workflow"

stage=validate-output-bundle
[[ -s $run_dir/result.json && -s $run_dir/report.md && -s $run_dir/plot-manifest.json ]] || {
  echo 'Workflow did not produce its canonical result, report, and plot manifest.' >&2; exit 3;
}
printf 'status=completed\nexecution_status=completed\n' >> "$run_dir/manifest.env"
log "Run complete. Review $run_dir/report.md and $run_dir/plots/cases/nominal.png."
