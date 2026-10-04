#!/usr/bin/env python3
"""Validate the packs in packs/ and build installable archives into dist/.

Usage:
    python3 tools/build.py            # validate, then build every pack
    python3 tools/build.py --check    # validate only (what CI runs)
    python3 tools/build.py permafrost # build a single pack by directory name

A pack directory containing manifest.json is built as a .mcpack. A directory
containing behavior_pack/ and/or resource_pack/ is built as a .mcaddon.
Output names come from the directory name and the manifest version.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
DIST = ROOT / "dist"
SKIP = {".DS_Store", "Thumbs.db", "desktop.ini"}
UUID_RE = re.compile(r"^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
# Fixed timestamp so rebuilding unchanged sources gives identical archives.
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def manifests(pack_dir):
    return sorted(
        p for p in (pack_dir / "manifest.json", *pack_dir.glob("*_pack/manifest.json"))
        if p.is_file()
    )


def validate():
    errors = []
    seen_uuids = {}
    header_uuids = set()
    all_manifests = []

    for path in sorted(PACKS.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {e}")

    for pack_dir in sorted(p for p in PACKS.iterdir() if p.is_dir()):
        found = manifests(pack_dir)
        if not found:
            errors.append(f"{pack_dir.relative_to(ROOT)}: no manifest.json found")
        all_manifests.extend(found)

    for path in all_manifests:
        rel = path.relative_to(ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError:
            continue  # already reported above
        header = data.get("header", {})
        header_uuids.add(header.get("uuid"))
        for uuid in [header.get("uuid")] + [m.get("uuid") for m in data.get("modules", [])]:
            if not uuid or not UUID_RE.match(uuid):
                errors.append(f"{rel}: bad or missing uuid {uuid!r}")
            elif uuid in seen_uuids:
                errors.append(f"{rel}: uuid {uuid} also used in {seen_uuids[uuid]}")
            else:
                seen_uuids[uuid] = rel
        for module in data.get("modules", []):
            entry = module.get("entry")
            if entry and not (path.parent / entry).is_file():
                errors.append(f"{rel}: script entry {entry} does not exist")

    # A pack-to-pack dependency must point at a pack in this repo, at its current version.
    versions = {}
    for path in all_manifests:
        try:
            header = json.loads(path.read_text(encoding="utf-8-sig")).get("header", {})
        except ValueError:
            continue
        versions[header.get("uuid")] = header.get("version")
    for path in all_manifests:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError:
            continue
        for dep in data.get("dependencies", []):
            uuid = dep.get("uuid")
            if not uuid:
                continue
            rel = path.relative_to(ROOT)
            if uuid not in header_uuids:
                errors.append(f"{rel}: depends on unknown pack uuid {uuid}")
            elif dep.get("version") != versions[uuid]:
                errors.append(
                    f"{rel}: depends on {uuid} version {dep.get('version')}, "
                    f"but that pack is at {versions[uuid]}"
                )
    return errors


def build(pack_dir):
    found = manifests(pack_dir)
    is_addon = not (pack_dir / "manifest.json").is_file()
    version = json.loads(found[0].read_text(encoding="utf-8-sig"))["header"]["version"]
    name = f"{pack_dir.name}-v{'.'.join(map(str, version))}"
    out = DIST / f"{name}.{'mcaddon' if is_addon else 'mcpack'}"
    DIST.mkdir(exist_ok=True)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(pack_dir.rglob("*")):
            if not path.is_file() or path.name in SKIP:
                continue
            info = zipfile.ZipInfo(path.relative_to(pack_dir).as_posix(), ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
            count += 1
    print(f"built {out.relative_to(ROOT)} ({count} files, {out.stat().st_size // 1024} KB)")


def main(argv):
    check_only = "--check" in argv
    names = [a for a in argv if not a.startswith("-")]

    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"\n{len(errors)} validation error(s)", file=sys.stderr)
        return 1
    print("validation ok")
    if check_only:
        return 0

    pack_dirs = [PACKS / n for n in names] or sorted(p for p in PACKS.iterdir() if p.is_dir())
    for pack_dir in pack_dirs:
        if not pack_dir.is_dir():
            print(f"no such pack: {pack_dir.name}", file=sys.stderr)
            return 1
        build(pack_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
