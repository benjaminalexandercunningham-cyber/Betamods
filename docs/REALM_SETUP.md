# Updating the Realm

These steps install or update the Betamods packs on the Realm. They work on any device that runs Minecraft Bedrock, including an iPad. They have not yet been run end to end against a live Realm, so report anything that differs.

Only the Realm owner's account can change the Realm's packs.

## 1. Back up

In Minecraft: **Play → Realms → edit (pencil) on the Realm → Backups**, and make sure a recent backup exists. Download a copy if the world matters.

## 2. Import the packs

1. On the release page, download `betamods-<version>-all.mcaddon`.
2. Open the file with Minecraft. On iPad: tap the download, then **Share → Minecraft** (or open it from the Files app). Minecraft imports all seven packs.

## 3. Apply them to the Realm

Open **Play → Realms → edit (pencil) → Edit World**.

Under **Behavior Packs**, activate these, top to bottom:

1. Classic Ore Drops & Oak Planks
2. Beta Inventory Enforcer
3. Beta Entity Enforcer BP
4. Permafrost Snow & Ice BP (optional)

Under **Resource Packs**, activate these, top to bottom:

1. Beta Entity Enforcer RP
2. Permafrost Snow & Ice RP (optional)
3. Beta Block & Item Filter

The order matters: the entity enforcer and permafrost resource packs must sit above the block/item filter.

If you are updating, deactivate the older version of each pack before activating the new one. Then leave the settings screen and let the Realm restart; players download the resource packs when they next join.

## Permafrost is optional and sticky

Permafrost replaces snow and ice with custom blocks. Only activate it if you want that. Once it has run in the world, do not deactivate it without reverting first: run `/scriptevent classic_permafrost:revert`, visit the converted areas, then deactivate both of its packs.

## If Edit World will not apply the packs

Fallback: in the Realm's settings, download the world, apply the packs to that local copy in its world settings, then use **Replace World** to upload it back. This overwrites the Realm world with your copy, so do it while nobody is playing.

## After updating

Old pack versions stay on the device. Remove them under **Settings → Storage** so they are not activated by mistake.
