#!/usr/bin/env bash
set -euo pipefail

step_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pyptc_dir="$(cd "${step_dir}/../.." && pwd)"
venv_dir="${step_dir}/.venv"

python3 -m venv --system-site-packages "${venv_dir}"
"${venv_dir}/bin/python" -m pip install --disable-pip-version-check -r "${step_dir}/requirements.txt"

for tool in git meson ninja gfortran nm; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    printf 'Required tool is missing from PATH: %s\n' "${tool}" >&2
    exit 1
  fi
done

printf 'Admission environment ready.\n'
printf 'Python: %s\n' "$("${venv_dir}/bin/python" --version 2>&1)"
printf 'PyPTC source: %s\n' "${pyptc_dir}"
printf 'Activate with: source %q/bin/activate\n' "${venv_dir}"
