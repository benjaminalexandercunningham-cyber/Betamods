BETA INVENTORY ENFORCER 1.1

Import into Minecraft Bedrock 1.21.90 or newer, then activate under World Settings > Behavior Packs. Uses the stable Script API; no Beta APIs experiment needed. Works independently of the texture pack; keep both active for visuals plus enforcement.

Deletes entire stacks outside the original chart whitelist from every player every tick (normally about 0.05 seconds). Includes hotbar, inventory, armor, mainhand, offhand and UI cursor. Also cleans on spawn and cancels forbidden item-use events. Works in Survival and Creative, with no operator exemption. Newly introduced/custom items are blocked by default. Item counts, names, durability and enchantments of allowed stacks are preserved.

Red beds are retained by data-aware clear commands; other colors are removed when they enter the player inventory/equipment. Bed held solely on the UI cursor shares the red bed identifier and cannot be color-checked through this API; it is checked when deposited into inventory. Original fish use cod/cooked_cod, and roses use poppy. Removed/unobtainable historical blocks are not recreated.

Deletes existing forbidden possessions as soon as the pack runs. Does not delete already placed blocks, items inside chests/ender chests, or dropped ground items; taking them into your inventory triggers cleanup. This is tick-based enforcement, not a guarantee against all actions during the fraction of a tick before cleanup.

Validation: simulated inventory/equipment/cursor cleanup, allow/deny regression cases, use cancellation, spawn callback, and archive/JSON/syntax checks. No live Bedrock client was available for testing.

Version 1.1: removed oak slabs and petrified oak slabs from the allowlist. Other wooden slabs were already forbidden. All other item rules and cleanup logic are unchanged.
