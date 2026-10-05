# Beta 1.7.3 Items Only — report

Pack: [packs/beta-items-only](../packs/beta-items-only), version 1.0.1.
Generators: [tools/beta_items/generate.py](../tools/beta_items/generate.py) and [tools/beta_items/rules.py](../tools/beta_items/rules.py).

## Status

**Nothing here has been run in a Bedrock client.** None of the six acceptance checks has been performed; they all need a running game. What was checked:

- Every generated file is valid JSON and the pack passes `tools/build.py --check`.
- An independent pass over the effective recipe set (vanilla plus overrides) found 137 craftable recipes, none with an output or ingredient outside the allowlist.
- An independent pass over all 309 effective loot tables found no entry outside the allowlist, no enchanting function and no empty pool.
- The script was run against a mocked Script API: item removal, the raw-metal swap, and the inventory, armor, offhand and cursor sweep behaved as intended.
- Every Script API member the script uses exists in the `@minecraft/server` 2.10.0 metadata.

The method used to disable recipes (below) is the first thing to confirm in game.

## Target

| | |
| --- | --- |
| Game version | Bedrock 1.26.50 (bedrock-samples 1.26.50.4, dated 15 Sep 2026) |
| `min_engine_version` | 1.26.50 |
| Manifest `format_version` | 2 |
| Script module | `@minecraft/server` 2.10.0, the highest non-beta version in the 1.26.50 metadata |
| Experiments | none |

## Allowlist

[allowlist.json](../packs/beta-items-only/allowlist.json) holds 220 identifiers, all present in the 1.26.50 item list. Scripts cannot read JSON files, so the generator copies the list into `scripts/allowlist.js`; `allowlist.json` stays the only file to edit.

Decisions where the Beta item has no single modern equivalent:

| Beta item | Chosen | Why / what is excluded |
| --- | --- | --- |
| Ink sac, bone meal, lapis lazuli, cocoa beans (as dyes) | `ink_sac`, `bone_meal`, `lapis_lazuli`, `cocoa_beans` | The raw material is the Beta item. `black_dye`, `white_dye`, `blue_dye`, `brown_dye` are excluded. |
| Rose | `poppy` | |
| Tall grass | `short_grass`, `fern` | Beta's third "shrub" variant has no equivalent. |
| Wooden slab | `oak_slab` | Closest craftable item. `petrified_oak_slab` behaves like Beta's but cannot be crafted. The older Inventory Enforcer pack deliberately blocked oak slabs; this pack allows them. |
| Stone slab | `smooth_stone_slab` | Same look as the Beta stone slab. |
| Cobblestone stairs | `stone_stairs` | That is the Bedrock identifier. |
| Raw / cooked fish | `cod`, `cooked_cod` | Salmon, tropical fish and pufferfish excluded. |
| Pumpkin | `pumpkin` and `carved_pumpkin` | Beta pumpkins had a face; modern ones generate uncarved. |
| Map | `empty_map` and `filled_map` | |
| Bed | `bed` | All 16 colours share this identifier; the script cannot tell them apart. |
| Coal | `coal` and `charcoal` | Separate identifiers now. |
| Planks, sign, door, trapdoor, fence, boat | the oak variants only | |
| Blocks that existed but were never held | `bedrock`, `mob_spawner`, `farmland`, `web`, `sponge`, `grass_block`, `short_grass`, `fern`, `deadbush`, `ice`, `snow_layer` are allowed | They were Beta blocks. Water, lava, fire and portal are not listed. |
| Chainmail armor | allowed | Existed as items, never craftable. |
| Locked chest, furnace minecart | not listed | No Bedrock equivalent. |

## Script

[scripts/main.js](../packs/beta-items-only/scripts/main.js) loads the allowlist into a `Set` once, removes item entities that are not on it when they spawn or load, and every 20 ticks clears non-allowlisted stacks from each player's inventory, armor, offhand and cursor. When a player interacts with a block that has an inventory (chest, furnace, hopper and so on), that inventory is cleared the same way before the screen opens.

One addition beyond the brief: dropped `raw_iron` and `raw_gold` are swapped for `iron_ore` and `gold_ore`. Beta ores dropped the ore block; without the swap, iron and gold cannot be obtained at all.

## Recipes

Disabling method: the override keeps the vanilla recipe body and identifier and sets `"tags": ["deprecated"]`. This is how Mojang's own files retire recipes. Since 1.0.1 a disabled recipe's `unlock` condition is also replaced with `{"context": "None"}`, as in vanilla's retired `cobweb_to_string`, so that it stops unlocking; 1.0.0 kept the vanilla unlock condition and disabled recipes such as iron nuggets and cherry boats were reported as still listed in the recipe book. **Whether 1.0.1 removes them has not been confirmed in game.** Recipes a player unlocked earlier are stored with the player; `/recipe take @a *` clears them.

