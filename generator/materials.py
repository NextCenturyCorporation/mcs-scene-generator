from typing import List, NamedTuple


class MaterialTuple(NamedTuple):
    material: str
    color: List[str]


UNTRAINED_COLOR_LIST = [
    # Won't be used in Eval 3
]

AZURE = MaterialTuple("Custom/Materials/Azure", ["azure", "blue"])
BLACK = MaterialTuple("Custom/Materials/Black", ["black"])
BLUE = MaterialTuple("Custom/Materials/Blue", ["blue"])
BROWN = MaterialTuple("Custom/Materials/Brown", ["brown", "orange"])
CHARTREUSE = MaterialTuple(
    "Custom/Materials/Chartreuse",
    ["chartreuse", "green", "yellow"]
)
CREAM = MaterialTuple("Custom/Materials/Cream", ["cream", "white"])
CYAN = MaterialTuple("Custom/Materials/Cyan", ["cyan", "blue", "green"])
DARKGREY = MaterialTuple(
    "Custom/Materials/DarkGrey",
    ["darkslategrey", "grey"]
)
GOLDENROD = MaterialTuple(
    "Custom/Materials/Goldenrod",
    ["goldenrod", "yellow", "orange"]
)
GREEN = MaterialTuple("Custom/Materials/Green", ["green"])
GREY = MaterialTuple("Custom/Materials/Grey", ["grey"])
INDIGO = MaterialTuple(
    "Custom/Materials/Indigo",
    ["indigo", "blue", "purple"]
)
LIME = MaterialTuple("Custom/Materials/Lime", ["lime", "green"])
MAGENTA = MaterialTuple(
    "Custom/Materials/Magenta",
    ["magenta", "purple", "red"]
)
MAROON = MaterialTuple("Custom/Materials/Maroon", ["maroon", "red"])
NAVY = MaterialTuple("Custom/Materials/Navy", ["navy", "blue"])
OLIVE = MaterialTuple("Custom/Materials/Olive", ["olive", "yellow", "green"])
ORANGE = MaterialTuple("Custom/Materials/Orange", ["orange"])
PINK = MaterialTuple("Custom/Materials/Pink", ["pink", "red"])
RED = MaterialTuple("Custom/Materials/Red", ["red"])
ROSE = MaterialTuple("Custom/Materials/Rose", ["rose", "red", "purple"])
PURPLE = MaterialTuple("Custom/Materials/Purple", ["purple"])
SPRINGGREEN = MaterialTuple(
    "Custom/Materials/SpringGreen",
    ["springgreen", "green"]
)
TAN = MaterialTuple("Custom/Materials/Tan", ["tan", "brown"])
TEAL = MaterialTuple("Custom/Materials/Teal", ["teal", "blue", "green"])
VIOLET = MaterialTuple(
    "Custom/Materials/Violet",
    ["violet", "purple", "blue"]
)
WHITE = MaterialTuple("Custom/Materials/White", ["white"])
YELLOW = MaterialTuple("Custom/Materials/Yellow", ["yellow"])

# Only colors that are exact opposites of one another (uses RGB color wheel).
# Only use bright colors with max saturation/value in this specific list.
OBJECT_OPPOSITE_MATERIALS = [
    AZURE,
    BLUE,
    CHARTREUSE,
    CYAN,
    MAGENTA,
    ORANGE,
    ROSE,
    SPRINGGREEN,
    VIOLET,
    YELLOW
]

# Do not use any placer colors (cyan/magenta) in this specific list.
WALL_OPPOSITE_MATERIALS = [
    AZURE,
    BLUE,
    CHARTREUSE,
    GREEN,
    MAROON,
    NAVY,
    OLIVE,
    ORANGE,
    PURPLE,
    ROSE,
    SPRINGGREEN,
    TEAL,
    VIOLET,
    YELLOW
]

