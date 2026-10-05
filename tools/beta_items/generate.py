#!/usr/bin/env python3
"""Generate the overrides of packs/beta-items-only from the vanilla pack files.

Usage:
    git clone --depth 1 https://github.com/Mojang/bedrock-samples
    python3 tools/beta_items/generate.py --samples path/to/bedrock-samples

Reads packs/beta-items-only/allowlist.json and the vanilla behavior pack, then
rewrites these parts of the pack from scratch:

    recipes/            disabled or Beta-rewritten vanilla recipes
    loot_tables/        vanilla tables with non-allowlisted entries removed,
                        plus Beta drops for the Beta mobs
    spawn_rules/        empty rules for every mob that is not a Beta mob
    scripts/allowlist.js  the allowlist as a module (scripts cannot read JSON)
    coverage.json       what was generated, for review and for the report

Everything Beta-specific that is not derivable from the allowlist lives in
rules.py next to this file. Re-run after a game update; the script stops with
an error when a rule no longer matches the vanilla files.
"""
import argparse
import copy
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "beta-items-only"
DISABLED_TAG = "deprecated"  # the tag vanilla itself uses for retired recipes
CRAFTING_STATIONS = {"crafting_table", "furnace"}


def load(path):
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except ValueError:
        # A few vanilla files carry comments or trailing commas.
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        text = re.sub(r'//[^\n"]*$', "", text, flags=re.M)
        text = re.sub(r",(\s*[}\]])", r"\1", text)
        return json.loads(text)


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Item names
# --------------------------------------------------------------------------

def candidates(name, data=None):
    """Modern identifiers a vanilla item reference can stand for.

    Vanilla files still use pre-flattening names with data values
    (minecraft:dye 15, minecraft:log:1). Returns a list because a legacy name
    without a data value means "any variant".
    """
    if isinstance(name, dict):
        if "tag" in name:
            return list(rules.ITEM_TAGS.get(name["tag"], []))
        name, data = name.get("item"), name.get("data", data)
    parts = name.split(":")
    if parts[-1].lstrip("-").isdigit() and len(parts) > 1:
        data = int(parts[-1])
        parts = parts[:-1]
    if len(parts) == 1:
        parts = ["minecraft", parts[0]]
    name = ":".join(parts)
    if not isinstance(data, int):
        data = None  # ranges and molang: variant unknown

    if name in rules.LEGACY_VARIANTS:
        variants = rules.LEGACY_VARIANTS[name]
        if data is None:
            return sorted(set(variants.values()))
        return [variants.get(data, f"{name}:{data}")]
    name = rules.LEGACY_NAMES.get(name, name)
    if name in rules.DATA_IS_VARIANT and data not in (None, 0):
        return [f"{name}:{data}"]
    return [name]


class Context:
    def __init__(self, samples):
        self.samples = samples
        self.vanilla = samples / "behavior_pack"
        self.allow = set(json.loads((PACK / "allowlist.json").read_text()))
        known = {
            i["name"]
            for i in load(samples / "metadata/vanilladata_modules/mojang-items.json")["data_items"]
        }
        unknown = sorted(self.allow - known)
        if unknown:
            sys.exit(f"allowlist.json has identifiers this game version does not know: {unknown}")
        self.version = load(samples / "version.json")["latest"]["version"]

    def allowed(self, name, data=None):
        return any(c in self.allow for c in candidates(name, data))



# --------------------------------------------------------------------------
# Recipes
# --------------------------------------------------------------------------

def recipe_parts(kind, body):
    """(ingredients, results) of a recipe body, as raw vanilla references."""
    if kind == "minecraft:recipe_shaped":
        ingredients = list(body["key"].values())
    elif kind == "minecraft:recipe_shapeless":
        ingredients = list(body["ingredients"])
    elif kind == "minecraft:recipe_furnace":
        return [body["input"]], [body["output"]]
    else:
        return None, None
    result = body["result"]
    return ingredients, result if isinstance(result, list) else [result]


