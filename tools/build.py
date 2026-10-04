#!/usr/bin/env python3
"""Validate the packs in packs/ and build installable archives into dist/.

Usage:
    python3 tools/build.py            # validate, then build every pack
    python3 tools/build.py --check    # validate only (what CI runs)
    python3 tools/build.py permafrost # build a single pack by directory name
    python3 tools/build.py --release v1.0.0   # also build the release bundles

A pack directory containing manifest.json is built as a .mcpack. A directory
containing behavior_pack/ and/or resource_pack/ is built as a .mcaddon.
Output names come from the directory name and the manifest version.

--release additionally writes, named after the given tag:
    betamods-<tag>-all.mcaddon  every pack in one file, for one-tap import
    betamods-<tag>-server.zip   unpacked packs plus world_*_packs.json for a
                                Bedrock Dedicated Server or hosting panel
    SHA256SUMS.txt              checksums of everything in dist/
"""
import hashlib
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

# Load order written to the server bundle's world_*_packs.json, highest
# priority first. The entity enforcer and permafrost resource packs must sit
# above the block/item filter, and the ores/planks recipes above other packs.
BEHAVIOR_ORDER = ["classic-ores-planks", "inventory-enforcer", "entity-enforcer", "permafrost"]
RESOURCE_ORDER = ["entity-enforcer", "permafrost", "block-item-filter"]
# Shipped in the bundles but left out of the default world_*_packs.json.
OPTIONAL = {"permafrost"}


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


def write_zip(out, entries):
    """entries: iterable of (archive name, Path or bytes)."""
    DIST.mkdir(exist_ok=True)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for name, src in entries:
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src if isinstance(src, bytes) else src.read_bytes())
            count += 1
    print(f"built {out.relative_to(ROOT)} ({count} files, {out.stat().st_size // 1024} KB)")


def files(src_dir, prefix=""):
    for path in sorted(src_dir.rglob("*")):
        if path.is_file() and path.name not in SKIP:
            yield prefix + path.relative_to(src_dir).as_posix(), path


def build(pack_dir):
    found = manifests(pack_dir)
    is_addon = not (pack_dir / "manifest.json").is_file()
    version = json.loads(found[0].read_text(encoding="utf-8-sig"))["header"]["version"]
    name = f"{pack_dir.name}-v{'.'.join(map(str, version))}"
    write_zip(DIST / f"{name}.{'mcaddon' if is_addon else 'mcpack'}", files(pack_dir))


def units():
    """Every individual pack as (pack name, 'behavior' or 'resource', dir, header)."""
    for pack_dir in sorted(p for p in PACKS.iterdir() if p.is_dir()):
        for manifest in manifests(pack_dir):
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            types = {m.get("type") for m in data.get("modules", [])}
            kind = "resource" if "resources" in types else "behavior"
            yield pack_dir.name, kind, manifest.parent, data["header"]


def build_release(tag):
    all_units = list(units())
    unordered = [
        f"{name} ({kind})" for name, kind, _, _ in all_units
        if name not in (BEHAVIOR_ORDER if kind == "behavior" else RESOURCE_ORDER)
    ]
    if unordered:
        sys.exit(f"add to BEHAVIOR_ORDER/RESOURCE_ORDER in tools/build.py: {', '.join(unordered)}")

    # One file holding every pack; Minecraft imports each top-level folder as a pack.
    entries = []
    for name, kind, src, _ in all_units:
        entries.extend(files(src, f"betamods-{name}-{'bp' if kind == 'behavior' else 'rp'}/"))
    write_zip(DIST / f"betamods-{tag}-all.mcaddon", entries)

    # Server layout: drop-in behavior_packs/ and resource_packs/ folders plus
    # the world_*_packs.json files that switch the packs on for a world.
    entries = [("SERVER_SETUP.txt", (ROOT / "tools" / "SERVER_SETUP.txt").read_bytes())]
    for kind, order in (("behavior", BEHAVIOR_ORDER), ("resource", RESOURCE_ORDER)):
        by_name = {n: (src, header) for n, k, src, header in all_units if k == kind}
        enabled = []
        for name in order:
            src, header = by_name[name]
            entries.extend(files(src, f"{kind}_packs/betamods-{name}/"))
            enabled.append((name, {"pack_id": header["uuid"], "version": header["version"]}))
        for filename, include_optional in (
            (f"world_{kind}_packs.json", False),
            (f"with-permafrost/world_{kind}_packs.json", True),
        ):
            packs = [e for n, e in enabled if include_optional or n not in OPTIONAL]
            entries.append((filename, (json.dumps(packs, indent=2) + "\n").encode()))
    write_zip(DIST / f"betamods-{tag}-server.zip", entries)

    sums = DIST / "SHA256SUMS.txt"
    lines = [
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}"
        for p in sorted(DIST.iterdir()) if p.is_file() and p != sums
    ]
    sums.write_text("\n".join(lines) + "\n")
    print(f"wrote {sums.relative_to(ROOT)}")


def main(argv):
    check_only = "--check" in argv
    tag = None
    if "--release" in argv:
        i = argv.index("--release")
        if i + 1 >= len(argv) or not re.match(r"^v\d+\.\d+\.\d+[\w.-]*$", argv[i + 1]):
            print("--release needs a tag like v1.0.0", file=sys.stderr)
            return 1
        tag = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    names = [a for a in argv if not a.startswith("-")]

    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"\n{len(errors)} validation error(s)", file=sys.stderr)
        return 1
    print("validation ok")
    if check_only:
        return 0

    if tag and names:
        print("--release builds every pack; do not name packs with it", file=sys.stderr)
        return 1
    if tag and DIST.is_dir():
        for old in DIST.iterdir():  # stale files would end up in SHA256SUMS.txt
            if old.is_file():
                old.unlink()
    pack_dirs = [PACKS / n for n in names] or sorted(p for p in PACKS.iterdir() if p.is_dir())
    for pack_dir in pack_dirs:
        if not pack_dir.is_dir():
            print(f"no such pack: {pack_dir.name}", file=sys.stderr)
            return 1
        build(pack_dir)
    if tag:
        build_release(tag)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