# Colors that are exact opposites of one another using the RGB color wheel.
OPPOSITE_SETS = {
    "Custom/Materials/Azure": ORANGE,
    "Custom/Materials/Black": WHITE,
    "Custom/Materials/Blue": YELLOW,
    "Custom/Materials/Chartreuse": VIOLET,
    "Custom/Materials/Cyan": MAGENTA,
    "Custom/Materials/Goldenrod": INDIGO,  # Not an official opposite
    "Custom/Materials/Green": PURPLE,
    "Custom/Materials/Indigo": GOLDENROD,  # Not an official opposite
    "Custom/Materials/Magenta": CYAN,
    "Custom/Materials/Maroon": TEAL,
    "Custom/Materials/Navy": OLIVE,
    "Custom/Materials/Olive": NAVY,
    "Custom/Materials/Orange": AZURE,
    "Custom/Materials/Purple": GREEN,
    "Custom/Materials/Rose": SPRINGGREEN,
    "Custom/Materials/SpringGreen": ROSE,
    "Custom/Materials/Teal": MAROON,
    "Custom/Materials/Violet": CHARTREUSE,
    "Custom/Materials/White": BLACK,
    "Custom/Materials/Yellow": BLUE
}

ADJACENT_SETS = {
    "Custom/Materials/Azure": [
        BLUE.material, CYAN.material, NAVY.material, TEAL.material
    ],
    "Custom/Materials/Black": [GREY.material],
    "Custom/Materials/Blue": [
        AZURE.material, INDIGO.material, NAVY.material, VIOLET.material
    ],
    "Custom/Materials/Brown": [
        GOLDENROD.material, MAROON.material, OLIVE.material, ORANGE.material,
        RED.material, YELLOW.material
    ],
    "Custom/Materials/Chartreuse": [
        GOLDENROD.material, GREEN.material, LIME.material, OLIVE.material,
        YELLOW.material
    ],
    "Custom/Materials/Cyan": [
        AZURE.material, SPRINGGREEN.material, TEAL.material
    ],
    "Custom/Materials/Goldenrod": [
        BROWN.material, CHARTREUSE.material, OLIVE.material, ORANGE.material,
        YELLOW.material
    ],
    "Custom/Materials/Green": [
        CHARTREUSE.material, LIME.material, SPRINGGREEN.material
    ],
    "Custom/Materials/Grey": [BLACK.material, WHITE.material],
    "Custom/Materials/Indigo": [
        BLUE.material, NAVY.material, PURPLE.material, VIOLET.material
    ],
    "Custom/Materials/Lime": [
        CHARTREUSE.material, GREEN.material, SPRINGGREEN.material
    ],
    "Custom/Materials/Magenta": [
        PURPLE.material, ROSE.material, VIOLET.material
    ],
    "Custom/Materials/Maroon": [
        BROWN.material, ORANGE.material, RED.material, ROSE.material
    ],
    "Custom/Materials/Navy": [
        AZURE.material, BLUE.material, INDIGO.material, VIOLET.material
    ],
    "Custom/Materials/Olive": [
        BROWN.material, CHARTREUSE.material, GOLDENROD.material,
        ORANGE.material, YELLOW.material
    ],
    "Custom/Materials/Orange": [
        BROWN.material, GOLDENROD.material, MAROON.material, OLIVE.material,
        RED.material, YELLOW.material
    ],
    "Custom/Materials/Purple": [
        INDIGO.material, MAGENTA.material, ROSE.material, VIOLET.material
    ],
    "Custom/Materials/Red": [
        BROWN.material, MAROON.material, ORANGE.material, ROSE.material
    ],
    "Custom/Materials/Rose": [
        MAGENTA.material, MAROON.material, PURPLE.material, RED.material
    ],
    "Custom/Materials/SpringGreen": [
        CYAN.material, GREEN.material, LIME.material, TEAL.material
    ],
    "Custom/Materials/Teal": [
        AZURE.material, CYAN.material, SPRINGGREEN.material
    ],
    "Custom/Materials/Violet": [
        BLUE.material, INDIGO.material, MAGENTA.material, NAVY.material,
        PURPLE.material
    ],
    "Custom/Materials/White": [GREY.material],
    "Custom/Materials/Yellow": [
        BROWN.material, CHARTREUSE.material, GOLDENROD.material,
        OLIVE.material, ORANGE.material
    ]
}

