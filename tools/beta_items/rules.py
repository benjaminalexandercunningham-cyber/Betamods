"""Beta 1.7.3 facts the generator cannot derive from allowlist.json.

Sources: Minecraft Wiki version-history sections (recipe yields, drops) and
the vanilla Bedrock pack files (identifiers, legacy names).
"""

M = "minecraft:"

# --------------------------------------------------------------------------
# Mobs
# --------------------------------------------------------------------------

BETA_MOBS = {M + n for n in (
    "pig", "cow", "sheep", "chicken", "squid", "wolf", "zombie", "skeleton",
    "spider", "creeper", "slime", "ghast",
    "zombie_pigman",  # Bedrock identifier of the zombified piglin
)}

# --------------------------------------------------------------------------
# Legacy item names still used inside vanilla recipe and loot files
# --------------------------------------------------------------------------

_COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
            "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
_WOODS = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak"]


def _variants(names):
    return {i: M + n for i, n in enumerate(names)}


# name -> {data value -> modern identifier}
LEGACY_VARIANTS = {
    M + "dye": _variants([
        "ink_sac", "red_dye", "green_dye", "cocoa_beans", "lapis_lazuli", "purple_dye",
        "cyan_dye", "light_gray_dye", "gray_dye", "pink_dye", "lime_dye", "yellow_dye",
        "light_blue_dye", "magenta_dye", "orange_dye", "bone_meal", "black_dye",
        "brown_dye", "blue_dye", "white_dye"]),
    M + "wool": _variants([c + "_wool" for c in _COLOURS]),
    M + "carpet": _variants([c + "_carpet" for c in _COLOURS]),
    M + "log": _variants([w + "_log" for w in _WOODS[:4]]),
    M + "log2": _variants([w + "_log" for w in _WOODS[4:]]),
    M + "wood": _variants([w + "_wood" for w in _WOODS]),
    M + "planks": _variants([w + "_planks" for w in _WOODS]),
    M + "sapling": _variants([w + "_sapling" for w in _WOODS]),
    M + "boat": _variants([w + "_boat" for w in _WOODS]),
    M + "coal": _variants(["coal", "charcoal"]),
    M + "bucket": {0: M + "bucket", 1: M + "milk_bucket", 8: M + "water_bucket", 10: M + "lava_bucket"},
}

# name -> modern identifier, whatever the data value
LEGACY_NAMES = {
    M + "sign": M + "oak_sign",
    M + "fish": M + "cod",
    M + "cooked_fish": M + "cooked_cod",
    M + "reeds": M + "sugar_cane",
    M + "emptymap": M + "empty_map",
    M + "map": M + "empty_map",
    M + "record_13": M + "music_disc_13",
    M + "record_cat": M + "music_disc_cat",
}

# Identifiers where a non-zero data value still selects a different,
# post-Beta item (sandstone 3 is smooth sandstone, sand 1 is red sand).
DATA_IS_VARIANT = {M + n for n in ("sandstone", "stone", "sand", "dirt", "sponge", "golden_apple")}

# Item tags used as recipe ingredients -> the members that could be allowed.
# Tags not listed here have no Beta members.
ITEM_TAGS = {
    M + "planks": [M + "oak_planks"],
    M + "logs": [M + "oak_log", M + "spruce_log", M + "birch_log"],
    M + "logs_that_burn": [M + "oak_log", M + "spruce_log", M + "birch_log"],
    M + "coals": [M + "coal", M + "charcoal"],
    M + "stone_tool_materials": [M + "cobblestone"],
    M + "stone_crafting_materials": [M + "cobblestone"],
    M + "wooden_slabs": [M + "oak_slab"],
    M + "wool": [M + c + "_wool" for c in _COLOURS],
    M + "egg": [M + "egg"],
    M + "mushrooms_for_stew": [M + "red_mushroom", M + "brown_mushroom"],
    M + "soul_fire_base_blocks": [M + "soul_sand"],
}

# --------------------------------------------------------------------------
# Recipes
# --------------------------------------------------------------------------


def _count(n):
    def apply(body):
        result = body["result"]
        (result[0] if isinstance(result, list) else result)["count"] = n
    return apply


def _result(item):
    def apply(body):
        body["result"]["item"] = item
        body["result"].pop("data", None)
    return apply


def _golden_apple(body):
    body["key"]["#"] = {"item": M + "gold_block"}


