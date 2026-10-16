#!/usr/bin/env bash
# Build the Swiss German MDX/Astro preview from current canonical inputs.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/build_ch_astro_preview.sh --release-id ID [options]

Options:
  --release-id ID      Build reference shown in the footer (required).
  --beta               Show the Swiss BETA warning in the header.
  --tag TAG             Stage questions from this question-pool Git tag.
  --feedback-url URL    Feedback form (default: https://50ohm.jp2s.ch/feedback).
  --fr-url URL          French site URL for the language control.
  --it-url URL          Italian site URL for the language control.
  --help                Show this help.

Only the German Astro preview is built. FR/IT controls remain non-clickable
unless their existing site URLs are supplied. No release is published.
EOF
}

release_id=''
beta=false
question_tag=''
feedback_url='https://50ohm.jp2s.ch/feedback'
fr_url=''
it_url=''
while (($#)); do
  case "$1" in
    --release-id|--tag|--feedback-url|--fr-url|--it-url)
      (($# >= 2)) || { printf 'Missing value for %s\n' "$1" >&2; exit 2; }
      case "$1" in
        --release-id) release_id=$2 ;;
        --tag) question_tag=$2 ;;
        --feedback-url) feedback_url=$2 ;;
        --fr-url) fr_url=$2 ;;
        --it-url) it_url=$2 ;;
      esac
      shift 2 ;;
    --beta) beta=true; shift ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ $release_id =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$ ]] &&
  [[ $release_id != *..* ]] && [[ $release_id != *. ]] && [[ $release_id != *.lock ]] || {
    printf 'Invalid or missing --release-id\n' >&2; exit 2;
  }
[[ $feedback_url =~ ^https?://[^/?#]+ ]] || { printf 'Invalid --feedback-url\n' >&2; exit 2; }
for site_url in "$fr_url" "$it_url"; do
  [[ -z $site_url || $site_url =~ ^https?://[^[:space:]]+$ ]] || {
    printf 'FR/IT URLs must be absolute HTTP(S) URLs\n' >&2; exit 2;
  }
done

repo_dir=$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")
orchestrator_dir=$(realpath "$repo_dir/..")
run_id=$(date +%Y%m%d-%H%M%S)
input_dir="tmp/ch-input/de-$run_id"
build_dir="tmp/ch-build/de-$run_id"
uv_cache_dir="$orchestrator_dir/tmp/next-uv-cache"
log_dir="$orchestrator_dir/tmp/ch-preview-logs/$run_id"
mkdir -p "$log_dir"

run_step() {
  local name=$1
  shift
  printf '%s ...\n' "$name"
  if "$@" >"$log_dir/$name.log" 2>&1; then
    printf '%s: done\n' "$name"
  else
    printf '%s failed; log: %s/%s.log\n' "$name" "$log_dir" "$name" >&2
    tail -n 50 "$log_dir/$name.log" >&2
    exit 1
  fi
}

pushd "$orchestrator_dir/50ohm-contents-ch" >/dev/null
staging_args=(--language de --skip-build)
if [[ -n $question_tag ]]; then staging_args+=(--tag "$question_tag"); fi
run_step stage env UV_CACHE_DIR="$uv_cache_dir" uv run --locked python \
  tools/run_multilingual_canonical_build.py "${staging_args[@]}"
popd >/dev/null

pushd "$repo_dir" >/dev/null
run_step prepare env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 python \
  tools/prepare_ch_input.py \
  --source ../50ohm-contents-ch/work/generator-input/de \
  --output "$input_dir" --content-repo ../50ohm-contents-ch \
  --question-repo ../50ohm-question-pool
run_step mdx env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 ohm \
  --config "$input_dir/build-config.json" --input "$input_dir" \
  --output "$build_dir" --format mdx \
  --edition NE --edition A --edition NEA --no-render-solutions

pushd frontend >/dev/null
if [[ ! -d node_modules ]]; then run_step npm-install npm ci --no-audit --no-fund; fi
run_step astro env XDG_CONFIG_HOME="$orchestrator_dir/tmp/astro-config" ASTRO_TELEMETRY_DISABLED=1 \
  OHM_BUILD_DIR="../$build_dir" OHM_CH_INPUT_DIR="../$input_dir" \
  PUBLIC_SITE_PROFILE=ch PUBLIC_SHUFFLE_ANSWERS=false \
  PUBLIC_CH_RELEASE_ID="$release_id" PUBLIC_CH_BETA="$beta" \
  PUBLIC_CH_FEEDBACK_URL="$feedback_url" \
  PUBLIC_CH_FR_URL="$fr_url" PUBLIC_CH_IT_URL="$it_url" \
  npm run build
popd >/dev/null

run_step audit env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 python \
  tools/audit_ch_build.py --source "$input_dir" --build "$build_dir" \
  --site frontend/dist --output "tmp/ch-audit-$run_id.json"
printf 'Site: %s/frontend/dist/index.html\nAudit: %s/tmp/ch-audit-%s.json\n' "$repo_dir" "$repo_dir" "$run_id"
printf 'Logs: %s\n' "$log_dir"
popd >/dev/null