_CUSTOM_MATERIALS = [
    AZURE,
    BLACK,
    BLUE,
    BROWN,
    CHARTREUSE,
    CREAM,
    CYAN,
    DARKGREY,
    GREEN,
    GREY,
    LIME,
    MAGENTA,
    MAROON,
    NAVY,
    OLIVE,
    ORANGE,
    RED,
    ROSE,
    PURPLE,
    SPRINGGREEN,
    TEAL,
    VIOLET,
    WHITE,
    YELLOW
]

CUSTOM_CARPET_MATERIALS = [
    MaterialTuple(item.material + 'CarpetMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

CUSTOM_DRYWALL_MATERIALS = [
    MaterialTuple(item.material + 'DrywallMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

CUSTOM_WOOD_MATERIALS = [
    MaterialTuple(item.material + 'WoodMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

BLOCK_BLANK_MATERIALS = [
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1",
        ["blue"]
    ),
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1",
        ["grey"]
    ),
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1",
        ["green"]
    ),
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1",
        ["red"]
    ),
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1",
        ["brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1",
        ["yellow"]
    )
]

BLOCK_LETTER_MATERIALS = [
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_A_Blue_1K/ToyBlockBlueA",
        ["blue", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_B_Blue_1K/ToyBlockBlueB",
        ["blue", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC",
        ["blue", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_D_Blue_1K/ToyBlockBlueD",
        ["blue", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM",
        ["blue", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS",
        ["blue", "brown"]
    )
]

BLOCK_NUMBER_MATERIALS = [
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1",
        ["yellow", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2",
        ["yellow", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3",
        ["yellow", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_4_Yellow_1K/NumberBlockYellow_4",
        ["yellow", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_5_Yellow_1K/NumberBlockYellow_5",
        ["yellow", "brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_6_Yellow_1K/NumberBlockYellow_6",
        ["yellow", "brown"]
    )
]

CARDBOARD_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_Tan", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_White", ["grey"])
]

BROWN_MARBLE_FAKE_1 = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/BrownMarbleFake 1",
    ["brown", "orange"]
)
CONCRETE_BOARDS_1 = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/ConcreteBoards1",
    ["grey", "white"]
)
CONCRETE_FLOOR = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/ConcreteFloor",
    ["grey", "black", "blue"]
)
GREY_GRANITE = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/GREYGRANITE",
    ["grey"]
)
PINK_CONCRETE_BEDROOM_1 = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/PinkConcrete_Bedroom1",
    ["red", "grey"]
)
WHITE_COUNTERTOP = MaterialTuple(
    "AI2-THOR/Materials/Ceramics/WhiteCountertop",
    ["grey", "white"]
)

CERAMIC_MATERIALS = [
    BROWN_MARBLE_FAKE_1,
    CONCRETE_BOARDS_1,
    CONCRETE_FLOOR,
    GREY_GRANITE,
    PINK_CONCRETE_BEDROOM_1,
    WHITE_COUNTERTOP
    # Don't use the brick or cobblestone textures.
]

CARPET_2 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/Carpet2",
    ["brown", "grey"]
)
CARPET_3 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/Carpet3",
    ["brown"]
)
CARPET_4 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/Carpet4",
    ["blue", "black"]
)
CARPET_8 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/Carpet8",
    ["black"]
)
CARPET_DARK = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetDark",
    ["yellow", "brown"]
)
CARPET_DARK_1 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetDark 1",
    ["brown"]
)
CARPET_DARK_GREEN = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetDarkGreen",
    ["green"]
)
CARPET_GREEN = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetGreen",
    ["green"]
)
CARPET_WHITE = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetWhite",
    ["white"]
)
CARPET_WHITE_3 = MaterialTuple(
    "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
    ["white", "grey"]
)

FABRIC_MATERIALS = [
    CARPET_2,
    CARPET_3,
    CARPET_4,
    CARPET_8,
    CARPET_DARK,
    CARPET_DARK_1,
    CARPET_DARK_GREEN,
    CARPET_GREEN,
    CARPET_WHITE,
    CARPET_WHITE_3
    # Don't use highly patterned multicolor carpet textures.
] + CUSTOM_CARPET_MATERIALS

LEATHER_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Leather", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Leather2", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Leather3", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Leather 2", ["black"])
]

# Only used with antique_armchair_1
LEATHER_ARMCHAIR_MATERIALS = [
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_1",
        ["brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_2",
        ["grey"]
    ),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_3",
        ["brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_4",
        ["grey"]
    ),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_normal_OLD",
        ["brown"]
    )

]

