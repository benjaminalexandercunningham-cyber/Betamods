BETA ENTITY ENFORCER v1.0

Import this .mcaddon into Bedrock 1.21.90+. Activate Beta Entity Enforcer BP in World Settings > Behavior Packs and its companion RP in Resource Packs. Put its RP ABOVE the earlier texture filter so its invisible render definitions take priority. Keep your inventory enforcer active too. Stable Script API; Beta APIs experiment is not required.

KEPT MOBS: chicken, pig, sheep, cow, squid, wolf, zombie, skeleton, spider, creeper, ghast, zombie pigman (Bedrock identifier zombie_pigman), slime. Slimes existed before Beta 1.7.3. Players, dropped items, paintings, original boats/minecarts, arrows, eggs, snowballs, fishing hooks, ghast fireballs, TNT, falling blocks and lightning are also preserved.

BLOCKED: all other catalogued entities, including newer mobs, armor stands, newer projectiles, newer minecarts, chest boats, XP bottles and XP orbs. Custom/unknown entities are removed by the script whitelist too. Spawn rules are disabled where available; catalogued blocked entities have no eggs or summoning permission and instantly despawn. Client rendering is invisible and silent, with no attachments or particle scripts. Existing blocked entities in loaded chunks are removed on the next sweep.

NO DEATH POOF/LOOT/XP: removal uses despawn/remove, not the normal kill/death process. No global death particle texture is altered, so original mobs retain their normal effects. XP orbs from any source are invisible and immediately removed, making XP unavailable. Some sources may internally create an orb before removal; existing player XP levels are not erased.

This suppresses entity TYPES; it does not restore every original mob model, AI, biome spawn rate or pre-Beta subtype. Normal mobs still use modern mechanics. Future unrecognised entity types are removed but cannot have their textures/spawn rules pre-overridden until the pack is updated. Standard three dimensions are swept every tick; unknown custom dimensions are covered only by spawn events. Already placed modern blocks are outside this pack.

Structural checks and simulated spawn/sweep tests passed. No running Bedrock client was available for validation.

VERSION 1.1 — NO BABIES
All entities carrying minecraft:is_baby are removed, including the original animal species, baby zombies, and baby zombie pigmen. Existing loaded babies are removed on the next tick; newborns and naturally spawned babies are checked on spawn and every tick after their baby components are applied. Adults are preserved. Small slimes remain allowed: small slime size is not the baby component. No death animation, loot, XP or poof is created by removal. This replaces the v1.0 entity add-on; use the v1.1 behavior/resource packs together.
