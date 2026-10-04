PERMAFROST SNOW & ICE v2.0

Disable BOTH old restoration packs and the random-ticks-off pack. Import the .mcaddon, activate its behavior and resource packs, and put its RP above other resource packs. It never changes randomTickSpeed. If the old freeze pack left your gamerule at zero, run /gamerule randomtickspeed 1 once.

This replaces detected native snow layers and normal ice with visually similar custom blocks that HAVE NO MELTING BEHAVIOR. Once converted, high randomTickSpeed cannot melt them; there is no restore-after-melt loop. Player mining removes them permanently. Placed native snow/ice is converted in the placement callback. Existing blocks near players are progressively converted using the scanner. An undiscovered native block can still melt before conversion.

The scanner covers a 33x33 surface area, three blocks above/twelve below the reported heightmap, plus twenty-one blocks around player height. Existing already-melted blocks cannot be recovered. Snow thickness 1-8 is preserved. Snow stacking is supported. Textures are copied from vanilla into independent custom aliases, so the earlier texture filter cannot blank them. Loot refers to native items so the inventory enforcer accepts it.

CUSTOM-BLOCK TRADEOFFS: Some vanilla-only interactions differ. Native grass may not automatically acquire its snowy side when covered by custom snow. Snow shovel/tool speed and item drops, light behavior, ice translucency and piston interactions may differ from native blocks. This is a different block identifier, not a patch to vanilla melt code.

REMOVAL: Keep the add-on installed while converted blocks exist. To revert loaded/scanned blocks, run /scriptevent classic_permafrost:revert, visit every converted area and wait for the scans, then exit and disable the add-on before reloading. This mode lasts for the current session only. Unvisited/deep converted blocks may need manual /fill replacement. Removing the add-on without reversion leaves custom-block references in the world.

JSON, geometry/state coverage, mining separation and simulated high-tick conversion checks passed. No running Bedrock client was available for visual or engine testing.