BLACK_SMOOTH_METAL = MaterialTuple(
    "AI2-THOR/Materials/Metals/BlackSmoothMeta",
    ["black"]
)
BRASS_1 = MaterialTuple(
    "AI2-THOR/Materials/Metals/Brass 1",
    ["yellow", "brown"]
)
BROWN_METAL_1 = MaterialTuple(
    "AI2-THOR/Materials/Metals/BrownMetal 1",
    ["brown"]
)
BRUSHED_ALUMINUM_BLUE = MaterialTuple(
    "AI2-THOR/Materials/Metals/BrushedAluminum_Blue",
    ["blue", "grey"]
)
BRUSHED_IRON_ALBEDO = MaterialTuple(
    "AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency",
    ["black", "grey"]
)
GENERIC_STAINLESS_STEEL = MaterialTuple(
    "AI2-THOR/Materials/Metals/GenericStainlessSteel",
    ["grey"]
)
HAMMERED_METAL_ALBEDO = MaterialTuple(
    "AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1",
    ["brown"]
)
METAL = MaterialTuple("AI2-THOR/Materials/Metals/Metal", ["grey", "white"])
WHITE_METAL = MaterialTuple("AI2-THOR/Materials/Metals/WhiteMetal", ["white"])
NURSERY_CABINET_METAL = MaterialTuple(
    "UnityAssetStore/Baby_Room/Models/Materials/cabinet metal",
    ["grey"]
)

METAL_MATERIALS = [
    BLACK_SMOOTH_METAL,
    BRASS_1,
    BROWN_METAL_1,
    BRUSHED_ALUMINUM_BLUE,
    BRUSHED_IRON_ALBEDO,
    GENERIC_STAINLESS_STEEL,
    HAMMERED_METAL_ALBEDO,
    METAL,
    WHITE_METAL,
    NURSERY_CABINET_METAL
]

BLACK_PLASTIC = MaterialTuple(
    "AI2-THOR/Materials/Plastics/BlackPlastic",
    ["black"]
)
ORANGE_PLASTIC = MaterialTuple(
    "AI2-THOR/Materials/Plastics/OrangePlastic",
    ["orange"]
)
WHITE_PLASTIC = MaterialTuple(
    "AI2-THOR/Materials/Plastics/WhitePlastic",
    ["white"]
)
KINDERGARTEN_RED_PLASTIC = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1",
    ["red"]
)
KINDERGARTEN_BLUE_PLASTIC = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2",
    ["blue"]
)
KINDERGARTEN_GREEN_PLASTIC = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3",
    ["green"]
)
KINDERGARTEN_YELLOW_PLASTIC = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4",
    ["yellow"]
)

PLASTIC_MATERIALS = [
    BLACK_PLASTIC,
    ORANGE_PLASTIC,
    WHITE_PLASTIC,
    KINDERGARTEN_RED_PLASTIC,
    KINDERGARTEN_BLUE_PLASTIC,
    KINDERGARTEN_GREEN_PLASTIC,
    KINDERGARTEN_YELLOW_PLASTIC
]

BLUE_RUBBER = MaterialTuple(
    "AI2-THOR/Materials/Plastics/BlueRubber",
    ["blue"]
)
LIGHT_BLUE_RUBBER = MaterialTuple(
    "AI2-THOR/Materials/Plastics/LightBlueRubber",
    ["blue"]
)

RUBBER_MATERIALS = [
    BLUE_RUBBER,
    LIGHT_BLUE_RUBBER
]

