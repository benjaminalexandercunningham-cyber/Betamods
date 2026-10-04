# Betamods

Minecraft Bedrock packs that approximate selected Beta 1.7.3 rules in the modern game. They do not recreate the full historical game.

Target: **Bedrock 1.21.90 or newer**, stable Script API (`@minecraft/server` 2.0.0). No Beta APIs experiment is required.

## Packs

| Directory | Type | Version | What it does |
| --- | --- | --- | --- |
| [packs/block-item-filter](packs/block-item-filter) | Resource pack | 1.2.0 | Blanks textures of post-Beta blocks and items; keeps snowy grass. |
| [packs/beta-items-only](packs/beta-items-only) | Behavior pack | 1.0.0 | Makes only Beta 1.7.3 items obtainable: deletes other items, disables their recipes, cleans loot and mob spawns. Replaces the next two packs. Needs Bedrock 1.26.50+. |
| [packs/inventory-enforcer](packs/inventory-enforcer) | Behavior pack | 1.1.0 | Deletes items outside the Beta allowlist from players every tick. |
| [packs/entity-enforcer](packs/entity-enforcer) | Add-on (BP + RP) | 1.1.0 | Removes post-Beta entities, baby mobs and XP orbs without drops or death effects. |
| [packs/classic-ores-planks](packs/classic-ores-planks) | Behavior pack | 1.0.0 | Iron and gold ore drop ore blocks; all plank recipes produce oak planks. |
| [packs/permafrost](packs/permafrost) | Add-on (BP + RP), optional | 2.0.0 | Converts snow layers and ice into custom blocks that never melt. |

Each pack has a `README.txt` with its exact rules and known limits. That file ships inside the built pack.

## Build

Requires Python 3.8+ (standard library only).

```bash
python3 tools/build.py
```

This validates every pack, then writes `.mcpack` / `.mcaddon` files to `dist/`. Other forms:

```bash
python3 tools/build.py --check
```

```bash
python3 tools/build.py permafrost
```

`--check` validates without building: all JSON parses, every manifest UUID is well formed and unique, script entry points exist, and BP-to-RP dependencies match the current RP version.

Built archives are not committed. They are published through GitHub Releases (below); CI also attaches them to every run as the `packs` artifact.

## Releases

Every tagged release on the [Releases page](https://github.com/benjaminalexandercunningham-cyber/Betamods/releases) carries these files:

| File | Use it for |
| --- | --- |
| `betamods-<tag>-all.mcaddon` | Updating the Realm. Open it on the device (iPad, phone, PC) to import every pack at once. See [docs/REALM_SETUP.md](docs/REALM_SETUP.md). |
| `<pack>-v<version>.mcpack` / `.mcaddon` | Importing a single pack. |
| `SHA256SUMS.txt` | Checksums of the files above. |

The download links work in any browser, so the Realm can be updated from an iPad with no computer involved.

### Cutting a release

Release tags look like `v1.0.0` and version the whole collection; individual packs keep their own versions in their manifests.

From the GitHub website or mobile app: **Releases → Draft a new release**, type a new tag such as `v1.0.0` targeting `main`, and publish. The Release workflow builds the files and attaches them a minute or so later.

From a terminal:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

To preview the release files locally:

```bash
python3 tools/build.py --release v1.0.0
```

## Install

1. Back up your world, then import the files from a release (or from `dist/`) into Minecraft. For the Realm, follow [docs/REALM_SETUP.md](docs/REALM_SETUP.md). Import permafrost only if you want its custom-block behavior.
2. Enable the inventory enforcer, entity enforcer and classic ores/planks behavior packs in world settings.
3. Enable the block/item filter and entity enforcer resource packs. Put the entity enforcer resource pack **above** the filter.
4. If using permafrost, enable both of its packs and put its resource pack above the filter too.
5. Disable older versions of each pack. Put the ores/planks behavior pack above other packs that override its recipes.

### Removing permafrost

Keep permafrost installed while converted blocks exist. To revert, run `/scriptevent classic_permafrost:revert`, visit the converted areas so they get scanned, then exit and disable the add-on before reloading. See [its README](packs/permafrost/README.txt) first.

## Working on the packs

- Edit files under `packs/` directly. Directory names carry no version; the version lives in each `manifest.json`.
- **When you change a pack, bump its version** in `manifest.json` (header and every module). For the two add-ons, also bump the RP version and the matching dependency entry in the BP manifest; `--check` fails if they drift.
- **Never change a UUID** of an existing pack. Minecraft treats a new UUID as a different pack and worlds lose their link to it.
- Work on a branch and open a pull request; CI validates and builds on every PR.
- Note the change in the pack's `README.txt` and in [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md).

### Regenerating the Beta Items Only overrides

Most of `packs/beta-items-only` is generated from Mojang's vanilla pack files. After a game update, or after editing `allowlist.json` or [tools/beta_items/rules.py](tools/beta_items/rules.py):

```bash
git clone --depth 1 https://github.com/Mojang/bedrock-samples ../bedrock-samples
```

```bash
python3 tools/beta_items/generate.py --samples ../bedrock-samples
```

The generator stops with an error if a rule no longer matches the vanilla files, or if an item that was craftable in Beta would be left without a recipe. Background and open issues are in [docs/BETA_ITEMS_ONLY_REPORT.md](docs/BETA_ITEMS_ONLY_REPORT.md).

Fast iteration: instead of re-importing an archive each time, copy or symlink a pack folder into Minecraft's `development_behavior_packs` / `development_resource_packs` folder and reload the world.

## Testing status

Packs have passed structural checks and simulated behavior tests only. **None of them has been tested in a live Bedrock client yet**, and the combination of all packs together is unverified. In-game results are the most valuable thing to report in issues.

## Known limits

- **Block/item filter:** this removes textures; it does not guarantee invisibility. Opaque vanilla materials can render blanked blocks as solid black. Collision, lighting, names and inventory entries are unchanged.
- **Beta items only:** recipes built into the game cannot be overridden, mobs from structures and spawners still appear, and items inside containers are untouched until picked up. See the report.
- **Inventory enforcer:** does not touch placed blocks, container contents or dropped items. Non-red beds held only on the cursor are not detected until they land in the inventory.
- **Entity enforcer:** removes entity types and babies; it does not restore Beta AI, spawn rates or models. Unknown future entities are removed by script but have no texture or spawn override.
- **Classic ores/planks:** covers player mining of normal iron and gold ore only. Deepslate ore, Nether gold ore, explosions and commands are unchanged.
- **Permafrost:** native snow and ice can still melt before the scanner reaches them. Custom blocks differ from vanilla in snowy-grass detection, mining speed, lighting, translucency and piston behavior.

## Assets and license

Minecraft assets in the resource packs originate from Mojang's Bedrock samples. No new license is granted for them. This project is not affiliated with Mojang or Microsoft.