Of 1,851 live vanilla recipes (Mojang's files retire a further 30 themselves):

| Result | Count |
| --- | --- |
| Left as vanilla | 124 |
| Rewritten to match Beta | 13 |
| Disabled: output not on the allowlist | 1,138 |
| Disabled: station did not exist (stonecutter, brewing stand, smithing table, cartography table, campfire-only) | 441 |
| Disabled: an ingredient is not on the allowlist | 125 |
| Disabled: all items are Beta items but the recipe is not | 10 |

Rewritten:

| Recipe | Change |
| --- | --- |
| Golden apple | 8 gold blocks instead of 8 gold ingots |
| Fence | 6 sticks give 2, instead of 4 planks + 2 sticks giving 3 |
| Sign | yields 1 instead of 3 |
| Ladder | yields 2 instead of 3 |
| Wooden door, iron door | yield 1 instead of 3 |
| Book | 3 paper, no leather |
| Stone button | 2 stone in a column instead of 1 |
| Oak slab | yields 3 instead of 6 |
| Rose red, dandelion yellow | yield 2 instead of 1 |
| Planks from spruce and birch logs | give oak planks |

Disabled although every item is a Beta item: the modern fence recipe, map without a compass, the two map-upgrade recipes, cobweb to string, saddle, snow layer, and smelting coal, redstone and lapis ore.

Two of these rest on memory rather than on wiki text I could retrieve, and are worth a second look: the fence **yield** of 2 (the wiki confirms the 6-stick recipe but not the count), and the Beta furnace list (iron, gold and diamond ore, sand, cobblestone, clay, porkchop, fish, cactus, logs). The other yields were confirmed from the wiki's history sections.

## Loot tables

260 of 309 vanilla tables are overridden at the same paths. Entries for items outside the allowlist are removed; pools left with nothing are removed whole, and tables left with no pools become `{}`, the same content as vanilla's own `empty.json`. Treasure maps, potions and enchanted books are removed, and enchanting functions are stripped from the items that stay.

Beta mob drops:

| Mob | Drops |
| --- | --- |
| Pig | 0–2 porkchop (cooked if burning) |
| Cow | 0–2 leather |
| Sheep | 1 wool of its colour |
| Chicken | 0–2 feathers |
| Squid | 1–3 ink sacs |
| Zombie | 0–2 feathers |
| Skeleton | 0–2 arrows, 0–2 bones |
| Spider | 0–2 string |
| Creeper | 0–2 gunpowder; disc 13 or cat when killed by a skeleton |
| Slime | 0–2 slimeballs |
| Ghast | 0–2 gunpowder |
| Zombified piglin | 0–2 cooked porkchop |
| Wolf | nothing |

Fishing gives raw cod only.

## Spawn rules

47 of the 60 vanilla spawn rules are replaced with empty rules. The 13 Beta mobs keep theirs; the zombie rule loses its chance to spawn a zombie villager instead.

Mobs that can still appear, because they do not come from spawn rules (not solved, as agreed):

- **Spawners:** cave spiders (mineshafts), blazes (fortresses), magma cubes (bastions), silverfish (strongholds), and everything from trial spawners.
- **Placed with structures:** villagers, iron golems and cats in villages; pillagers, vindicators, evokers and allays in outposts and mansions; witches in swamp huts; guardians and elder guardians in monuments; shulkers in End cities; piglins, piglin brutes and hoglins in bastions; zombie villagers in igloos and abandoned villages.
- **Game events:** wandering traders and their llamas, raids (ravagers, vexes), skeleton horse traps, wardens, creakings, the ender dragon.
- **Conversions and riders:** drowned from zombies under water, zombie villagers from killed villagers, zombified piglins from pigs struck by lightning, chicken and spider jockeys, baby animals from breeding, baby zombies.
- **Player-built:** snow golems and iron golems, since pumpkins, snow and iron blocks are Beta items.

The Beta Entity Enforcer pack removes these at runtime and can be used alongside this pack.

## Could not be done

- **In-game testing**, including confirming the recipe book. No Bedrock client is available here.
- **Recipes built into the game.** Some recipes are not shipped as files and so cannot be overridden: classic stone, cobblestone and sandstone slabs (still yield 6), oak trapdoor, wooden pressure plate, wool dyeing, and beds (craftable in all 16 colours). Any built-in recipe that turns Beta items into a post-Beta item, such as a wooden button, will still show in the recipe book; the crafted item is deleted within a second. The full list of built-in recipes can only be read from the game.
- **Book** stays a shapeless recipe; Beta required a vertical column.
- **Items that share an identifier** with a Beta item pass the allowlist: coloured beds, tipped arrows, enchanted versions of Beta tools.
- **Containers and placed blocks.** Items inside a chest, furnace or other storage block stay there until a player opens it; hoppers can still move them meanwhile. Blocks already placed are untouched.
- **The one-second window.** A forbidden item can be held, and in principle used, for up to a second.
- **Raw-metal swap side effects.** Deepslate iron and gold ore also end up dropping the normal ore block, and Fortune would multiply it.
- **Other post-Beta blocks drop nothing**, including deepslate, so mining below Y=0 yields only ores.
- **Mob equipment.** Zombies can still spawn holding and dropping iron swords or shovels and Beta-material armor.
- **Villager trades** are not edited; traded items outside the allowlist are deleted by the sweep.
- **Creative players** are swept like everyone else.

## In-game checklist

1. Content log: load a world with the pack and confirm no errors.
2. Recipe book: confirm no post-Beta items; note any that appear (they are built-in recipes).
3. Break diorite: nothing drops. Break iron ore with a stone pickaxe: an iron ore block drops.
4. `/give @s minecraft:netherite_ingot`: gone within about a second.
5. Craft a golden apple (gold blocks), fence (sticks), sign, door, ladder, stone button and book the Beta way.
6. Spend a night in the overworld and watch for non-Beta mobs away from structures.