BROWN_DRYWALL = MaterialTuple(
    "AI2-THOR/Materials/Walls/BrownDrywall",
    ["brown"]
)
DRYWALL = MaterialTuple(
    "AI2-THOR/Materials/Walls/Drywall",
    ["white", "grey"]
)
DRYWALL_BEIGE = MaterialTuple(
    "AI2-THOR/Materials/Walls/DrywallBeige",
    ["white", "brown"]
)
DRYWALL_GREEN = MaterialTuple(
    "AI2-THOR/Materials/Walls/DrywallGreen",
    ["green"]
)
DRYWALL_ORANGE = MaterialTuple(
    "AI2-THOR/Materials/Walls/DrywallOrange",
    ["orange"]
)
DRYWALL_4_TILED = MaterialTuple(
    "AI2-THOR/Materials/Walls/Drywall4Tiled",
    ["white"]
)
EGGSHELL_DRYWALL = MaterialTuple(
    "AI2-THOR/Materials/Walls/EggshellDrywall",
    ["blue"]
)
RED_DRYWALL = MaterialTuple("AI2-THOR/Materials/Walls/RedDrywall", ["red"])
WALL_DRYWALL_GREY = MaterialTuple(
    "AI2-THOR/Materials/Walls/WallDrywallGrey",
    ["grey", "white"]
)
YELLOW_DRYWALL = MaterialTuple(
    "AI2-THOR/Materials/Walls/YellowDrywall",
    ["yellow"]
)

CEILING_MATERIALS = [
    DRYWALL_4_TILED,
    DRYWALL_BEIGE,
    DRYWALL,
    WALL_DRYWALL_GREY
]

WALL_MATERIALS = [
    BROWN_DRYWALL,
    DRYWALL,
    DRYWALL_BEIGE,
    DRYWALL_GREEN,
    DRYWALL_ORANGE,
    DRYWALL_4_TILED,
    EGGSHELL_DRYWALL,
    RED_DRYWALL,
    WALL_DRYWALL_GREY,
    YELLOW_DRYWALL
] + CUSTOM_DRYWALL_MATERIALS

BEDROOM_FLOOR_1 = MaterialTuple(
    "AI2-THOR/Materials/Wood/BedroomFloor1",
    ["brown", "orange"]
)
BLACK_WOOD = MaterialTuple("AI2-THOR/Materials/Wood/BlackWood", ["black"])
DARK_WOOD_2 = MaterialTuple("AI2-THOR/Materials/Wood/DarkWood2", ["black"])
DARK_WOOD_SMOOTH_2 = MaterialTuple(
    "AI2-THOR/Materials/Wood/DarkWoodSmooth2",
    ["black"]
)
LIGHT_WOOD_COUNTERS_1 = MaterialTuple(
    "AI2-THOR/Materials/Wood/LightWoodCounters 1",
    ["brown", "orange"]
)
LIGHT_WOOD_COUNTERS_3 = MaterialTuple(
    "AI2-THOR/Materials/Wood/LightWoodCounters3",
    ["brown", "red"]
)
LIGHT_WOOD_COUNTERS_4 = MaterialTuple(
    "AI2-THOR/Materials/Wood/LightWoodCounters4",
    ["brown"]
)
TEXTURES_COM_WOOD_FINE_50_1_SEEMLESS = MaterialTuple(
    "AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S",
    ["brown", "red"]
)
WHITE_WOOD = MaterialTuple("AI2-THOR/Materials/Wood/WhiteWood", ["white"])
WOOD_FLOORS_CROSS = MaterialTuple(
    "AI2-THOR/Materials/Wood/WoodFloorsCross",
    ["brown", "yellow"]
)
WOOD_GRAIN_BROWN = MaterialTuple(
    "AI2-THOR/Materials/Wood/WoodGrain_Brown",
    ["brown"]
)
WOOD_GRAIN_TAN = MaterialTuple(
    "AI2-THOR/Materials/Wood/WoodGrain_Tan",
    ["brown"]
)
WORN_WOOD = MaterialTuple(
    "AI2-THOR/Materials/Wood/WornWood",
    ["brown", "black"]
)
KINDERGARTEN_BLUE_WOOD = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1",
    ["blue"]
)
KINDERGARTEN_RED_WOOD = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2",
    ["red"]
)
KINDERGARTEN_GREEN_WOOD = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3",
    ["green"]
)
KINDERGARTEN_YELLOW_WOOD = MaterialTuple(
    "UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4",
    ["yellow"]
)
NURSERY_BROWN_WOOD = MaterialTuple(
    "UnityAssetStore/Baby_Room/Models/Materials/wood 1",
    ["brown"]
)