def generate_recipes(ctx, coverage):
    out = PACK / "recipes"
    by_id = {}
    for path in sorted((ctx.vanilla / "recipes").glob("*.json")):
        data = load(path)
        kind = next(k for k in data if k != "format_version")
        body = data[kind]
        ident = body["description"]["identifier"]
        live = body.get("tags") != [DISABLED_TAG]
        # Vanilla sometimes keeps a retired twin under the same identifier;
        # the live one is the recipe players actually get.
        if ident not in by_id or (live and not by_id[ident][3]):
            by_id[ident] = (path, data, kind, live)

    shorts = {i.split(":", 1)[-1] for i in by_id}
    missing = sorted((set(rules.RECIPE_REWRITES) | set(rules.RECIPE_NOT_IN_BETA)) - shorts)
    if missing:
        sys.exit(f"rules.py names recipes that vanilla no longer has: {missing}")

    kept, rewritten, disabled = [], [], {}
    craftable = set()

    def result_ids(kind, body):
        return [c for r in recipe_parts(kind, body)[1] for c in candidates(r)]

    for ident, (path, data, kind, live) in sorted(by_id.items()):
        if not live:
            continue  # already uncraftable in vanilla
        body = data[kind]
        short = ident.split(":", 1)[-1]
        tags = set(body.get("tags", []))
        ingredients, results = recipe_parts(kind, body)

        reason = None
        if short in rules.RECIPE_REWRITES:
            new = copy.deepcopy(data)
            rules.RECIPE_REWRITES[short][1](new[kind])
            dump(out / path.name, new)
            rewritten.append({"recipe": short, "change": rules.RECIPE_REWRITES[short][0]})
            craftable.update(result_ids(kind, new[kind]))
            continue
        if ingredients is None:
            reason = "station does not exist in Beta"
        elif not tags & CRAFTING_STATIONS:
            reason = "station does not exist in Beta"
        elif not all(ctx.allowed(r) for r in results):
            reason = "output not on allowlist"
        elif not all(ctx.allowed(i) for i in ingredients):
            reason = "ingredient not on allowlist"
        elif kind == "minecraft:recipe_furnace":
            output = candidates(body["output"])[0]
            if not any((i, output) in rules.BETA_SMELTING for i in candidates(body["input"])):
                reason = "not a Beta smelting recipe"
        elif short in rules.RECIPE_NOT_IN_BETA:
            reason = "recipe did not exist in Beta: " + rules.RECIPE_NOT_IN_BETA[short]

        if reason is None:
            kept.append(short)
            craftable.update(result_ids(kind, body))
            continue
        new = copy.deepcopy(data)
        new[kind]["tags"] = [DISABLED_TAG]
        # Otherwise the recipe still unlocks and stays listed in the recipe
        # book. Vanilla's retired cobweb_to_string recipe does the same.
        if "unlock" in new[kind]:
            new[kind]["unlock"] = {"context": "None"}
        dump(out / path.name, new)
        disabled.setdefault(reason.split(":")[0], []).append(short)

    uncraftable = sorted(rules.BETA_CRAFTABLE - craftable - rules.BUILT_IN_RECIPES)
    if uncraftable:
        sys.exit(f"craftable in Beta but no recipe left for: {uncraftable}")
    listed_twice = sorted(rules.BUILT_IN_RECIPES & craftable)
    if listed_twice:
        sys.exit(f"rules.BUILT_IN_RECIPES lists items that now have recipe files: {listed_twice}")
    stray = sorted(rules.BETA_CRAFTABLE - ctx.allow)
    if stray:
        sys.exit(f"rules.BETA_CRAFTABLE lists items missing from allowlist.json: {stray}")

    coverage["recipes"] = {
        "vanilla_total": len(by_id),
        "kept_unchanged": sorted(kept),
        "rewritten": rewritten,
        "disabled_count": sum(len(v) for v in disabled.values()),
        "disabled_by_reason": {k: len(v) for k, v in sorted(disabled.items())},
        "disabled_not_in_beta": sorted(disabled.get("recipe did not exist in Beta", [])),
        "built_in_not_overridable": sorted(rules.BUILT_IN_RECIPES),
    }


# --------------------------------------------------------------------------
# Loot tables
# --------------------------------------------------------------------------

def bare(function_name):
    return function_name.split(":", 1)[-1]


def filter_entry(ctx, entry):
    """The entry to keep (possibly cleaned), or None to drop it."""
    kind = entry.get("type")
    if kind != "item":
        return entry  # nested tables are filtered in their own file
    functions = entry.get("functions", [])
    names = {bare(f.get("function", "")) for f in functions}
    if names & rules.LOOT_FUNCTIONS_POST_BETA:
        return None
    data = None
    for f in functions:
        if bare(f.get("function", "")) == "set_data":
            data = f.get("data")
        if bare(f.get("function", "")) in ("random_aux_value", "set_data_from_color_index"):
            data = "any"
    options = candidates(entry["name"], data if isinstance(data, int) else None)
    if data is not None and not isinstance(data, int):
        # Random variant: keep only when every variant is allowed (sheep wool).
        if not all(o in ctx.allow for o in options):
            return None
    elif not any(o in ctx.allow for o in options):
        return None
    if "pools" in entry:  # armor sets nest further pools inside an entry
        entry = {**entry, "pools": filter_pools(ctx, entry["pools"])}
        if not entry["pools"]:
            del entry["pools"]
    return entry


