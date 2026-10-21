#!/usr/bin/env bash
# Prompt for an electric ACC setup file, then scrape and export.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

choose_setup() {
  local files=()
  local choice=""
  local i=1
  local count=0

  shopt -s nullglob
  files=(ca_acc/electric/setups/*.yaml)
  shopt -u nullglob
  count=${#files[@]}

  if [[ "$count" -eq 0 ]]; then
    echo "No setup files found in ca_acc/electric/setups/." >&2
    exit 1
  fi

  echo "Starting ACC Electric Model data scraping..."
  echo ""
  echo "Select a setup file:"
  for f in "${files[@]}"; do
    echo "  ${i}) ${f}"
    i=$((i + 1))
  done
  echo ""

  while true; do
    printf "Enter a number or a path to a setup file: "
    IFS= read -r choice < /dev/tty || exit 1
    choice="${choice#"${choice%%[![:space:]]*}"}"
    choice="${choice%"${choice##*[![:space:]]}"}"

    if [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le "$count" ]]; then
      SETUP_PATH_CHOSEN="${files[$((choice - 1))]}"
      return 0
    fi
    if [[ -n "$choice" && -f "$choice" ]]; then
      SETUP_PATH_CHOSEN="$choice"
      return 0
    fi
    if [[ -n "$choice" && -f "ca_acc/electric/setups/$choice" ]]; then
      SETUP_PATH_CHOSEN="ca_acc/electric/setups/$choice"
      return 0
    fi
    echo "No setup file matches '${choice}'. Enter a number from the list or a path to a YAML file." >&2
  done
}

if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  return 0
fi

if [[ -n "${ACC_ELECTRIC_SETUP:-}" ]]; then
  SETUP_PATH_CHOSEN="$ACC_ELECTRIC_SETUP"
  echo "Starting ACC Electric Model data scraping..."
else
  choose_setup
fi

if [[ ! -f "$SETUP_PATH_CHOSEN" ]]; then
  echo "Setup file not found: ${SETUP_PATH_CHOSEN}" >&2
  exit 1
fi

echo "Setup file: ${SETUP_PATH_CHOSEN}"
echo ""
mkdir -p ca_acc/output
ACC_ELECTRIC_SETUP="$SETUP_PATH_CHOSEN" DB=ca_acc/output/ca_electric_acc.db uv run sqlmesh -p ca_acc/electric plan --auto-apply
echo "Exporting electric ACC table to CSV..."
time DB=ca_acc/output/ca_electric_acc.db uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM ca_electric_acc.ca_acc_layer1_smoothing.electric_acc_smoothed) TO 'ca_acc/output/full_ca_avoided_costs_acc_smoothed.csv' (HEADER, DELIMITER ',');\"); con.close()"
echo "CSV file saved to: ca_acc/output/full_ca_avoided_costs_acc_smoothed.csv"
