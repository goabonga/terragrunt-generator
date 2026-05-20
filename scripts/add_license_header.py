#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>


import argparse
import os
import sys

LICENSE_LINES = [
    "# SPDX-License-Identifier: MIT",
    "# Copyright (c) 2024-2026 Chris <goabonga@pm.me>",
]
LICENSE_HEADER = "\n".join(LICENSE_LINES)


def has_license(lines: list[str]) -> bool:
    lines = [line.strip() for line in lines]
    if lines and lines[0].startswith("#!"):
        return lines[2 : 2 + len(LICENSE_LINES)] == LICENSE_LINES
    return lines[: len(LICENSE_LINES)] == LICENSE_LINES


def add_license_header(file_path: str) -> bool:
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    if has_license(lines):
        return False  # already compliant

    new_lines: list[str] = []
    if lines and lines[0].startswith("#!"):
        new_lines.append(lines[0].rstrip("\n"))
        new_lines.append("")
        new_lines.append(LICENSE_HEADER)
        new_lines.append("")
        new_lines.extend(line.rstrip("\n") for line in lines[1:])
    else:
        new_lines.append(LICENSE_HEADER)
        new_lines.append("")
        new_lines.extend(line.rstrip("\n") for line in lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    print(f"License header added to: {file_path}")
    return True


def check_license(file_path: str) -> bool:
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()
    return has_license(lines)


# Directories that never carry project sources: virtualenvs, VCS
# metadata, build output and tool caches. Pruned from the walk so a
# scan rooted at "." does not flag third-party files (e.g. a wheel's
# bundled Cargo.toml under .venv).
PRUNE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "dist",
    "site",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "node_modules",
}


def process_directory(root: str, extensions: list[str], check_only: bool) -> int:
    missing_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            ext = os.path.splitext(filename)[1]
            no_ext = ext == ""
            match = (
                not extensions
                or (no_ext and "none" in extensions)
                or any(filename.endswith(f".{ext}") for ext in extensions)
            )
            if not match:
                continue

            if check_only:
                if not check_license(path):
                    missing_files.append(path)
            else:
                add_license_header(path)

    if check_only:
        if missing_files:
            print("Missing license headers in:")
            for f in missing_files:
                print(f" - {f}")
            return 1
        print("All files have license headers.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Add or check SPDX license headers.")
    parser.add_argument(
        "--path", type=str, default=".", help="Root directory to process"
    )
    parser.add_argument(
        "--types",
        type=str,
        default="py",
        help=(
            "Comma-separated list of file extensions (e.g. py,sh). "
            "Use 'none' to include files without extension, or pass an empty string "
            "to process all files regardless of extension."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Only check for missing license headers without modifying files. "
            "Exits 1 if any are missing."
        ),
    )
    args = parser.parse_args()

    extensions = [ext.strip() for ext in args.types.split(",") if ext.strip()]
    exit_code = process_directory(args.path, extensions, check_only=args.check)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
