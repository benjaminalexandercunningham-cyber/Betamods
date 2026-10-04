# Betamods

Minecraft Bedrock packs that approximate selected Beta 1.7.3 rules in the modern game. They do not recreate the full historical game.

Target: **Bedrock 1.21.90 or newer**, stable Script API (`@minecraft/server` 2.0.0). No Beta APIs experiment is required.

## Packs

| Directory | Type | Version | What it does |
| --- | --- | --- | --- |
| [packs/block-item-filter](packs/block-item-filter) | Resource pack | 1.2.0 | Blanks textures of post-Beta blocks and items; keeps snowy grass. |
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

Built archives are not committed. Publish them through GitHub Releases; CI also attaches them to every run as the `packs` artifact.

## Install

1. Back up your world, then import the built files from `dist/` into Minecraft. Import permafrost only if you want its custom-block behavior.
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

Fast iteration: instead of re-importing an archive each time, copy or symlink a pack folder into Minecraft's `development_behavior_packs` / `development_resource_packs` folder and reload the world.

## Testing status

Packs have passed structural checks and simulated behavior tests only. **None of them has been tested in a live Bedrock client yet**, and the combination of all packs together is unverified. In-game results are the most valuable thing to report in issues.

## Known limits

- **Block/item filter:** this removes textures; it does not guarantee invisibility. Opaque vanilla materials can render blanked blocks as solid black. Collision, lighting, names and inventory entries are unchanged.
- **Inventory enforcer:** does not touch placed blocks, container contents or dropped items. Non-red beds held only on the cursor are not detected until they land in the inventory.
- **Entity enforcer:** removes entity types and babies; it does not restore Beta AI, spawn rates or models. Unknown future entities are removed by script but have no texture or spawn override.
- **Classic ores/planks:** covers player mining of normal iron and gold ore only. Deepslate ore, Nether gold ore, explosions and commands are unchanged.
- **Permafrost:** native snow and ice can still melt before the scanner reaches them. Custom blocks differ from vanilla in snowy-grass detection, mining speed, lighting, translucency and piston behavior.

## Assets and license

Minecraft assets in the resource packs originate from Mojang's Bedrock samples. No new license is granted for them. This project is not affiliated with Mojang or Microsoft.