def _fence(body):
    body["pattern"] = ["###", "###"]
    body["key"] = {"#": {"item": M + "stick"}}
    body["unlock"] = [{"item": M + "stick"}]
    body["result"] = {"item": M + "oak_fence", "count": 2}


def _button(body):
    body["pattern"] = ["#", "#"]


def _book(body):
    body["ingredients"] = [i for i in body["ingredients"] if i["item"] != M + "leather"]


# vanilla recipe identifier (without namespace) -> (what changed, how)
RECIPE_REWRITES = {
    "golden_apple": ("8 gold blocks around the apple instead of 8 gold ingots", _golden_apple),
    "oak_fence": ("6 sticks give 2 fences instead of 4 planks + 2 sticks giving 3", _fence),
    "sign_oak": ("yields 1 sign instead of 3", _count(1)),
    "ladder": ("yields 2 ladders instead of 3", _count(2)),
    "wooden_door": ("yields 1 door instead of 3", _count(1)),
    "iron_door": ("yields 1 door instead of 3", _count(1)),
    "book": ("3 paper, no leather (stays shapeless; Beta needed a vertical column)", _book),
    "stone_button": ("2 stone in a column instead of 1 stone", _button),
    "oak_wooden_slab": ("yields 3 slabs instead of 6", _count(3)),
    "red_dye_from_poppy": ("yields 2 rose red instead of 1", _count(2)),
    "yellow_dye_from_dandelion": ("yields 2 dandelion yellow instead of 1", _count(2)),
    "spruce_planks": ("spruce logs give oak planks, the only plank type", _result(M + "oak_planks")),
    "birch_planks": ("birch logs give oak planks, the only plank type", _result(M + "oak_planks")),
}

# Recipes made only of allowlisted items that Beta 1.7.3 did not have.
RECIPE_NOT_IN_BETA = {
    "fence": "modern planks-and-sticks fence; the 6-stick recipe replaces it",
    "map": "maps needed a compass (locator_map is the Beta recipe)",
    "basic_map_to_enhanced": "map upgrading",
    "empty_map_to_enhanced": "map upgrading",
    "cobweb_to_string": "cobwebs could not be crafted into string",
    "saddle": "saddles were dungeon loot only",
    "snow_layer": "snow layers could not be crafted",
}

# (input, output) pairs the Beta furnace accepted.
BETA_SMELTING = {(M + a, M + b) for a, b in (
    ("iron_ore", "iron_ingot"), ("gold_ore", "gold_ingot"), ("diamond_ore", "diamond"),
    ("sand", "glass"), ("cobblestone", "stone"), ("clay_ball", "brick"),
    ("porkchop", "cooked_porkchop"), ("cod", "cooked_cod"), ("cactus", "green_dye"),
    ("oak_log", "charcoal"), ("spruce_log", "charcoal"), ("birch_log", "charcoal"),
)}

# Allowlisted items that had a crafting or smelting recipe in Beta 1.7.3.
# The generator refuses to finish if any of them ends up with no recipe.
BETA_CRAFTABLE = {M + n for n in """
oak_planks stick torch crafting_table furnace chest ladder oak_fence oak_sign wooden_door iron_door
trapdoor oak_stairs stone_stairs smooth_stone_slab cobblestone_slab sandstone_slab oak_slab
wooden_pressure_plate stone_pressure_plate stone_button lever redstone_torch repeater
dispenser noteblock jukebox piston sticky_piston tnt rail golden_rail detector_rail
minecart chest_minecart oak_boat bed bookshelf
iron_block gold_block diamond_block lapis_block iron_ingot gold_ingot diamond lapis_lazuli
sandstone snow clay brick_block glowstone white_wool lit_pumpkin
stone glass brick charcoal green_dye cooked_porkchop cooked_cod
wooden_sword wooden_shovel wooden_pickaxe wooden_axe wooden_hoe
stone_sword stone_shovel stone_pickaxe stone_axe stone_hoe
iron_sword iron_shovel iron_pickaxe iron_axe iron_hoe
diamond_sword diamond_shovel diamond_pickaxe diamond_axe diamond_hoe
golden_sword golden_shovel golden_pickaxe golden_axe golden_hoe
leather_helmet leather_chestplate leather_leggings leather_boots
iron_helmet iron_chestplate iron_leggings iron_boots
diamond_helmet diamond_chestplate diamond_leggings diamond_boots
golden_helmet golden_chestplate golden_leggings golden_boots
bow arrow fishing_rod flint_and_steel shears compass clock bucket bowl
mushroom_stew bread cake cookie sugar paper book painting golden_apple empty_map
bone_meal red_dye yellow_dye orange_dye pink_dye lime_dye light_blue_dye cyan_dye
purple_dye magenta_dye gray_dye light_gray_dye
orange_wool magenta_wool light_blue_wool yellow_wool lime_wool pink_wool gray_wool light_gray_wool
cyan_wool purple_wool blue_wool brown_wool green_wool red_wool black_wool
""".split()}

