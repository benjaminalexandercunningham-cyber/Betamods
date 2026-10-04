import { world, system } from "@minecraft/server";
const ALLOWED = new Set([
  "minecraft:arrow",
  "minecraft:boat",
  "minecraft:chest_minecart",
  "minecraft:chicken",
  "minecraft:cow",
  "minecraft:creeper",
  "minecraft:egg",
  "minecraft:falling_block",
  "minecraft:fireball",
  "minecraft:fishing_hook",
  "minecraft:furnace_minecart",
  "minecraft:ghast",
  "minecraft:item",
  "minecraft:lightning_bolt",
  "minecraft:minecart",
  "minecraft:painting",
  "minecraft:pig",
  "minecraft:player",
  "minecraft:sheep",
  "minecraft:skeleton",
  "minecraft:slime",
  "minecraft:snowball",
  "minecraft:spider",
  "minecraft:squid",
  "minecraft:tnt",
  "minecraft:wolf",
  "minecraft:zombie",
  "minecraft:zombie_pigman"
]);
const DIMENSIONS = ["overworld", "nether", "the_end"];
function removeForbidden(entity) {
  if (!ALLOWED.has(entity.typeId) ||
      (entity.typeId !== "minecraft:player" && entity.getComponent("minecraft:is_baby"))) {
    // remove() produces no death animation, loot, XP or poof particle.
    entity.remove();
  }
}
world.afterEvents.entitySpawn.subscribe(({ entity }) => {
  try { removeForbidden(entity); } catch { /* entity already gone; sweep retries */ }
});
let lastWarning = -1200;
system.runInterval(() => {
  for (const name of DIMENSIONS) {
    try {
      for (const entity of world.getDimension(name).getEntities()) {
        try { removeForbidden(entity); } catch { /* invalid entity */ }
      }
    } catch (error) {
      if (system.currentTick - lastWarning >= 1200) {
        console.warn(`[Beta Entity Enforcer] Sweep will retry: ${error}`);
        lastWarning = system.currentTick;
      }
    }
  }
}, 1);