def strip_functions(node):
    """Remove enchanting functions wherever they sit in a table."""
    if isinstance(node, list):
        return [strip_functions(n) for n in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for key, value in node.items():
        if key == "functions" and isinstance(value, list):
            value = [f for f in value
                     if bare(f.get("function", "")) not in rules.LOOT_FUNCTIONS_STRIPPED]
            if not value:
                continue
        out[key] = strip_functions(value)
    return out


def filter_pools(ctx, pools):
    kept = []
    for pool in pools:
        if "entries" not in pool:
            kept.append(pool)
            continue
        entries = [e for e in (filter_entry(ctx, e) for e in pool["entries"]) if e]
        # A pool left with nothing, or only "empty" entries, is removed whole
        # rather than left behind as an empty pool.
        if any(e.get("type") != "empty" for e in entries):
            kept.append({**pool, "entries": entries})
    return kept


def filter_table(ctx, table):
    pools = filter_pools(ctx, table.get("pools", []))
    return strip_functions({**table, "pools": pools}) if pools else {}


def generate_loot(ctx, coverage):
    out = PACK / "loot_tables"
    source = ctx.vanilla / "loot_tables"
    changed, emptied = [], []
    seen = set()
    for path in sorted(source.rglob("*.json")):
        rel = path.relative_to(source).as_posix()
        seen.add(rel)
        table = load(path)
        if rel in rules.LOOT_OVERRIDES:
            new = rules.LOOT_OVERRIDES[rel]
        else:
            new = filter_table(ctx, table)
        if new != table:
            dump(out / rel, new)
            changed.append(rel)
            if not new:
                emptied.append(rel)
    missing = sorted(set(rules.LOOT_OVERRIDES) - seen)
    if missing:
        sys.exit(f"rules.LOOT_OVERRIDES names tables vanilla no longer has: {missing}")
    coverage["loot_tables"] = {
        "vanilla_total": len(seen),
        "overridden": len(changed),
        "beta_mob_tables": sorted(k for k in rules.LOOT_OVERRIDES if k.startswith("entities/")),
        "emptied": emptied,
    }


# --------------------------------------------------------------------------
# Spawn rules
# --------------------------------------------------------------------------

def generate_spawn_rules(ctx, coverage):
    out = PACK / "spawn_rules"
    disabled, adjusted, untouched = [], [], []
    for path in sorted((ctx.vanilla / "spawn_rules").glob("*.json")):
        data = load(path)
        rule = data["minecraft:spawn_rules"]
        ident = rule["description"]["identifier"]
        if ident not in rules.BETA_MOBS:
            dump(out / path.name, {
                "format_version": data["format_version"],
                "minecraft:spawn_rules": {"description": rule["description"], "conditions": []},
            })
            disabled.append(ident)
            continue
        # Beta mobs keep their rules, minus any chance to spawn as another mob.
        new = copy.deepcopy(data)
        for condition in new["minecraft:spawn_rules"].get("conditions", []):
            permute = condition.get("minecraft:permute_type")
            if not permute:
                continue
            keep = [
                p for p in permute
                if p.get("entity_type", ident).split("<")[0] in rules.BETA_MOBS
            ]
            if all("entity_type" not in p for p in keep):
                del condition["minecraft:permute_type"]
            else:
                condition["minecraft:permute_type"] = keep
        if new != data:
            dump(out / path.name, new)
            adjusted.append(ident)
        else:
            untouched.append(ident)
    no_rule = sorted(rules.BETA_MOBS - set(adjusted) - set(untouched))
    if no_rule:
        sys.exit(f"Beta mobs without a vanilla spawn rule: {no_rule}")

    entities = {
        e["name"] if e["name"].startswith("minecraft:") else "minecraft:" + e["name"]
        for e in load(ctx.samples / "metadata/vanilladata_modules/mojang-entities.json")["data_items"]
    }
    coverage["spawn_rules"] = {
        "disabled": sorted(disabled),
        "beta_mobs_adjusted": sorted(adjusted),
        "beta_mobs_untouched": sorted(untouched),
        "entities_without_spawn_rule": sorted(
            e for e in entities if e not in rules.BETA_MOBS and e not in disabled
        ),
    }


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--samples", required=True, type=Path,
                        help="checkout of https://github.com/Mojang/bedrock-samples")
    args = parser.parse_args()
    if not (args.samples / "behavior_pack" / "recipes").is_dir():
        sys.exit(f"{args.samples} does not look like a bedrock-samples checkout")

    ctx = Context(args.samples)
    for name in ("recipes", "loot_tables", "spawn_rules"):
        shutil.rmtree(PACK / name, ignore_errors=True)

    coverage = {"generated_from": f"bedrock-samples {ctx.version}", "allowlist_size": len(ctx.allow)}
    generate_recipes(ctx, coverage)
    generate_loot(ctx, coverage)
    generate_spawn_rules(ctx, coverage)
    dump(PACK / "coverage.json", coverage)

    module = (
        "// Generated from allowlist.json by tools/beta_items/generate.py. Do not edit.\n"
        "export const ALLOWLIST = " + json.dumps(sorted(ctx.allow), indent=2) + ";\n"
    )
    (PACK / "scripts").mkdir(exist_ok=True)
    (PACK / "scripts" / "allowlist.js").write_text(module, encoding="utf-8")

    r, l, s = coverage["recipes"], coverage["loot_tables"], coverage["spawn_rules"]
    print(f"vanilla {ctx.version}, {len(ctx.allow)} allowlisted items")
    print(f"recipes: {len(r['kept_unchanged'])} kept, {len(r['rewritten'])} rewritten, "
          f"{r['disabled_count']} disabled {r['disabled_by_reason']}")
    print(f"loot tables: {l['overridden']} of {l['vanilla_total']} overridden")
    print(f"spawn rules: {len(s['disabled'])} disabled, {len(s['beta_mobs_adjusted'])} adjusted")


if __name__ == "__main__":
    main()
