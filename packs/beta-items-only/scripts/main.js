import { world, system, EquipmentSlot, ItemStack } from "@minecraft/server";
import { ALLOWLIST } from "./allowlist.js";

// Everything not listed in allowlist.json is deleted, including items added
// by future game versions and by other packs.
const ALLOWED = new Set(ALLOWLIST);

// Beta iron and gold ore dropped the ore block. The modern game drops raw
// metal, which is not a Beta item, so those drops are swapped for the ore
// block instead of being deleted. Without this iron and gold are unobtainable.
const DROP_CONVERSIONS = new Map([
  ["minecraft:raw_iron", "minecraft:iron_ore"],
  ["minecraft:raw_gold", "minecraft:gold_ore"],
]);

const SWEEP_INTERVAL_TICKS = 20; // about once a second
const EQUIPMENT_SLOTS = [
  EquipmentSlot.Head,
  EquipmentSlot.Chest,
  EquipmentSlot.Legs,
  EquipmentSlot.Feet,
  EquipmentSlot.Offhand,
];

// Backstop for block drops, mob drops and anything thrown out of a container.
function checkItemEntity(entity) {
  try {
    if (!entity.isValid || entity.typeId !== "minecraft:item") return;
    const stack = entity.getComponent("minecraft:item")?.itemStack;
    if (!stack || ALLOWED.has(stack.typeId)) return;
    const replacement = DROP_CONVERSIONS.get(stack.typeId);
    const { dimension, location } = entity;
    entity.remove();
    if (replacement) dimension.spawnItem(new ItemStack(replacement, stack.amount), location);
  } catch (error) {
    console.warn(`[Beta Items Only] item check failed: ${error}`);
  }
}

// Clears every stack that is not on the allowlist out of a container.
function sweepContainer(container) {
  for (let slot = 0; slot < container.size; slot++) {
    const item = container.getItem(slot);
    if (!item || ALLOWED.has(item.typeId)) continue;
    const replacement = DROP_CONVERSIONS.get(item.typeId);
    container.setItem(slot, replacement ? new ItemStack(replacement, item.amount) : undefined);
  }
}

// Backstop for chest loot, trades, /give and anything else that puts an item
// straight into a player's hands.
function sweepPlayer(player) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (container) sweepContainer(container);
  const equippable = player.getComponent("minecraft:equippable");
  if (equippable) {
    for (const slot of EQUIPMENT_SLOTS) {
      const item = equippable.getEquipment(slot);
      if (item && !ALLOWED.has(item.typeId)) equippable.setEquipment(slot, undefined);
    }
  }
  const cursor = player.getComponent("minecraft:cursor_inventory");
  if (cursor?.item && !ALLOWED.has(cursor.item.typeId)) cursor.clear();
}

// Chests, furnaces, hoppers and other storage blocks are swept as a player
// opens them, so items stored before the pack was added never reach the screen.
world.beforeEvents.playerInteractWithBlock.subscribe(({ block }) => {
  const { dimension, location } = block;
  // Before events cannot modify the world; do the sweep right after.
  system.run(() => {
    try {
      const container = dimension.getBlock(location)?.getComponent("minecraft:inventory")?.container;
      if (container) sweepContainer(container);
    } catch (error) {
      console.warn(`[Beta Items Only] container sweep failed: ${error}`);
    }
  });
});

world.afterEvents.entitySpawn.subscribe(({ entity }) => checkItemEntity(entity));
// Items already lying in a chunk when it loads do not fire entitySpawn.
world.afterEvents.entityLoad.subscribe(({ entity }) => checkItemEntity(entity));

system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    try {
      sweepPlayer(player);
    } catch (error) {
      console.warn(`[Beta Items Only] sweep failed for ${player.name}: ${error}`);
    }
  }
}, SWEEP_INTERVAL_TICKS);