# Beta-craftable items whose modern recipe is built into the game instead of
# shipped as a recipe file. They stay craftable, but cannot be overridden, so
# their yields stay modern (slabs give 6, not 3). The generator checks that
# this list is still accurate.
BUILT_IN_RECIPES = {M + n for n in (
    "bed", "trapdoor", "wooden_pressure_plate",
    "smooth_stone_slab", "cobblestone_slab", "sandstone_slab",
    *(c + "_wool" for c in _COLOURS if c != "white"),
)}

# --------------------------------------------------------------------------
# Loot tables
# --------------------------------------------------------------------------

# An entry using one of these produces a post-Beta item whatever its name.
LOOT_FUNCTIONS_POST_BETA = {
    "exploration_map", "set_potion", "set_stew_effect", "set_banner_details",
    "set_armor_trim", "enchant_book_for_trading", "set_ominous_bottle_amplifier",
}
# Removed from entries that are kept: Beta had no enchantments.
LOOT_FUNCTIONS_STRIPPED = {
    "enchant_randomly", "enchant_with_levels", "enchant_random_gear", "specific_enchants",
}


def _drop(name, low, high, *extra):
    functions = [{"function": "set_count", "count": {"min": low, "max": high}}, *extra]
    return {"rolls": 1, "entries": [{"type": "item", "name": name, "weight": 1, "functions": functions}]}


_COOKED_IF_BURNING = {
    "function": "furnace_smelt",
    "conditions": [{"condition": "entity_properties", "entity": "this", "properties": {"on_fire": True}}],
}

# Whole-file replacements, keyed by path below loot_tables/.
LOOT_OVERRIDES = {
    "entities/pig.json": {"pools": [_drop(M + "porkchop", 0, 2, _COOKED_IF_BURNING)]},
    "entities/cow.json": {"pools": [_drop(M + "leather", 0, 2)]},
    # One wool of the sheep's colour, written the way the vanilla table does.
    "entities/sheep.json": {"pools": [{"rolls": 1, "entries": [{
        "type": "item", "name": M + "wool", "weight": 1,
        "functions": [{"function": "minecraft:set_data_from_color_index"}]}]}]},
    "entities/chicken.json": {"pools": [_drop(M + "feather", 0, 2)]},
    "entities/squid.json": {"pools": [_drop(M + "dye", 1, 3, {"function": "set_data", "data": 0})]},
    "entities/zombie.json": {"pools": [_drop(M + "feather", 0, 2)]},
    "entities/skeleton.json": {"pools": [_drop(M + "arrow", 0, 2), _drop(M + "bone", 0, 2)]},
    "entities/spider.json": {"pools": [_drop(M + "string", 0, 2)]},
    "entities/creeper.json": {"pools": [
        _drop(M + "gunpowder", 0, 2),
        {"conditions": [{"condition": "killed_by_entity", "entity_type": M + "skeleton"}],
         "rolls": 1,
         "entries": [{"type": "item", "name": M + "record_13"}, {"type": "item", "name": M + "record_cat"}]},
    ]},
    "entities/slime.json": {"pools": [_drop(M + "slime_ball", 0, 2)]},
    "entities/ghast.json": {"pools": [_drop(M + "gunpowder", 0, 2)]},
    "entities/zombie_pigman.json": {"pools": [_drop(M + "cooked_porkchop", 0, 2)]},
    # Beta fishing only ever gave raw fish.
    "gameplay/fishing.json": {"pools": [{"rolls": 1, "entries": [
        {"type": "loot_table", "name": "loot_tables/gameplay/fishing/fish.json", "weight": 1}]}]},
    "gameplay/jungle_fishing.json": {"pools": [{"rolls": 1, "entries": [
        {"type": "loot_table", "name": "loot_tables/gameplay/fishing/fish.json", "weight": 1}]}]},
}