WOOD_MATERIALS = [
    BEDROOM_FLOOR_1,
    BLACK_WOOD,
    DARK_WOOD_2,
    DARK_WOOD_SMOOTH_2,
    LIGHT_WOOD_COUNTERS_1,
    LIGHT_WOOD_COUNTERS_3,
    LIGHT_WOOD_COUNTERS_4,
    TEXTURES_COM_WOOD_FINE_50_1_SEEMLESS,
    WHITE_WOOD,
    WOOD_FLOORS_CROSS,
    WOOD_GRAIN_BROWN,
    WOOD_GRAIN_TAN,
    WORN_WOOD,
    KINDERGARTEN_BLUE_WOOD,
    KINDERGARTEN_RED_WOOD,
    KINDERGARTEN_GREEN_WOOD,
    KINDERGARTEN_YELLOW_WOOD,
    NURSERY_BROWN_WOOD
] + CUSTOM_WOOD_MATERIALS

# Only used with sofa_1
SOFA_1_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_Blue", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_Gold", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_Salmon", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_Red", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa1_White", ["white"])
]

# Only used with sofa_chair_1
SOFA_CHAIR_1_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_Black", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_Blue", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_Gold", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_Salmon", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/SofaChair1_White", ["white"])
]

# Only used with sofa_2 and sofa_chair_2
SOFA_2_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa2_Grey", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa2_White", ["white"]),
    MaterialTuple(
        "AI2-THOR/Materials/Fabrics/SofaChair2_Fabric_AlbedoTransparency",
        ["grey"]
    )
]

# Only used with sofa_3 and sofa_chair_3
SOFA_3_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Blue", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Blue_Light", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Brown_Pattern", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Green_Dark", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Green_Pattern", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_Red", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Sofa3_White_Pattern", ["white"])
]

# Only used with sofa_8
SOFA_8_MATERIALS = [
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat_BaseColor",
        ["red"]
    ),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3SeatDirt_BaseColor",
        ["red"]
    ),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2_BaseColor",
        ["brown"]
    ),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2D_BaseColor",
        ["brown"]
    )
]

# Only used with sofa_chair_8
SOFA_CHAIR_8_MATERIALS = [
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2_BaseColor",
        ["brown"]
    ),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2D_BaseColor",
        ["brown"]
    )
]

# Only used with sofa_9 and sofa_chair_9
SOFA_9_MATERIALS = [
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2Seat_BaseColor",
        ["red"]
    ),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2SeatD_BaseColor",
        ["brown"]
    )
]

