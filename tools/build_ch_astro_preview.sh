#!/usr/bin/env bash
# Build the Swiss multilingual MDX/Astro preview from canonical inputs.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/build_ch_astro_preview.sh --release-id ID [options]

Options:
  --release-id ID      Build reference shown in the footer (required).
  --beta               Show the BETA warning in all localized headers.
  --tag TAG             Stage questions from this question-pool Git tag.
  --feedback-url URL    Feedback form (default: https://50ohm.jp2s.ch/feedback).
  --help                Show this help.

The locale list is read from frontend/i18n.config.json. The wrapper stages,
prepares and builds every configured locale, then audits each output. It does
not publish a release.
EOF
}

release_id=''
beta=false
question_tag=''
feedback_url='https://50ohm.jp2s.ch/feedback'
while (($#)); do
  case "$1" in
    --release-id|--tag|--feedback-url)
      (($# >= 2)) || { printf 'Missing value for %s\n' "$1" >&2; exit 2; }
      case "$1" in
        --release-id) release_id=$2 ;;
        --tag) question_tag=$2 ;;
        --feedback-url) feedback_url=$2 ;;
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

repo_dir=$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")
orchestrator_dir=$(realpath "$repo_dir/..")
run_id=$(date +%Y%m%d-%H%M%S)
input_root="$orchestrator_dir/tmp/ch-input/$run_id"
build_root="$orchestrator_dir/tmp/ch-build/$run_id"
uv_cache_dir="$orchestrator_dir/tmp/next-uv-cache"
log_dir="$orchestrator_dir/tmp/ch-preview-logs/$run_id"
astro_cache_dir="$orchestrator_dir/tmp/astro-cache/$run_id"
mkdir -p "$log_dir"
mapfile -t locales < <(python -c 'import json, sys; from pathlib import Path; print("\n".join(json.loads(Path(sys.argv[1]).read_text())["locales"]))' "$repo_dir/frontend/i18n.config.json")

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
staging_args=(--skip-build)
if [[ -n $question_tag ]]; then staging_args+=(--tag "$question_tag"); fi
run_step stage env UV_CACHE_DIR="$uv_cache_dir" uv run --locked python \
  tools/run_multilingual_canonical_build.py "${staging_args[@]}"
popd >/dev/null

pushd "$repo_dir" >/dev/null
for locale in "${locales[@]}"; do
  run_step "prepare-$locale" env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 python \
    tools/prepare_ch_input.py --language "$locale" \
    --source "../50ohm-contents-ch/work/generator-input/$locale" \
    --output "$input_root/$locale" --content-repo ../50ohm-contents-ch \
    --question-repo ../50ohm-question-pool
  run_step "mdx-$locale" env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 ohm \
    --config "$input_root/$locale/build-config.json" --input "$input_root/$locale" \
    --output "$build_root/$locale" --format mdx \
    --edition NE --edition A --edition NEA --no-render-solutions
  run_step "media-$locale" env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 python \
    tools/qualify_mdx_assets.py --root "$build_root/$locale" --locale "$locale"
done

pushd frontend >/dev/null
if [[ ! -d node_modules ]]; then run_step npm-install npm ci --no-audit --no-fund; fi
run_step astro env XDG_CONFIG_HOME="$orchestrator_dir/tmp/astro-config" ASTRO_TELEMETRY_DISABLED=1 \
  OHM_BUILD_ROOT="$build_root" OHM_CH_INPUT_ROOT="$input_root" OHM_ASTRO_CACHE_DIR="$astro_cache_dir" \
  PUBLIC_SITE_PROFILE=ch PUBLIC_SHUFFLE_ANSWERS=false \
  PUBLIC_CH_RELEASE_ID="$release_id" PUBLIC_CH_BETA="$beta" \
  PUBLIC_CH_FEEDBACK_URL="$feedback_url" \
  npm run build
popd >/dev/null

for locale in "${locales[@]}"; do
  run_step "audit-$locale" env UV_CACHE_DIR="$uv_cache_dir" uv run --locked --python 3.14 python \
    tools/audit_ch_build.py --locale "$locale" \
    --source "$input_root/$locale" --build "$build_root/$locale" \
    --site "frontend/dist/$locale" --output "tmp/ch-audit-$run_id-$locale.json"
done
printf 'Sites: %s/frontend/dist/{%s}/index.html\n' "$repo_dir" "$(IFS=,; echo "${locales[*]}")"
printf 'Audits: %s/tmp/ch-audit-%s-{%s}.json\n' "$repo_dir" "$run_id" "$(IFS=,; echo "${locales[*]}")"
printf 'Logs: %s\n' "$log_dir"
popd >/dev/null
