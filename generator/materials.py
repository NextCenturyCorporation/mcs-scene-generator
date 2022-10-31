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
BROWN = MaterialTuple("Custom/Materials/Brown", ["brown"])
CHARTREUSE = MaterialTuple(
    "Custom/Materials/Chartreuse", ["chartreuse", "green"])
CYAN = MaterialTuple("Custom/Materials/Cyan", ["cyan", "blue", "green"])
GOLDENROD = MaterialTuple(
    "Custom/Materials/Goldenrod", ["goldenrod", "yellow"])
GREEN = MaterialTuple("Custom/Materials/Green", ["green"])
GREY = MaterialTuple("Custom/Materials/Grey", ["grey"])
INDIGO = MaterialTuple("Custom/Materials/Indigo", ["indigo", "blue"])
LIME = MaterialTuple("Custom/Materials/Lime", ["lime", "green"])
MAGENTA = MaterialTuple("Custom/Materials/Magenta", ["magenta", "purple"])
MAROON = MaterialTuple("Custom/Materials/Maroon", ["maroon", "red"])
NAVY = MaterialTuple("Custom/Materials/Navy", ["navy", "blue"])
OLIVE = MaterialTuple("Custom/Materials/Olive", ["olive", "green"])
ORANGE = MaterialTuple("Custom/Materials/Orange", ["orange"])
PINK = MaterialTuple("Custom/Materials/Pink", ["pink", "red"])
RED = MaterialTuple("Custom/Materials/Red", ["red"])
ROSE = MaterialTuple("Custom/Materials/Rose", ["rose", "red"])
PURPLE = MaterialTuple("Custom/Materials/Purple", ["purple"])
SPRINGGREEN = MaterialTuple(
    "Custom/Materials/SpringGreen", ["springgreen", "green"])
TAN = MaterialTuple("Custom/Materials/Tan", ["brown"])
TEAL = MaterialTuple("Custom/Materials/Teal", ["teal", "blue", "green"])
VIOLET = MaterialTuple("Custom/Materials/Violet", ["violet", "purple"])
WHITE = MaterialTuple("Custom/Materials/White", ["white"])
YELLOW = MaterialTuple("Custom/Materials/Yellow", ["yellow"])

# Only colors that are exact opposites of one another (uses RGB color wheel).
# Only use bright colors with max saturation/value in this specific list.
OPPOSITE_MATERIALS = [
    AZURE,
    BLUE,
    CHARTREUSE,
    CYAN,
    LIME,
    MAGENTA,
    ORANGE,
    RED,
    ROSE,
    SPRINGGREEN,
    VIOLET,
    YELLOW
]

OPPOSITE_SETS = {
    "Custom/Materials/Azure": ORANGE,
    "Custom/Materials/Black": WHITE,
    "Custom/Materials/Blue": YELLOW,
    "Custom/Materials/Chartreuse": VIOLET,
    "Custom/Materials/Cyan": RED,
    "Custom/Materials/Goldenrod": INDIGO,  # Not an official opposite
    "Custom/Materials/Green": PURPLE,
    "Custom/Materials/Indigo": GOLDENROD,  # Not an official opposite
    "Custom/Materials/Lime": MAGENTA,
    "Custom/Materials/Magenta": LIME,
    "Custom/Materials/Maroon": TEAL,
    "Custom/Materials/Navy": OLIVE,
    "Custom/Materials/Olive": NAVY,
    "Custom/Materials/Orange": AZURE,
    "Custom/Materials/Purple": GREEN,
    "Custom/Materials/Red": CYAN,
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
    CYAN,
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

_CUSTOM_CARPET_MATERIALS = [
    MaterialTuple(item.material + 'CarpetMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

_CUSTOM_DRYWALL_MATERIALS = [
    MaterialTuple(item.material + 'DrywallMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

_CUSTOM_WOOD_MATERIALS = [
    MaterialTuple(item.material + 'WoodMCS', item.color)
    for item in _CUSTOM_MATERIALS
]

BLOCK_BLANK_MATERIALS = [
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1",
                  ["grey"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1",
                  ["brown"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1",
                  ["yellow"])
]

BLOCK_LETTER_MATERIALS = [
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_A_Blue_1K/ToyBlockBlueA",
                  ["blue", "brown"]),
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_B_Blue_1K/ToyBlockBlueB",
                  ["blue", "brown"]),
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC",
                  ["blue", "brown"]),
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_D_Blue_1K/ToyBlockBlueD",
                  ["blue", "brown"]),
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM",
                  ["blue", "brown"]),
    MaterialTuple("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS",
                  ["blue", "brown"])
]

BLOCK_NUMBER_MATERIALS = [
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1",
                  ["yellow", "brown"]),
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2",
                  ["yellow", "brown"]),
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3",
                  ["yellow", "brown"]),
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_4_Yellow_1K/NumberBlockYellow_4",
                  ["yellow", "brown"]),
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_5_Yellow_1K/NumberBlockYellow_5",
                  ["yellow", "brown"]),
    MaterialTuple("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_6_Yellow_1K/NumberBlockYellow_6",
                  ["yellow", "brown"])
]

