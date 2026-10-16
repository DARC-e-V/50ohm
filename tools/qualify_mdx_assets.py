"""Prefix root-relative course media URLs with their configured locale."""

import argparse
from pathlib import Path

from i18n_config import LOCALES


def qualify(root: Path, locale: str) -> int:
    if locale not in LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    changed = 0
    for path in root.rglob("*.mdx"):
        text = path.read_text(encoding="utf-8")
        updated = text.replace('src="/pictures/', f'src="/{locale}/pictures/')
        updated = updated.replace('src="/photos/', f'src="/{locale}/photos/')
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="One locale's generated MDX tree")
    parser.add_argument("--locale", choices=LOCALES, required=True)
    args = parser.parse_args()
    print(f"locale={args.locale} mdx_files_with_localized_media={qualify(args.root, args.locale)}")


if __name__ == "__main__":
    main()
