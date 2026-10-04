CLASSIC ORE DROPS & OAK PLANKS 1.0

Import the .mcpack in Bedrock 1.21.90+ and activate under World Settings > Behavior Packs. Put it above other packs that change the same recipes. No resource pack or Beta APIs experiment is needed. Compatible with the earlier texture, inventory and entity filters.

Iron ore drops one iron ore block when player-mined with a stone-tier or better pickaxe (golden/wooden pickaxes are insufficient). Gold ore drops one gold ore block with an iron-tier or better pickaxe. Creative and incorrect tools retain native behavior. Fortune does not multiply ore blocks; Silk Touch also gives the ore block. Survival tool durability and Unbreaking are applied. Normal furnace smelting recipes remain intact.

All vanilla recipes that produce planks now produce oak planks, including spruce, birch, other logs, wood, stripped variants, stems/hyphae and bamboo blocks. Recipe identifiers, inputs and output counts are preserved: ordinary logs still produce four planks, bamboo keeps its original yield. Modern inputs blocked by the earlier inventory enforcer remain blocked; allowed spruce/birch logs work normally.

Ore handling covers player mining of ordinary iron_ore/gold_ore. Deepslate ores, Nether gold ore, explosions and command destruction are outside this change. The script replaces the final mining break to avoid raw-metal drops; native break particles/statistic callbacks for these two ores may differ.

Validated recipes and simulated ore breaks, tool tiers, one-block drops, durability, Creative, duplicate events and unrelated blocks. Not tested inside a running Bedrock client.