CARDBOARD_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_Tan", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Misc/Cardboard_White", ["grey"])
]

CERAMIC_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Ceramics/BrownMarbleFake 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/ConcreteBoards1", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/ConcreteFloor", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/GREYGRANITE", ["grey"]),
    MaterialTuple(
        "AI2-THOR/Materials/Ceramics/PinkConcrete_Bedroom1", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/WhiteCountertop", ["grey"])
    # Don't use the brick or cobblestone textures.
]

FABRIC_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet2", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet3", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet4", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet8", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDark", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDark 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDarkGreen", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetGreen", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite 3", ["white"])
    # Don't use highly patterned multicolor carpet textures.
] + _CUSTOM_CARPET_MATERIALS

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
        ["brown"]),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_2",
        ["grey"]),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_3",
        ["brown"]),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_4",
        ["grey"]),
    MaterialTuple(
        "UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_normal_OLD",
        ["brown"])

]

METAL_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Metals/BlackSmoothMeta", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Metals/Brass 1", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Metals/BrownMetal 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Metals/BrushedAluminum_Blue", ["blue"]),
    MaterialTuple(
        "AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Metals/GenericStainlessSteel", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1",
                  ["green"]),
    MaterialTuple("AI2-THOR/Materials/Metals/Metal", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Metals/WhiteMetal", ["white"]),
    MaterialTuple(
        "UnityAssetStore/Baby_Room/Models/Materials/cabinet metal", ["grey"])
]

PLASTIC_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Plastics/BlackPlastic", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Plastics/OrangePlastic", ["orange"]),
    MaterialTuple("AI2-THOR/Materials/Plastics/WhitePlastic", ["white"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4",
                  ["yellow"])
]

RUBBER_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Plastics/BlueRubber", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Plastics/LightBlueRubber", ["blue"])
]

CEILING_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall4Tiled", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/DrywallBeige", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall", ["white"])]

WALL_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Walls/BrownDrywall", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/DrywallBeige", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/DrywallGreen", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Walls/DrywallOrange", ["orange"]),
    MaterialTuple("AI2-THOR/Materials/Walls/Drywall4Tiled", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Walls/EggshellDrywall", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Walls/RedDrywall", ["red"]),
    MaterialTuple("AI2-THOR/Materials/Walls/WallDrywallGrey", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Walls/YellowDrywall", ["yellow"])
] + _CUSTOM_DRYWALL_MATERIALS

WOOD_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Wood/BedroomFloor1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/BlackWood", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWood2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWoodSmooth2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters3", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters4", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S",
                  ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WhiteWood", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodFloorsCross", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Tan", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WornWood", ["brown"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4",
                  ["yellow"]),
    MaterialTuple(
        "UnityAssetStore/Baby_Room/Models/Materials/wood 1", ["brown"])
] + _CUSTOM_WOOD_MATERIALS

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
        "AI2-THOR/Materials/Fabrics/SofaChair2_Fabric_AlbedoTransparency", ["grey"])
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
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat_BaseColor", ["red"]),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3SeatDirt_BaseColor", ["red"]),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2_BaseColor", ["brown"]),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2D_BaseColor", ["brown"])
]

# Only used with sofa_chair_8
SOFA_CHAIR_8_MATERIALS = [
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2_BaseColor", ["brown"]),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2D_BaseColor", ["brown"])
]

# Only used with sofa_9 and sofa_chair_9
SOFA_9_MATERIALS = [
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2Seat_BaseColor", ["red"]),
    MaterialTuple(
        "Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2SeatD_BaseColor", ["brown"])
]