# Only used with sofa_chair_4, sofa_chair_5, sofa_chair_6, and sofa_chair_7
ARMCHAIR_THORKEA_MATERIALS = [
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ekemas_Fabric_Mat",
        ["grey"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ektorp_Fabric_Mat",
        ["brown"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Emmabo_Fabric_Mat",
        ["blue"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Karlstad_Fabric_Mat",
        ["blue"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Overalt_Fabric_Mat",
        ["brown"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Tullsta_Fabric_Mat",
        ["white"]
    )
]

# Only used with sofa_4, sofa_5, sofa_6, and sofa_7
SOFA_THORKEA_MATERIALS = [
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Alrid_Fabric_Mat",
        ["grey"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Ektorp_Fabric_Mat",
        ["white"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Kramfors_Fabric_Mat",
        ["brown"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Solsta_Fabric_Mat",
        ["grey"]
    ),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Vreta_Fabric_Mat",
        ["white"]
    )
]

# For use with Rect and Hooked Tools
TOOL_MATERIALS = [
    MaterialTuple(
        "UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_13",
        ["grey"]
    ),
    MaterialTuple(
        "UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_15",
        ["brown"]
    ),
    MaterialTuple(
        "UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_34",
        ["pink"]
    ),
    MaterialTuple(
        "UnityAssetStore/YughuesFreeMetalMaterials/Materials/M_YFMM_36",
        ["green"]
    )
]


# Choose only ceramic, fabric, metal, and wood materials that aren't too shiny
# or have distracting patterns.
FLOOR_MATERIALS = [
    CARPET_2,
    CARPET_3,
    CARPET_4,
    CARPET_8,
    CARPET_DARK,
    CARPET_DARK_1,
    CARPET_DARK_GREEN,
    CARPET_GREEN,
    CARPET_WHITE,
    CARPET_WHITE_3,
    DARK_WOOD_2,
    DARK_WOOD_SMOOTH_2,
    LIGHT_WOOD_COUNTERS_1,
    TEXTURES_COM_WOOD_FINE_50_1_SEEMLESS,
    WORN_WOOD,
    KINDERGARTEN_BLUE_WOOD,
    KINDERGARTEN_RED_WOOD,
    KINDERGARTEN_GREEN_WOOD,
    KINDERGARTEN_YELLOW_WOOD,
    NURSERY_BROWN_WOOD
]

INTUITIVE_PHYSICS_BLOCK_MATERIALS = BLOCK_BLANK_MATERIALS.copy()

INTUITIVE_PHYSICS_METAL_MATERIALS = [
    BRASS_1,
    BROWN_METAL_1,
    BRUSHED_ALUMINUM_BLUE,
    BRUSHED_IRON_ALBEDO,
    GENERIC_STAINLESS_STEEL,
    HAMMERED_METAL_ALBEDO,
    METAL,
    NURSERY_CABINET_METAL
]

INTUITIVE_PHYSICS_PLASTIC_MATERIALS = [
    KINDERGARTEN_RED_PLASTIC,
    KINDERGARTEN_BLUE_PLASTIC,
    KINDERGARTEN_GREEN_PLASTIC,
    KINDERGARTEN_YELLOW_PLASTIC
]

INTUITIVE_PHYSICS_WOOD_MATERIALS = [
    DARK_WOOD_SMOOTH_2,
    LIGHT_WOOD_COUNTERS_1,
    LIGHT_WOOD_COUNTERS_3,
    LIGHT_WOOD_COUNTERS_4,
    WOOD_GRAIN_BROWN,
    WOOD_GRAIN_TAN,
    WORN_WOOD,
    KINDERGARTEN_BLUE_WOOD,
    KINDERGARTEN_RED_WOOD,
    KINDERGARTEN_GREEN_WOOD,
    KINDERGARTEN_YELLOW_WOOD,
    NURSERY_BROWN_WOOD
]

# Room and occluder walls in intuitive physics scenes cannot use reflective
# materials, like some ceramics, metals and woods, due to the glare.
INTUITIVE_PHYSICS_WALL_GROUPINGS = [WALL_MATERIALS + [
    BROWN_MARBLE_FAKE_1,
    CONCRETE_FLOOR,
    GREY_GRANITE,
    WHITE_COUNTERTOP,
    DARK_WOOD_SMOOTH_2,
    WORN_WOOD,
    KINDERGARTEN_BLUE_WOOD,
    KINDERGARTEN_RED_WOOD,
    KINDERGARTEN_GREEN_WOOD,
    KINDERGARTEN_YELLOW_WOOD
]]

ROOM_WALL_MATERIALS = CERAMIC_MATERIALS + METAL_MATERIALS + WALL_MATERIALS + \
    WOOD_MATERIALS
# Remove wall materials matching placer colors.
ROOM_WALL_MATERIALS = [item for item in ROOM_WALL_MATERIALS if (
    not item.material.startswith('Custom/Materials/Cyan') and
    not item.material.startswith('Custom/Materials/Magenta')
)]

FLAT_MATERIALS = [
    AZURE,
    BLACK,
    BLUE,
    BROWN,
    CHARTREUSE,
    CREAM,
    CYAN,
    DARKGREY,
    GOLDENROD,
    GREEN,
    GREY,
    INDIGO,
    LIME,
    MAGENTA,
    MAROON,
    NAVY,
    OLIVE,
    ORANGE,
    PINK,
    RED,
    ROSE,
    PURPLE,
    SPRINGGREEN,
    TAN,
    TEAL,
    VIOLET,
    WHITE,
    YELLOW
]


# Lists for all currently configurable materials, except for the lava.
ALL_CONFIGURABLE_MATERIAL_LIST_NAMES = [
    'ARMCHAIR_THORKEA_MATERIALS',
    'BLOCK_BLANK_MATERIALS',
    'BLOCK_LETTER_MATERIALS',
    'BLOCK_NUMBER_MATERIALS',
    'CARDBOARD_MATERIALS',
    'CERAMIC_MATERIALS',
    'FABRIC_MATERIALS',
    'LEATHER_MATERIALS',
    'LEATHER_ARMCHAIR_MATERIALS',
    'METAL_MATERIALS',
    'PLASTIC_MATERIALS',
    'RUBBER_MATERIALS',
    'WALL_MATERIALS',
    'WOOD_MATERIALS',
    'SOFA_1_MATERIALS',
    'SOFA_CHAIR_1_MATERIALS',
    'SOFA_2_MATERIALS',
    'SOFA_3_MATERIALS',
    'SOFA_8_MATERIALS',
    'SOFA_CHAIR_8_MATERIALS',
    'SOFA_9_MATERIALS',
    'SOFA_THORKEA_MATERIALS',
    'FLAT_MATERIALS'
]
ALL_CONFIGURABLE_MATERIAL_LISTS = [
    globals()[name] for name in ALL_CONFIGURABLE_MATERIAL_LIST_NAMES
]
ALL_CONFIGURABLE_MATERIAL_TUPLES = [
    item for list_item in ALL_CONFIGURABLE_MATERIAL_LISTS for item in list_item
]
ALL_CONFIGURABLE_MATERIAL_STRINGS = list(set([
    item.material for item in ALL_CONFIGURABLE_MATERIAL_TUPLES
]))
ALL_CONFIGURABLE_MATERIAL_LISTS_AND_STRINGS = (
    ALL_CONFIGURABLE_MATERIAL_LIST_NAMES + ALL_CONFIGURABLE_MATERIAL_STRINGS
)


# Lists for all materials that aren't restricted to specific shapes.
ALL_UNRESTRICTED_MATERIAL_LIST_NAMES = [
    'BLOCK_BLANK_MATERIALS',
    'CARDBOARD_MATERIALS',
    'CERAMIC_MATERIALS',
    'FABRIC_MATERIALS',
    'LEATHER_MATERIALS',
    'METAL_MATERIALS',
    'OBJECT_OPPOSITE_MATERIALS',
    'PLASTIC_MATERIALS',
    'RUBBER_MATERIALS',
    'WALL_OPPOSITE_MATERIALS',
    'WALL_MATERIALS',
    'WOOD_MATERIALS',
    'FLAT_MATERIALS'
]
ALL_UNRESTRICTED_MATERIAL_LISTS = [
    globals()[name] for name in ALL_UNRESTRICTED_MATERIAL_LIST_NAMES
]
ALL_UNRESTRICTED_MATERIAL_TUPLES = [
    item for list_item in ALL_UNRESTRICTED_MATERIAL_LISTS for item in list_item
]
ALL_UNRESTRICTED_MATERIAL_STRINGS = list(set([
    item.material for item in ALL_UNRESTRICTED_MATERIAL_TUPLES
]))
ALL_UNRESTRICTED_MATERIAL_LISTS_AND_STRINGS = (
    ALL_UNRESTRICTED_MATERIAL_LIST_NAMES + ALL_UNRESTRICTED_MATERIAL_STRINGS
)


# Ignore object-specific materials like letter/number blocks and sofas.
ALL_PRIMITIVE_MATERIAL_TUPLES = (
    BLOCK_BLANK_MATERIALS +
    CERAMIC_MATERIALS +
    FABRIC_MATERIALS +
    LEATHER_MATERIALS +
    METAL_MATERIALS +
    PLASTIC_MATERIALS +
    RUBBER_MATERIALS +
    WALL_MATERIALS +
    WOOD_MATERIALS +
    FLAT_MATERIALS
)


def filter_used_colors(
    possible_material_list: List[MaterialTuple],
    used_material_list: List[MaterialTuple]
) -> List[MaterialTuple]:
    """Return a subset of the given possible materials, excluding all materials
    that have the same colors as any of the used materials."""
    filtered_material_list = []
    for material in possible_material_list:
        excluded = False
        for used_material in used_material_list:
            if any([(c in used_material.color) for c in material.color]):
                excluded = True
                break
        if not excluded:
            filtered_material_list.append(material)
    return filtered_material_list


def find_colors(material_name: str, default_value: str = None) -> List[str]:
    for item in ALL_CONFIGURABLE_MATERIAL_TUPLES:
        if item.material == material_name:
            return item.color
    return default_value
