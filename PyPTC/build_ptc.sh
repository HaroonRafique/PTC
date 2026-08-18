#!/usr/bin/env bash
set -euo pipefail

pyptc_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${pyptc_dir}/build/build_ptc.sh" "$@"