# Only used with sofa_chair_4, sofa_chair_5, sofa_chair_6, and sofa_chair_7
ARMCHAIR_THORKEA_MATERIALS = [
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ekemas_Fabric_Mat", ["grey"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ektorp_Fabric_Mat", ["brown"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Emmabo_Fabric_Mat", ["blue"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Karlstad_Fabric_Mat", ["blue"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Overalt_Fabric_Mat", ["brown"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Tullsta_Fabric_Mat", ["white"])
]

# Only used with sofa_4, sofa_5, sofa_6, and sofa_7
SOFA_THORKEA_MATERIALS = [
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Alrid_Fabric_Mat", ["grey"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Ektorp_Fabric_Mat", ["white"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Kramfors_Fabric_Mat", ["brown"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Solsta_Fabric_Mat", ["grey"]),
    MaterialTuple(
        "AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Vreta_Fabric_Mat", ["white"])
]

# Choose only ceramic, fabric, metal, and wood materials that aren't too shiny
# or have distracting patterns.
FLOOR_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet2", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet3", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet4", ["blue"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/Carpet8", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDark", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDark 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetDarkGreen", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetGreen", ["green"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Fabrics/CarpetWhite 3", ["white"]),
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWood2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWoodSmooth2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S",
                  ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WornWood", ["brown"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4",
                  ["yellow"]),
    MaterialTuple(
        "UnityAssetStore/Baby_Room/Models/Materials/wood 1", ["brown"])
]

INTUITIVE_PHYSICS_BLOCK_MATERIALS = [
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1",
                  ["grey"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1",
                  ["brown"]),
    MaterialTuple("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1",
                  ["yellow"])
]

INTUITIVE_PHYSICS_METAL_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Metals/Brass 1", ["yellow"]),
    MaterialTuple("AI2-THOR/Materials/Metals/BrownMetal 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Metals/BrushedAluminum_Blue", ["blue"]),
    MaterialTuple(
        "AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Metals/GenericStainlessSteel", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1",
                  ["green"]),
    MaterialTuple("AI2-THOR/Materials/Metals/Metal", ["grey"]),
    MaterialTuple(
        "UnityAssetStore/Baby_Room/Models/Materials/cabinet metal", ["grey"])
]

INTUITIVE_PHYSICS_PLASTIC_MATERIALS = [
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4",
                  ["yellow"])
]

INTUITIVE_PHYSICS_WOOD_MATERIALS = [
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWoodSmooth2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters3", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/LightWoodCounters4", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Brown", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WoodGrain_Tan", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WornWood", ["brown"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4",
                  ["yellow"]),
    MaterialTuple(
        "UnityAssetStore/Baby_Room/Models/Materials/wood 1", ["brown"])
]

# Room and occluder walls in intuitive physics scenes cannot use reflective
# materials, like some ceramics, metals and woods, due to the glare.
INTUITIVE_PHYSICS_WALL_GROUPINGS = [WALL_MATERIALS + [
    MaterialTuple("AI2-THOR/Materials/Ceramics/BrownMarbleFake 1", ["brown"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/ConcreteFloor", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/GREYGRANITE", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Ceramics/WhiteCountertop", ["grey"]),
    MaterialTuple("AI2-THOR/Materials/Wood/DarkWoodSmooth2", ["black"]),
    MaterialTuple("AI2-THOR/Materials/Wood/WornWood", ["brown"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1",
                  ["blue"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2",
                  ["red"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3",
                  ["green"]),
    MaterialTuple("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4",
                  ["yellow"]),
]]

ROOM_WALL_MATERIALS = CERAMIC_MATERIALS + METAL_MATERIALS + WALL_MATERIALS + \
    WOOD_MATERIALS

FLAT_MATERIALS = [
    AZURE,
    BLACK,
    BLUE,
    BROWN,
    CHARTREUSE,
    CYAN,
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
    'OPPOSITE_MATERIALS',
    'PLASTIC_MATERIALS',
    'RUBBER_MATERIALS',
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


def find_colors(material_name: str, default_value: str = None) -> List[str]:
    for item in ALL_CONFIGURABLE_MATERIAL_TUPLES:
        if item.material == material_name:
            return item.color
    return default_value
