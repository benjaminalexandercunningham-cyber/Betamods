import { world, system, ItemStack, GameMode } from "@minecraft/server";
const ORES = new Set(["minecraft:iron_ore", "minecraft:gold_ore"]);
const IRON_TOOLS = new Set(["minecraft:stone_pickaxe", "minecraft:copper_pickaxe", "minecraft:iron_pickaxe", "minecraft:diamond_pickaxe", "minecraft:netherite_pickaxe"]);
const GOLD_TOOLS = new Set(["minecraft:iron_pickaxe", "minecraft:diamond_pickaxe", "minecraft:netherite_pickaxe"]);
const pending = new Set();
world.beforeEvents.playerBreakBlock.subscribe(event => {
  const ore = event.block.typeId;
  if (!ORES.has(ore) || event.cancel) return;
  const player = event.player;
  const creative = player.getGameMode() === GameMode.Creative;
  if (creative) return; // Let native creative mining happen without drops.
  const tool = event.itemStack;
  const canDrop = (ore === "minecraft:iron_ore" ? IRON_TOOLS : GOLD_TOOLS).has(tool?.typeId);
  // Wrong tools retain the normal break behavior and drop nothing.
  if (!canDrop) return;
  const dimension = event.block.dimension;
  const location = { ...event.block.location };
  const key = `${dimension.id}:${location.x},${location.y},${location.z}`;
  event.cancel = true;
  if (pending.has(key)) return;
  pending.add(key);
  const selectedSlot = player.selectedSlotIndex;
  const originalDamage = tool.getComponent("minecraft:durability")?.damage;
  const unbreaking = tool.getComponent("minecraft:enchantable")?.getEnchantment("unbreaking")?.level ?? 0;
  system.run(() => {
    try {
      const block = dimension.getBlock(location);
      if (!block || block.typeId !== ore) return;
      block.setType("minecraft:air");
      // Exactly one ore block: Fortune does not multiply classic ore drops.
      dimension.spawnItem(new ItemStack(ore, 1), {
        x: location.x + 0.5, y: location.y + 0.5, z: location.z + 0.5
      });
      const inventory = player.getComponent("minecraft:inventory")?.container;
      const held = inventory?.getItem(selectedSlot);
      const durability = held?.getComponent("minecraft:durability");
      // Do not damage a different item if the player changed tools meanwhile.
      if (held?.typeId === tool.typeId && durability && durability.damage === originalDamage &&
          Math.random() < 1 / (unbreaking + 1)) {
        if (durability.damage + 1 >= durability.maxDurability) {
          inventory.setItem(selectedSlot, undefined);
          player.playSound("random.break");
        } else {
          durability.damage += 1;
          inventory.setItem(selectedSlot, held);
        }
      }
    } catch (error) {
      console.warn(`[Classic Ore Drops] ${error}`);
    } finally { pending.delete(key); }
  });
});
