import copy
from enum import Enum
from typing import Any, Dict, List, Union


def _create_size_option(
    size_multiplier: float,
    size_text: str,
    base_dict: Dict[str, float],
    is_untrained: bool = False
) -> Dict[str, Any]:
    return {
        'dimensions': {
            'x': base_dict['dimensions']['x'] * size_multiplier,
            'y': base_dict['dimensions']['y'] * size_multiplier,
            'z': base_dict['dimensions']['z'] * size_multiplier
        },
        'mass': base_dict['mass'] * size_multiplier,
        'positionY': base_dict['positionY'] * size_multiplier,
        'scale': {
            'x': base_dict['scale']['x'] * size_multiplier,
            'y': base_dict['scale']['y'] * size_multiplier,
            'z': base_dict['scale']['z'] * size_multiplier
        },
        'size': size_text,
        'untrainedSize': is_untrained
    }


_SOCCER_BALL = {
    "type": "soccer_ball",
    "color": ["white", "black"],
    "shape": ["ball"],
    "size": "small",
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.22,
        "y": 0.22,
        "z": 0.22
    },
    "mass": 1,
    "offset": {
        "x": 0,
        "y": 0.11,
        "z": 0
    },
    "positionY": 0.005,
    "salientMaterials": ["rubber"],
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_TROPHY = {
    "type": "trophy",
    "color": ["grey"],
    "shape": ["trophy"],
    "size": "small",
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.19,
        "y": 0.3,
        "z": 0.14
    },
    "mass": 1,
    "offset": {
        "x": 0,
        "y": 0.15,
        "z": 0
    },
    "positionY": 0.005,
    "salientMaterials": ["metal"],
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    },
    "sideways": {
        "dimensions": {
            "x": 0.19,
            "y": 0.14,
            "z": 0.3
        },
        "offset": {
            "x": 0,
            "y": 0,
            "z": 0.15
        },
        "positionY": 0.075,
        "rotation": {
            "x": 90,
            "y": 0,
            "z": 0
        }
    }
}


_CAKE = {
    "type": "cake",
    "color": ["brown"],
    "shape": ["cake"],
    "size": "small",
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.22 * 2,
        "y": 0.1 * 2,
        "z": 0.22 * 2
    },
    "mass": 2,
    "offset": {
        "x": 0,
        "y": 0.05 * 2,
        "z": 0
    },
    "positionY": 0.005,
    "materialCategory": [],
    "salientMaterials": ["food"],
    "scale": {
        "x": 2,
        "y": 2,
        "z": 2
    }
}


_BALL = {
    "type": "ball",
    "shape": ["ball"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.025,
            "y": 0.025,
            "z": 0.025
        },
        "mass": 0.125,
        "positionY": 0.0125,
        "scale": {
            "x": 0.025,
            "y": 0.025,
            "z": 0.025
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.05,
            "y": 0.05,
            "z": 0.05,
        },
        "mass": 0.25,
        "positionY": 0.025,
        "scale": {
            "x": 0.05,
            "y": 0.05,
            "z": 0.05
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.5,
        "positionY": 0.05,
        "scale": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        },
        "mass": 1,
        "positionY": 0.125,
        "scale": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        }
    }]
}


_BLOCK_BLANK_CUBE = {
    "type": "block_blank_wood_cube",
    "shape": ["blank block", "cube"],
    "attributes": ["moveable", "pickupable", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.2,
            "z": 0.1
        },
        "mass": 1.33,
        "offset": {
            "x": 0,
            "y": 0.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 2,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.2,
            "y": 0.1,
            "z": 0.2
        },
        "mass": 2.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_BLOCK_BLANK_CYLINDER = {
    "type": "block_blank_wood_cylinder",
    "shape": ["blank block", "cylinder"],
    "attributes": ["moveable", "pickupable", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.2,
            "z": 0.1
        },
        "mass": 1.33,
        "offset": {
            "x": 0,
            "y": 0.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 2,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.2,
            "y": 0.1,
            "z": 0.2
        },
        "mass": 2.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_BLOCK_LETTER = {
    # Readers, please ignore the "blue letter c" in the type: the object's
    # chosen material will change this design.
    "type": "block_blue_letter_c",
    "shape": ["letter block", "cube"],
    "size": "tiny",
    "mass": 0.66,
    "materialCategory": ["block_letter"],
    "salientMaterials": ["wood"],
    "attributes": ["moveable", "pickupable", "stackTarget", "occluder"],
    "dimensions": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BLOCK_NUMBER = {
    # Readers, please ignore the "yellow number 1" in the type: the object's
    # chosen material will change this design.
    "type": "block_yellow_number_1",
    "shape": ["number block", "cube"],
    "size": "tiny",
    "mass": 0.66,
    "materialCategory": ["block_number"],
    "salientMaterials": ["wood"],
    "attributes": ["moveable", "pickupable", "stackTarget", "occluder"],
    "dimensions": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_DUCK_ON_WHEELS = {
    "type": "duck_on_wheels",
    "shape": ["duck"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.105,
            "y": 0.085,
            "z": 0.0325
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.0425,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.21,
            "y": 0.17,
            "z": 0.065
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.085,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.42,
            "y": 0.34,
            "z": 0.13
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.17,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_TOY_RACECAR = {
    "type": "racecar_red",
    "shape": ["car"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.0525,
            "y": 0.045,
            "z": 0.1125
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.0225,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.105,
            "y": 0.09,
            "z": 0.225
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.045,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.21,
            "y": 0.18,
            "z": 0.45
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.09,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }]
}


_PACIFIER = {
    "type": "pacifier",
    "shape": ["pacifier"],
    "size": "tiny",
    "color": ["blue"],
    "mass": 0.125,
    "materialCategory": [],
    "salientMaterials": ["plastic"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.07,
        "y": 0.04,
        "z": 0.05
    },
    "offset": {
        "x": 0,
        "y": 0.02,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CRAYON = {
    "chooseMaterial": [{
        # TODO
        "type": "crayon_blue",
        "color": ["blue"]
    }],
    "shape": ["crayon"],
    "size": "tiny",
    "mass": 0.125,
    "materialCategory": [],
    "salientMaterials": ["wax"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.01,
        "y": 0.085,
        "z": 0.01
    },
    "offset": {
        "x": 0,
        "y": 0.0425,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_TURTLE_ON_WHEELS = {
    "type": "turtle_on_wheels",
    "shape": ["turtle"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.24 * 0.5,
            "y": 0.14 * 0.5,
            "z": 0.085 * 0.5
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.07 * 0.5,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.24,
            "y": 0.14,
            "z": 0.085
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.07,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.24 * 2,
            "y": 0.14 * 2,
            "z": 0.085 * 2
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.07 * 2,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_TOY_CAR = {
    "type": "car_1",
    "shape": ["car"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.075 * 0.75,
            "y": 0.065 * 0.75,
            "z": 0.14 * 0.75
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.03 * 0.75,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.075 * 1.5,
            "y": 0.065 * 1.5,
            "z": 0.14 * 1.5
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.03 * 1.5,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.075 * 3,
            "y": 0.065 * 3,
            "z": 0.14 * 3
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.03 * 3,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }]
}


_APPLE = {
    "chooseType": [{
        "type": "apple_1",
        "color": ["red"],
        "dimensions": {
            "x": 0.111,
            "y": 0.12,
            "z": 0.122
        },
        "offset": {
            "x": 0,
            "y": 0.005,
            "z": 0
        }
    }, {
        "type": "apple_2",
        "color": ["green"],
        "dimensions": {
            "x": 0.117,
            "y": 0.121,
            "z": 0.116
        },
        "offset": {
            "x": 0,
            "y": 0.002,
            "z": 0
        }
    }],
    "shape": ["apple"],
    "size": "tiny",
    "mass": 0.5,
    "materialCategory": [],
    "salientMaterials": ["food"],
    "attributes": ["moveable", "pickupable"],
    "positionY": 0.03,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BOWL = {
    "chooseType": [{
        "type": "bowl_3",
        "dimensions": {
            "x": 0.175,
            "y": 0.116,
            "z": 0.171
        },
        "offset": {
            "x": 0,
            "y": 0.055,
            "z": 0
        }
    }, {
        "type": "bowl_4",
        "dimensions": {
            "x": 0.209,
            "y": 0.059,
            "z": 0.206
        },
        "offset": {
            "x": 0,
            "y": 0.027,
            "z": 0
        },
    }, {
        "type": "bowl_6",
        "dimensions": {
            "x": 0.198,
            "y": 0.109,
            "z": 0.201
        },
        "offset": {
            "x": 0,
            "y": 0.052,
            "z": 0
        }
    }],
    "shape": ["bowl"],
    "size": "tiny",
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CUP = {
    "chooseType": [{
        "type": "cup_2",
        "dimensions": {
            "x": 0.105,
            "y": 0.135,
            "z": 0.104
        },
        "offset": {
            "x": 0,
            "y": 0.064,
            "z": 0
        }
    }, {
        "type": "cup_3",
        "dimensions": {
            "x": 0.123,
            "y": 0.149,
            "z": 0.126
        },
        "offset": {
            "x": 0,
            "y": 0.072,
            "z": 0
        }
    }, {
        "type": "cup_6",
        "dimensions": {
            "x": 0.106,
            "y": 0.098,
            "z": 0.106
        },
        "offset": {
            "x": 0,
            "y": 0.046,
            "z": 0
        }
    }],
    "shape": ["cup"],
    "size": "tiny",
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_PLATE = {
    "chooseType": [{
        "type": "plate_1",
        "dimensions": {
            "x": 0.208,
            "y": 0.117,
            "z": 0.222
        },
        "offset": {
            "x": 0,
            "y": 0.057,
            "z": 0
        }
    }, {
        "type": "plate_3",
        "dimensions": {
            "x": 0.304,
            "y": 0.208,
            "z": 0.305
        },
        "offset": {
            "x": 0,
            "y": 0.098,
            "z": 0
        }
    }, {
        "type": "plate_4",
        "dimensions": {
            "x": 0.202,
            "y": 0.113,
            "z": 0.206
        },
        "offset": {
            "x": 0,
            "y": 0.053,
            "z": 0
        },
    }],
    "shape": ["plate"],
    "size": "tiny",
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BOOKCASE = {
    "shape": ["shelf"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseType": [{
        "type": "bookcase_1_shelf",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1,
            "y": 1,
            "z": 0.5
        },
        "mass": 6,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 2,
            "z": 0.5
        },
        "mass": 18,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 24,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_1_shelf",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 1,
            "z": 0.5
        },
        "mass": 3,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 6,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 2,
            "z": 0.5
        },
        "mass": 9,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_1_shelf",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 1,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 24,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 2,
            "z": 0.5
        },
        "mass": 36,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 48,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }]
}


_BOOKCASE_SIDELESS = {
    "shape": ["shelf"],
    "attributes": ["receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseType": [{
        "type": "bookcase_1_shelf_sideless",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1,
            "y": 1,
            "z": 0.5
        },
        "mass": 6,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf_sideless",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 2,
            "z": 0.5
        },
        "mass": 18,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 24,
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_1_shelf_sideless",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 1,
            "z": 0.5
        },
        "mass": 3,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf_sideless",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 6,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 2,
            "z": 0.5
        },
        "mass": 9,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 0.5,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 0.5,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_1_shelf_sideless",
        "size": "medium",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 1,
            "z": 0.5
        },
        "mass": 12,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_2_shelf_sideless",
        "size": "large",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 1.5,
            "z": 0.5
        },
        "mass": 24,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_3_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 2,
            "z": 0.5
        },
        "mass": 36,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "bookcase_4_shelf_sideless",
        "size": "huge",
        "openAreas": [{
            "id": "bottom",
            "position": {
                "x": 0,
                "y": 0.04,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
        }, {
            "id": "shelf_1",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 2,
                "y": 0,
                "z": 0.25
            }
            # }, {
            #     "id": "shelf_2",
            #     "position": {
            #         "x": 0,
            #         "y": 1.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_3",
            #     "position": {
            #         "x": 0,
            #         "y": 1.52,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
            # }, {
            #     "id": "shelf_4",
            #     "position": {
            #         "x": 0,
            #         "y": 2.02,
            #         "z": 0
            #     },
            #     "dimensions": {
            #         "x": 0.5 * 2,
            #         "y": 0,
            #         "z": 0.25
            #     }
        }],
        "dimensions": {
            "x": 1 * 2,
            "y": 2.5,
            "z": 0.5
        },
        "mass": 48,
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 1
        }
    }]
}


_CART = {
    "type": "cart_1",
    "shape": ["cart"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "materialCategory": ["metal"],
    "salientMaterials": ["metal"],
    "chooseSize": [{
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.34 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.38 * 0.5,
                "y": 0,
                "z": 0.38 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.725 * 0.5,
            "y": 1.29 * 0.5,
            "z": 0.55 * 0.5
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.645 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.34,
                "z": 0
            },
            "dimensions": {
                "x": 0.38,
                "y": 0,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.725,
            "y": 1.29,
            "z": 0.55
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.645,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_CHAIR_1_NORMAL_BABY_SIZE = {
    "type": "chair_1",
    "shape": ["chair"],
    "attributes": ["pickupable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseSize": [{
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 0.33,
                "y": 0.5 * 0.33,
                "z": -0.02 * 0.33
            },
            "dimensions": {
                "x": 0.38 * 0.33,
                "y": 0,
                "z": 0.38 * 0.33
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.33,
            "y": 1.04 * 0.33,
            "z": 0.46 * 0.33
        },
        "mass": 0.5,
        "offset": {
            "x": 0,
            "y": 0.51 * 0.33,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.33,
            "y": 0.33,
            "z": 0.33
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 0.5,
                "y": 0.5 * 0.5,
                "z": -0.02 * 0.5
            },
            "dimensions": {
                "x": 0.38 * 0.5,
                "y": 0,
                "z": 0.38 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.5,
            "y": 1.04 * 0.5,
            "z": 0.46 * 0.5
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.51 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 0.66,
                "y": 0.5 * 0.66,
                "z": -0.02 * 0.66
            },
            "dimensions": {
                "x": 0.38 * 0.66,
                "y": 0,
                "z": 0.38 * 0.66
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.66,
            "y": 1.04 * 0.66,
            "z": 0.46 * 0.66
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.51 * 0.66,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.66,
            "y": 0.66,
            "z": 0.66
        }
    }]
}


_CHAIR_1_NORMAL = {
    "type": "chair_1",
    "shape": ["chair"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01,
                "y": 0.5,
                "z": -0.02
            },
            "dimensions": {
                "x": 0.38,
                "y": 0,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.54,
            "y": 1.04,
            "z": 0.46
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.51,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 0.75,
                "y": 0.5 * 0.75,
                "z": -0.02 * 0.75
            },
            "dimensions": {
                "x": 0.38 * 0.75,
                "y": 0,
                "z": 0.38 * 0.75
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.75,
            "y": 1.04 * 0.75,
            "z": 0.46 * 0.75
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.51 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 1.25,
                "y": 0.5 * 1.25,
                "z": -0.02 * 1.25
            },
            "dimensions": {
                "x": 0.38 * 1.25,
                "y": 0,
                "z": 0.38 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.54 * 1.25,
            "y": 1.04 * 1.25,
            "z": 0.46 * 1.25
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.51 * 1.25,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1.25,
            "z": 1.25
        }
    }]
}


_CHAIR_2_STOOL_CIRCLE_BABY_SIZE = {
    "type": "chair_2",
    "shape": ["stool"],
    "attributes": ["pickupable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.2 * 0.25,
                "y": 0,
                "z": 0.2 * 0.25
            }
        }],
        "mass": 0.5,
        "dimensions": {
            "x": 0.3 * 0.25,
            "y": 0.75 * 0.5,
            "z": 0.3 * 0.25
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.25,
            "y": 0.5,
            "z": 0.25
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.2 * 0.5,
                "y": 0,
                "z": 0.2 * 0.5
            }
        }],
        "mass": 1,
        "dimensions": {
            "x": 0.3 * 0.5,
            "y": 0.75 * 0.5,
            "z": 0.3 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.2 * 0.75,
                "y": 0,
                "z": 0.2 * 0.75
            }
        }],
        "mass": 2,
        "dimensions": {
            "x": 0.3 * 0.75,
            "y": 0.75 * 0.5,
            "z": 0.3 * 0.75
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.5,
            "z": 0.75
        }
    }]
}


_CHAIR_2_STOOL_CIRCLE = {
    "type": "chair_2",
    "shape": ["stool"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.2,
                "y": 0,
                "z": 0.2
            }
        }],
        "dimensions": {
            "x": 0.3,
            "y": 0.75,
            "z": 0.3
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.375,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.2,
                "y": 0,
                "z": 0.2
            }
        }],
        "mass": 3,
        "dimensions": {
            "x": 0.3,
            "y": 0.75 * 0.75,
            "z": 0.3
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.75,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.2 * 0.75,
                "y": 0,
                "z": 0.2 * 0.75
            }
        }],
        "mass": 2,
        "dimensions": {
            "x": 0.3 * 0.75,
            "y": 0.75 * 0.75,
            "z": 0.3 * 0.75
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }]
}


_CHAIR_3_STOOL_RECT = {
    "type": "chair_3",
    "shape": ["stool"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 1.3 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.3 * 0.75,
                "y": 0,
                "z": 0.6 * 0.75
            }
        }],
        "mass": 9,
        "dimensions": {
            "x": 0.42 * 0.75,
            "y": 0.8 * 0.75,
            "z": 0.63 * 0.75
        },
        "offset": {
            "x": 0,
            "y": 0.4 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 1.3 * 0.667,
                "z": 0
            },
            "dimensions": {
                "x": 0.3 * 0.667,
                "y": 0,
                "z": 0.6 * 0.667
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 0.42 * 0.667,
            "y": 0.8 * 0.667,
            "z": 0.63 * 0.667
        },
        "offset": {
            "x": 0,
            "y": 0.4 * 0.667,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.667,
            "y": 0.667,
            "z": 0.667
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 1.3 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.3 * 0.5,
                "y": 0,
                "z": 0.6 * 0.5
            }
        }],
        "mass": 3,
        "dimensions": {
            "x": 0.42 * 0.5,
            "y": 0.8 * 0.5,
            "z": 0.63 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.4 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_CHAIR_4_OFFICE = {
    "type": "chair_4",
    "shape": ["chair"],
    "attributes": ["moveable", "receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": -0.01 * 1.1,
                "y": 1.06 * 1.1,
                "z": 0.015 * 1.1
            },
            "dimensions": {
                "x": 0.32 * 1.1,
                "y": 0,
                "z": 0.32 * 1.1
            }
        }],
        "dimensions": {
            "x": 0.54 * 1.1,
            "y": 0.88 * 1.1,
            "z": 0.44 * 1.1
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.44 * 1.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.1,
            "y": 1.1,
            "z": 1.1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": -0.01 * 0.9,
                "y": 1.06 * 0.9,
                "z": 0.015 * 0.9
            },
            "dimensions": {
                "x": 0.32 * 0.9,
                "y": 0,
                "z": 0.32 * 0.9
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.9,
            "y": 0.88 * 0.9,
            "z": 0.44 * 0.9
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.9,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": -0.01 * 0.7,
                "y": 1.06 * 0.7,
                "z": 0.015 * 0.7
            },
            "dimensions": {
                "x": 0.32 * 0.7,
                "y": 0,
                "z": 0.32 * 0.7
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.7,
            "y": 0.88 * 0.7,
            "z": 0.44 * 0.7
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.7,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }]
}


_BLOCK_BLANK_CUBE_NOT_PICKUPABLE = {
    "type": "block_blank_wood_cube",
    "shape": ["blank block", "cube"],
    "size": "small",
    "attributes": ["moveable", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "mass": 5,
    "offset": {
        "x": 0,
        "y": 0.125,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 2.5,
        "y": 2.5,
        "z": 2.5
    }
}


_BLOCK_BLANK_CYLINDER_NOT_PICKUPABLE = {
    "type": "block_blank_wood_cylinder",
    "shape": ["blank block", "cylinder"],
    "size": "small",
    "attributes": ["moveable", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "mass": 5,
    "offset": {
        "x": 0,
        "y": 0.125,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 2.5,
        "y": 2.5,
        "z": 2.5
    }
}


_CHANGING_TABLE = {
    "type": "changing_table",
    "shape": ["changing table"],
    "size": "huge",
    "mass": 50,
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "attributes": ["receptacle", "openable", "occluder"],
    "enclosedAreas": [{
        # Remove the top drawer for now.
        #        "id": "_drawer_top",
        #        "position": {
        #            "x": 0.165,
        #            "y": 0.47,
        #            "z": -0.03
        #        },
        #        "dimensions": {
        #            "x": 0.68,
        #            "y": 0.22,
        #            "z": 0.41
        #            }
        #    }, {
        "id": "_drawer_bottom",
        "position": {
            "x": 0.175,
            "y": 0.19,
            "z": -0.03
        },
        "dimensions": {
            "x": 0.68,
            "y": 0.2,
            "z": 0.41
        }
    }],
    "openAreas": [{
        # Remove the top shelves for now.
        #        "id": "",
        #        "position": {
        #            "x": 0,
        #            "y": 0.85,
        #            "z": 0
        #        },
        #        "dimensions": {
        #            "x": 1,
        #            "y": 0,
        #            "z": 0.55
        #            }
        #    }, {
        #        "id": "_shelf_top",
        #        "position": {
        #            "x": 0,
        #            "y": 0.725,
        #            "z": -0.05
        #        },
        #        "dimensions": {
        #            "x": 1.05,
        #            "y": 0.2,
        #            "z": 0.44
        #            }
        #    }, {
        #        "id": "_shelf_middle",
        #        "position": {
        #            "x": -0.365,
        #            "y": 0.475,
        #            "z": -0.05
        #        },
        #        "dimensions": {
        #            "x": 0.32,
        #            "y": 0.25,
        #            "z": 0.44
        #            }
        #    }, {
        "id": "_shelf_bottom",
        "position": {
            "x": -0.365,
            "y": 0.2,
            "z": -0.05
        },
        "dimensions": {
            "x": 0.32,
            "y": 0.25,
            "z": 0.44
        }
    }],
    "dimensions": {
        "x": 1.1,
        "y": 0.96,
        "z": 0.89
    },
    "offset": {
        "x": 0,
        "y": 0.48,
        "z": 0.155
    },
    "closedDimensions": {
        "x": 1.1,
        "y": 0.96,
        "z": 0.58
    },
    "closedOffset": {
        "x": 0,
        "y": 0.48,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CRIB = {
    "type": "crib",
    "shape": ["crib"],
    "size": "huge",
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "mass": 10,
    "attributes": [],
    "dimensions": {
        "x": 0.65,
        "y": 0.9,
        "z": 1.25
    },
    "offset": {
        "x": 0,
        "y": 0.45,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_TABLE_1_RECT_BABY_SIZE = {
    "type": "table_1",
    "shape": ["table"],
    "attributes": ["pickupable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.5,
                "z": -0.07 * 0.5
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.5,
            "z": 1.63 * 0.5
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.33,
                "z": -0.07 * 0.5
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.33,
            "z": 1.63 * 0.5
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.33,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.33,
            "z": 0.5
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.5,
                "z": -0.07 * 0.25
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.25
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.5,
            "z": 1.63 * 0.25
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.5,
            "z": 0.25
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.33,
                "z": -0.07 * 0.25
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.25
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.33,
            "z": 1.63 * 0.25
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.33,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.33,
            "z": 0.25
        }
    }]
}


_TABLE_1_RECT_ACCESSIBLE = {
    "type": "table_1",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.5,
                "z": -0.07 * 0.5
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.5,
            "z": 1.63 * 0.5
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 1.175,
                "y": 0.88 * 0.5,
                "z": -0.07 * 0.5
            },
            "dimensions": {
                "x": 0.68 * 1.175,
                "y": 0,
                "z": 1.62 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.69 * 1.175,
            "y": 0.88 * 0.5,
            "z": 1.63 * 0.5
        },
        "mass": 6,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.175,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 1.175,
                "y": 0.88 * 0.5,
                "z": -0.07
            },
            "dimensions": {
                "x": 0.68 * 1.175,
                "y": 0,
                "z": 1.62
            }
        }],
        "dimensions": {
            "x": 0.69 * 1.175,
            "y": 0.88 * 0.5,
            "z": 1.63
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.175,
            "y": 0.5,
            "z": 1
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 2.35,
                "y": 0.88 * 0.5,
                "z": -0.07
            },
            "dimensions": {
                "x": 0.68 * 2.35,
                "y": 0,
                "z": 1.62
            }
        }],
        "dimensions": {
            "x": 0.69 * 2.35,
            "y": 0.88 * 0.5,
            "z": 1.63
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.44 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.35,
            "y": 0.5,
            "z": 1
        }
    }]
}


_TABLE_1_RECT_INACCESSIBLE = {
    "type": "table_1",
    "shape": ["table"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 0.5875,
        #                "y": 0.88,
        #                "z": -0.07 * 0.5
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 0.5875,
        #                "y": 0,
        #                "z": 1.62 * 0.5
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88,
            "z": 1.63 * 0.5
        },
        "mass": 6,
        "offset": {
            "x": 0,
            "y": 0.44,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 1.175,
        #                "y": 0.88,
        #                "z": -0.07 * 0.5
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 1.175,
        #                "y": 0,
        #                "z": 1.62 * 0.5
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 1.175,
            "y": 0.88,
            "z": 1.63 * 0.5
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.44,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.175,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 1.175,
        #                "y": 0.88,
        #                "z": -0.07
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 1.175,
        #                "y": 0,
        #                "z": 1.62
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 1.175,
            "y": 0.88,
            "z": 1.63
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.44,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.175,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 2.35,
        #                "y": 0.88,
        #                "z": -0.07
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 2.35,
        #                "y": 0,
        #                "z": 1.62
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 2.35,
            "y": 0.88,
            "z": 1.63
        },
        "mass": 12,
        "offset": {
            "x": 0,
            "y": 0.44,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.35,
            "y": 1,
            "z": 1
        }
    }]
}


_TABLE_2_CIRCLE_BABY_SIZE = {
    "type": "table_2",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.33,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.33,
                "y": 0,
                "z": 0.5 * 0.33
            }
        }],
        "dimensions": {
            "x": 0.67 * 0.33,
            "y": 0.74 * 0.33,
            "z": 0.67 * 0.33
        },
        "mass": 0.25,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.33,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.33,
            "y": 0.33,
            "z": 0.33
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.33,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.5 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.67 * 0.5,
            "y": 0.74 * 0.33,
            "z": 0.67 * 0.5
        },
        "mass": 0.5,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.33,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.33,
            "z": 0.5
        }
    }]
}


_TABLE_2_CIRCLE_ACCESSIBLE = {
    "type": "table_2",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.5,
                "y": 0,
                "z": 0.5 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.67 * 0.5,
            "y": 0.74 * 0.5,
            "z": 0.67 * 0.5
        },
        "mass": 0.75,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.5,
                "y": 0,
                "z": 0.5
            }
        }],
        "dimensions": {
            "x": 0.67,
            "y": 0.74 * 0.5,
            "z": 0.67
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 0.75,
                "y": 0,
                "z": 0.5 * 0.75
            }
        }],
        "dimensions": {
            "x": 0.67 * 0.75,
            "y": 0.74 * 0.75,
            "z": 0.67 * 0.75
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.74 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.5 * 1.5,
                "y": 0,
                "z": 0.5 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.67 * 1.5,
            "y": 0.74 * 0.75,
            "z": 0.67 * 1.5
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.37 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 0.75,
            "z": 1.5
        }
    }]
}


_TABLE_2_CIRCLE_INACCESSIBLE = {
    "type": "table_2",
    "shape": ["table"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseSize": [{
        "size": "large",
        # "openAreas": [{
        #    "id": "",
        #    "position": {
        #        "x": 0,
        #        "y": 0.74,
        #        "z": 0
        #    },
        #    "dimensions": {
        #        "x": 0.5,
        #        "y": 0,
        #        "z": 0.5
        #    }
        # }],
        "dimensions": {
            "x": 0.67,
            "y": 0.74,
            "z": 0.67
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.37,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        # "openAreas": [{
        #    "id": "",
        #    "position": {
        #        "x": 0,
        #        "y": 0.74,
        #        "z": 0
        #    },
        #    "dimensions": {
        #        "x": 0.5 * 2,
        #        "y": 0,
        #        "z": 0.5 * 2
        #    }
        # }],
        "dimensions": {
            "x": 0.67 * 2,
            "y": 0.74,
            "z": 0.67 * 2
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.37,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_TABLE_3_CIRCLE_BABY_SIZE = {
    "type": "table_3",
    "shape": ["table"],
    "attributes": ["pickupable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.84 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.4 * 0.5,
                "y": 0,
                "z": 0.4 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.573 * 0.5,
            "y": 1.018 * 0.5,
            "z": 0.557 * 0.5
        },
        "mass": 0.5,
        "offset": {
            "x": 0,
            "y": 0.509 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.84 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.4,
                "y": 0,
                "z": 0.4
            }
        }],
        "dimensions": {
            "x": 0.573,
            "y": 1.018 * 0.5,
            "z": 0.557
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.509 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }]
}


_TABLE_3_CIRCLE_ACCESSIBLE = {
    "type": "table_3",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.84 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.4 * 1.5,
                "y": 0,
                "z": 0.4 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.573 * 1.5,
            "y": 1.018 * 0.5,
            "z": 0.557 * 1.5
        },
        "mass": 1.5,
        "offset": {
            "x": 0,
            "y": 0.509 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 0.5,
            "z": 1.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.84 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.4 * 2,
                "y": 0,
                "z": 0.4 * 2
            }
        }],
        "dimensions": {
            "x": 0.573 * 2,
            "y": 1.018 * 0.5,
            "z": 0.557 * 2
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.509 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 0.5,
            "z": 2
        }
    }]
}


_TABLE_3_CIRCLE_INACCESSIBLE = {
    "type": "table_3",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.84,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 0.4,
        #                "y": 0,
        #                "z": 0.4
        #            }
        #        }],
        "dimensions": {
            "x": 0.573,
            "y": 1.018,
            "z": 0.557
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.509,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.84,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 0.4 * 1.5,
        #                "y": 0,
        #                "z": 0.4 * 1.5
        #            }
        #        }],
        "dimensions": {
            "x": 0.573 * 1.5,
            "y": 1.018,
            "z": 0.557 * 1.5
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.509,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1,
            "z": 1.5
        }
    }, {
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.84,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 0.4 * 2,
        #                "y": 0,
        #                "z": 0.4 * 2
        #            }
        #        }],
        "dimensions": {
            "x": 0.573 * 2,
            "y": 1.018,
            "z": 0.557 * 2
        },
        "mass": 6,
        "offset": {
            "x": 0,
            "y": 0.509,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }, {
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.84,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 0.4 * 2.5,
        #                "y": 0,
        #                "z": 0.4 * 2.5
        #            }
        #        }],
        "dimensions": {
            "x": 0.573 * 2.5,
            "y": 1.018,
            "z": 0.557 * 2.5
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.509,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.5,
            "y": 1,
            "z": 2.5
        }
    }]
}


_TABLE_4_SEMICIRCLE_ACCESSIBLE = {
    "type": "table_4",
    "shape": ["table"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic", "plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 0.75,
                "y": 0,
                "z": 0.8 * 0.75
            }
        }],
        "dimensions": {
            "x": 0.62 * 0.75,
            "y": 0.62 * 0.75,
            "z": 1.17 * 0.75
        },
        "mass": 3,
        "offset": {
            "x": 0,
            "y": 0.31 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.45,
                "y": 0,
                "z": 0.8
            }
        }],
        "dimensions": {
            "x": 0.62,
            "y": 0.62 * 0.75,
            "z": 1.17
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.31 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.75,
            "z": 1
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 1.25,
                "y": 0,
                "z": 0.8 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.62 * 1.25,
            "y": 0.62 * 0.75,
            "z": 1.17 * 1.25
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.31 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 0.75,
            "z": 1.25
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 1.5,
                "y": 0,
                "z": 0.8 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.62 * 1.5,
            "y": 0.62 * 0.75,
            "z": 1.17 * 1.5
        },
        "mass": 6,
        "offset": {
            "x": 0,
            "y": 0.31 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 0.75,
            "z": 1.5
        }
    }]
}


_TABLE_4_SEMICIRCLE_INACCESSIBLE = {
    "type": "table_4",
    "shape": ["table"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic", "plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0
            },
            "dimensions": {
                "x": 0.45,
                "y": 0,
                "z": 0.8
            }
        }],
        "dimensions": {
            "x": 0.62,
            "y": 0.62,
            "z": 1.17
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.31,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 1.25,
                "y": 0,
                "z": 0.8 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.62 * 1.25,
            "y": 0.62,
            "z": 1.17 * 1.25
        },
        "mass": 9,
        "offset": {
            "x": 0,
            "y": 0.31,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1,
            "z": 1.25
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 1.5,
                "y": 0,
                "z": 0.8 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.62 * 1.5,
            "y": 0.62,
            "z": 1.17 * 1.5
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.31,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1,
            "z": 1.5
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0
            },
            "dimensions": {
                "x": 0.45 * 2,
                "y": 0,
                "z": 0.8 * 2
            }
        }],
        "dimensions": {
            "x": 0.62 * 2,
            "y": 0.62,
            "z": 1.17 * 2
        },
        "mass": 12,
        "offset": {
            "x": 0,
            "y": 0.31,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_TABLE_5_RECT_ACCESSIBLE = {
    "type": "table_5",
    "shape": ["table"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.7 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1.2 * 0.25,
                "y": 0,
                "z": 0.9 * 0.333
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1.2 * 0.25,
            "y": 0.7 * 0.5,
            "z": 0.9 * 0.333
        },
        "offset": {
            "x": 0,
            "y": 0.35 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.25,
            "y": 0.5,
            "z": 0.333
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.7 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1.2 * 0.5,
                "y": 0,
                "z": 0.9 * 0.333
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 1.2 * 0.5,
            "y": 0.7 * 0.5,
            "z": 0.9 * 0.333
        },
        "offset": {
            "x": 0,
            "y": 0.35 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.333
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.7 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1.2 * 0.5,
                "y": 0,
                "z": 0.9 * 0.667
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 1.2 * 0.5,
            "y": 0.7 * 0.5,
            "z": 0.9 * 0.667
        },
        "offset": {
            "x": 0,
            "y": 0.35 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.667
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.7 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1.2,
                "y": 0,
                "z": 0.9 * 0.667
            }
        }],
        "mass": 12,
        "dimensions": {
            "x": 1.2,
            "y": 0.7 * 0.5,
            "z": 0.9 * 0.667
        },
        "offset": {
            "x": 0,
            "y": 0.35 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 0.667
        }
    }]
}


_TABLE_5_RECT_INACCESSIBLE = {
    "type": "table_5",
    "shape": ["table"],
    "attributes": ["receptacle", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2 * 0.25,
        #                "y": 0,
        #                "z": 0.9 * 0.333
        #            }
        #        }],
        "dimensions": {
            "x": 1.2 * 0.25,
            "y": 0.7,
            "z": 0.9 * 0.333
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.25,
            "y": 1,
            "z": 0.333
        }
    }, {
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2 * 0.5,
        #                "y": 0,
        #                "z": 0.9 * 0.333
        #            }
        #        }],
        "dimensions": {
            "x": 1.2 * 0.5,
            "y": 0.7,
            "z": 0.9 * 0.333
        },
        "mass": 12,
        "offset": {
            "x": 0,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.333
        }
    }, {
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2 * 0.5,
        #                "y": 0,
        #                "z": 0.9 * 0.667
        #            }
        #        }],
        "dimensions": {
            "x": 1.2 * 0.5,
            "y": 0.7,
            "z": 0.9 * 0.667
        },
        "mass": 16,
        "offset": {
            "x": 0,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.667
        }
    }, {
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2,
        #                "y": 0,
        #                "z": 0.9 * 0.667
        #            }
        #        }],
        "dimensions": {
            "x": 1.2,
            "y": 0.7,
            "z": 0.9 * 0.667
        },
        "mass": 20,
        "offset": {
            "x": 0,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 0.667
        }
    }]
}


_TABLE_7_RECT_ACCESSIBLE = {
    "type": "table_7",
    "shape": ["table"],
    "attributes": ["receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.49,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 4,
        "dimensions": {
            "x": 1.02 * 0.49,
            "y": 0.45,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.49,
            "y": 1,
            "z": 0.769
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 1,
            "z": 0.769
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 1,
            "z": 1.538
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 1,
            "z": 1.538
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 1.96,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 1.02 * 1.96,
            "y": 0.45,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.96,
            "y": 1,
            "z": 0.769
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 1.96,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 12,
        "dimensions": {
            "x": 1.02 * 1.96,
            "y": 0.45,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.96,
            "y": 1,
            "z": 1.538
        }
    }]
}


_TABLE_7_RECT_INACCESSIBLE = {
    "type": "table_7",
    "shape": ["table"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.49,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 1.02 * 0.49,
            "y": 0.45 * 2,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.49,
            "y": 2,
            "z": 0.769
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45 * 2,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 2,
            "z": 0.769
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 12,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45 * 2,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 2,
            "z": 1.538
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 0.98,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 1.02 * 0.98,
            "y": 0.45 * 2,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.98,
            "y": 2,
            "z": 1.538
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 1.96,
                "y": 0,
                "z": 0.65 * 0.769
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 1.02 * 1.96,
            "y": 0.45 * 2,
            "z": 0.65 * 0.769
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.96,
            "y": 2,
            "z": 0.769
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 1.02 * 1.96,
                "y": 0,
                "z": 0.65 * 1.538
            }
        }],
        "mass": 20,
        "dimensions": {
            "x": 1.02 * 1.96,
            "y": 0.45 * 2,
            "z": 0.65 * 1.538
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.96,
            "y": 2,
            "z": 1.538
        }
    }]
}


_TABLE_8_RECT_ACCESSIBLE = {
    "type": "table_8",
    "shape": ["table"],
    "attributes": ["receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 0.49
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45 * 0.5,
            "z": 1.02 * 0.49
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 0.5,
            "z": 0.49
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45 * 0.5,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 0.5,
            "z": 0.98
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 12,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45 * 0.5,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 0.5,
            "z": 0.98
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45 * 0.5,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 0.5,
            "z": 0.98
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 1.96
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45 * 0.5,
            "z": 1.02 * 1.96
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 0.5,
            "z": 1.96
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 1.96
            }
        }],
        "mass": 20,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45 * 0.5,
            "z": 1.02 * 1.96
        },
        "offset": {
            "x": 0,
            "y": 0.22 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 0.5,
            "z": 1.96
        }
    }]
}


_TABLE_8_RECT_INACCESSIBLE = {
    "type": "table_8",
    "shape": ["table"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 0.49
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45,
            "z": 1.02 * 0.49
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 1,
            "z": 0.49
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 1,
            "z": 0.98
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 12,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 1,
            "z": 0.98
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 0.98
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45,
            "z": 1.02 * 0.98
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 1,
            "z": 0.98
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.769,
                "y": 0,
                "z": 1.02 * 1.96
            }
        }],
        "mass": 16,
        "dimensions": {
            "x": 0.65 * 0.769,
            "y": 0.45,
            "z": 1.02 * 1.96
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.769,
            "y": 1,
            "z": 1.96
        }
    }, {
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.45,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.538,
                "y": 0,
                "z": 1.02 * 1.96
            }
        }],
        "mass": 20,
        "dimensions": {
            "x": 0.65 * 1.538,
            "y": 0.45,
            "z": 1.02 * 1.96
        },
        "offset": {
            "x": 0,
            "y": 0.22,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.538,
            "y": 1,
            "z": 1.96
        }
    }]
}


_TABLE_11_T_LEGS = {
    "type": "table_11",
    "shape": ["table"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic", "plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1,
                "y": 0,
                "z": 1
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 1,
            "y": 0.5,
            "z": 1
        },
        "offset": {
            "x": 0,
            "y": 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1 * 0.5,
                "y": 0,
                "z": 1 * 0.5
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1 * 0.5,
            "y": 0.5,
            "z": 1 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1,
                "y": 0,
                "z": 1
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1,
            "y": 0.5 * 0.5,
            "z": 1
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1 * 0.5,
                "y": 0,
                "z": 1 * 0.5
            }
        }],
        "mass": 4,
        "dimensions": {
            "x": 1 * 0.5,
            "y": 0.5 * 0.5,
            "z": 1 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_TABLE_12_X_LEGS = {
    "type": "table_12",
    "shape": ["table"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic", "plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "huge",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1,
                "y": 0,
                "z": 1
            }
        }],
        "mass": 8,
        "dimensions": {
            "x": 1,
            "y": 0.5,
            "z": 1
        },
        "offset": {
            "x": 0,
            "y": 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1 * 0.5,
                "y": 0,
                "z": 1 * 0.5
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1 * 0.5,
            "y": 0.5,
            "z": 1 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1,
                "y": 0,
                "z": 1
            }
        }],
        "mass": 6,
        "dimensions": {
            "x": 1,
            "y": 0.5 * 0.5,
            "z": 1
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }, {
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.5 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1 * 0.5,
                "y": 0,
                "z": 1 * 0.5
            }
        }],
        "mass": 4,
        "dimensions": {
            "x": 1 * 0.5,
            "y": 0.5 * 0.5,
            "z": 1 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_TV = {
    "type": "tv_2",
    "shape": ["television"],
    "color": ["grey", "black"],
    "materialCategory": [],
    "salientMaterials": ["plastic"],
    "attributes": [],
    "chooseSize": [{
        "size": "medium",
        "mass": 5,
        "dimensions": {
            "x": 1.234,
            "y": 0.896,
            "z": 0.256
        },
        "offset": {
            "x": 0,
            "y": 0.5,
            "z": 0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "medium",
        "mass": 2.5,
        "dimensions": {
            "x": 1.234 * 0.5,
            "y": 0.896 * 0.5,
            "z": 0.256 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 0.5,
            "z": 0
        },
        "positionY": 0.5 * 0.5,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "mass": 2.5,
        "dimensions": {
            "x": 1.234 * 1.5,
            "y": 0.896 * 1.5,
            "z": 0.256 * 1.5
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 1.5,
            "z": 0
        },
        "positionY": 0.5 * 1.5,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "size": "medium",
        "mass": 2.5,
        "dimensions": {
            "x": 1.234 * 2,
            "y": 0.896 * 2,
            "z": 0.256 * 2
        },
        "offset": {
            "x": 0,
            "y": 0.5 * 2,
            "z": 0
        },
        "positionY": 0.5 * 2,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_SHELF_2_TABLE_SQUARE = {
    "type": "shelf_2",
    "shape": ["shelf"],
    "attributes": ["receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.73,
                "z": 0
            },
            "dimensions": {
                "x": 0.92 * 0.5,
                "y": 0,
                "z": 1.01 * 0.5
            }
        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.5,
                "y": 0.22,
                "z": 0.87 * 0.5
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 0.5,
                "y": 0.235,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 0.5,
            "y": 0.73,
            "z": 1.02 * 0.5
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.355,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.73,
                "z": 0
            },
            "dimensions": {
                "x": 0.92,
                "y": 0,
                "z": 1.01
            }
        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.65,
                "y": 0.22,
                "z": 0.87
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225,
                "z": 0
            },
            "dimensions": {
                "x": 0.8,
                "y": 0.235,
                "z": 0.95
            }
        }],
        "dimensions": {
            "x": 0.93,
            "y": 0.73,
            "z": 1.02
        },
        "mass": 8,
        "offset": {
            "x": 0,
            "y": 0.355,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_SHELF_2_TABLE_RECT = {
    "type": "shelf_2",
    "shape": ["shelf"],
    "attributes": ["receptacle", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.65,
                "y": 0.22 * 2,
                "z": 0.87 * 0.5
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.8,
                "y": 0.235 * 2,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93,
            "y": 0.73 * 2,
            "z": 1.02 * 0.5
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.355 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 2,
            "z": 0.5
        }
    }, {
        "size": "large",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92 * 2,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 2,
                "y": 0.22 * 2,
                "z": 0.87 * 0.5
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 2,
                "y": 0.235 * 2,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 2,
            "y": 0.73 * 2,
            "z": 1.02 * 0.5
        },
        "mass": 14,
        "offset": {
            "x": 0,
            "y": 0.355 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 0.5
        }
    }, {
        "size": "huge",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92 * 2,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            #            "id": "_middle_shelf",
            #            "position": {
            #                "x": 0,
            #                "y": 0.52 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.65 * 2,
            #                "y": 0.22 * 3,
            #                "z": 0.87 * 0.5
            #            }
            #        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 3,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 2,
                "y": 0.235 * 3,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 2,
            "y": 0.73 * 3,
            "z": 1.02 * 0.5
        },
        "mass": 16,
        "offset": {
            "x": 0,
            "y": 0.355 * 3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 3,
            "z": 0.5
        }
    }, {
        "size": "huge",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92 * 3,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            #            "id": "_middle_shelf",
            #            "position": {
            #                "x": 0,
            #                "y": 0.52 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.65 * 3,
            #                "y": 0.22 * 3,
            #                "z": 0.87 * 0.5
            #            }
            #        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 3,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 3,
                "y": 0.235 * 3,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 3,
            "y": 0.73 * 3,
            "z": 1.02 * 0.5
        },
        "mass": 20,
        "offset": {
            "x": 0,
            "y": 0.355 * 3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 0.5
        }
    }]
}


_SHELF_1_CUBBY_BABY_SIZE = {
    "type": "shelf_1",
    "shape": ["shelf"],
    "attributes": ["moveable", "receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.78 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.5,
                "y": 0,
                "z": 0.39 * 0.5
            }
        }, {
            "id": "_top_right_shelf",
            "position": {
                "x": 0.175 * 0.5,
                "y": 0.56 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_top_left_shelf",
            "position": {
                "x": -0.175 * 0.5,
                "y": 0.56 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175 * 0.5,
                "y": 0.21 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175 * 0.5,
                "y": 0.21 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.78 * 0.5,
            "y": 0.77 * 0.5,
            "z": 0.4 * 0.5
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.385 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.78,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.77,
            #                "y": 0,
            #                "z": 0.39
            #            }
            #        }, {
            "id": "_top_right_shelf",
            "position": {
                "x": 0.175,
                "y": 0.56,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_top_left_shelf",
            "position": {
                "x": -0.175,
                "y": 0.56,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175,
                "y": 0.21,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175,
                "y": 0.21,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.78,
            "y": 0.77,
            "z": 0.4
        },
        "mass": 6,
        "offset": {
            "x": 0,
            "y": 0.385,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_SHELF_1_CUBBY = {
    "type": "shelf_1",
    "shape": ["shelf"],
    "attributes": ["receptacle", "stackTarget", "obstacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "massMultiplier": 1.5,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "huge",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.78 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.77 * 2,
            #                "y": 0,
            #                "z": 0.39
            #            }
            #        }, {
            #            "id": "_top_right_shelf",
            #            "position": {
            #                "x": 0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38
            #            }
            #        }, {
            #            "id": "_top_left_shelf",
            #            "position": {
            #                "x": -0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38
            #            }
            #        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.78 * 2,
            "y": 0.77 * 2,
            "z": 0.4
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.385 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 1
        }
    }, {
        "size": "huge",
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.78 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.77 * 2,
            #                "y": 0,
            #                "z": 0.39 * 2
            #            }
            #        }, {
            #            "id": "_top_right_shelf",
            #            "position": {
            #                "x": 0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38 * 2
            #            }
            #        }, {
            #            "id": "_top_left_shelf",
            #            "position": {
            #                "x": -0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38 * 2
            #            }
            #        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38 * 2
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38 * 2
            }
        }],
        "dimensions": {
            "x": 0.78 * 2,
            "y": 0.77 * 2,
            "z": 0.4 * 2
        },
        "mass": 12,
        "offset": {
            "x": 0,
            "y": 0.385 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_SOFA_BABY_SIZE = {
    "shape": ["sofa"],
    "salientMaterials": ["fabric"],
    "attributes": ["moveable", "receptacle", "stackTarget", "occluder"],
    "chooseType": [{
        "type": "sofa_1",
        "materialCategory": ["sofa_1"],
        "size": "medium",
        "mass": 5,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.333,
                "z": 0.24 * 0.333
            },
            "dimensions": {
                "x": 1.95 * 0.333,
                "y": 0,
                "z": 0.6 * 0.333
            }
        }],
        "dimensions": {
            "x": 2.64 * 0.333,
            "y": 1.15 * 0.333,
            "z": 1.23 * 0.333
        },
        "offset": {
            "x": 0,
            "y": 0.575 * 0.333,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.333,
            "y": 0.333,
            "z": 0.333
        }
    }, {
        "type": "sofa_1",
        "materialCategory": ["sofa_1"],
        "size": "large",
        "mass": 15,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.5,
                "z": 0.24 * 0.5
            },
            "dimensions": {
                "x": 1.95 * 0.5,
                "y": 0,
                "z": 0.6 * 0.5
            }
        }],
        "dimensions": {
            "x": 2.64 * 0.5,
            "y": 1.15 * 0.5,
            "z": 1.23 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.575 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "sofa_2",
        "materialCategory": ["sofa_2"],
        "size": "medium",
        "mass": 5,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59 * 0.333,
                "z": 0.15 * 0.333
            },
            "dimensions": {
                "x": 1.95 * 0.333,
                "y": 0,
                "z": 0.625 * 0.333
            }
        }],
        "dimensions": {
            "x": 2.55 * 0.333,
            "y": 1.25 * 0.333,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625 * 0.333,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.333,
            "y": 0.333,
            "z": 0.333
        }
    }, {
        "type": "sofa_2",
        "materialCategory": ["sofa_2"],
        "size": "large",
        "mass": 15,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59 * 0.5,
                "z": 0.15 * 0.5
            },
            "dimensions": {
                "x": 1.95 * 0.5,
                "y": 0,
                "z": 0.625 * 0.5
            }
        }],
        "dimensions": {
            "x": 2.55 * 0.5,
            "y": 1.25 * 0.5,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_SOFA_1 = {
    "type": "sofa_1",
    "shape": ["sofa"],
    "materialCategory": ["sofa_1"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 33,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0.24
            },
            "dimensions": {
                "x": 1.95 * 0.75,
                "y": 0,
                "z": 0.6
            }
        }],
        "dimensions": {
            "x": 2.64 * 0.75,
            "y": 1.15,
            "z": 1.23
        },
        "offset": {
            "x": 0,
            "y": 0.575,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 50,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0.24
            },
            "dimensions": {
                "x": 1.95,
                "y": 0,
                "z": 0.6
            }
        }],
        "dimensions": {
            "x": 2.64,
            "y": 1.15,
            "z": 1.23
        },
        "offset": {
            "x": 0,
            "y": 0.575,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 66,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0.24
            },
            "dimensions": {
                "x": 1.95 * 1.25,
                "y": 0,
                "z": 0.6
            }
        }],
        "dimensions": {
            "x": 2.64 * 1.25,
            "y": 1.15,
            "z": 1.23
        },
        "offset": {
            "x": 0,
            "y": 0.575,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1,
            "z": 1
        }
    }]
}


_SOFA_2 = {
    "type": "sofa_2",
    "shape": ["sofa"],
    "materialCategory": ["sofa_2"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 33,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95 * 0.75,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.55 * 0.75,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 50,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.55,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 66,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95 * 1.25,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.55 * 1.25,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1,
            "z": 1
        }
    }]
}


_SOFA_3 = {
    "type": "sofa_3",
    "shape": ["sofa"],
    "materialCategory": ["sofa_3"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 33,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95 * 0.75,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.4 * 0.75,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 50,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.4,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "huge",
        "mass": 66,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 1.95 * 1.25,
                "y": 0,
                "z": 0.625
            }
        }],
        "dimensions": {
            "x": 2.4 * 1.25,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1,
            "z": 1
        }
    }]
}


_SOFA_CHAIR_BABY_SIZE = {
    "shape": ["sofa chair"],
    "salientMaterials": ["fabric"],
    "attributes": ["moveable", "receptacle", "stackTarget", "occluder"],
    "chooseType": [{
        "type": "sofa_chair_1",
        "materialCategory": ["sofa_chair_1"],
        "size": "small",
        "mass": 3,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.333,
                "z": 0.24 * 0.333
            },
            "dimensions": {
                "x": 0.77 * 0.333,
                "y": 0,
                "z": 0.6 * 0.333
            }
        }],
        "dimensions": {
            "x": 1.43 * 0.333,
            "y": 1.15 * 0.333,
            "z": 1.23 * 0.333
        },
        "offset": {
            "x": 0,
            "y": 0.575 * 0.333,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.333,
            "y": 0.333,
            "z": 0.333
        }
    }, {
        "type": "sofa_chair_1",
        "materialCategory": ["sofa_chair_1"],
        "size": "medium",
        "mass": 10,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62 * 0.5,
                "z": 0.24 * 0.5
            },
            "dimensions": {
                "x": 0.77 * 0.5,
                "y": 0,
                "z": 0.6 * 0.5
            }
        }],
        "dimensions": {
            "x": 1.43 * 0.5,
            "y": 1.15 * 0.5,
            "z": 1.23 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.575 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "sofa_chair_2",
        "materialCategory": ["sofa_2"],
        "size": "small",
        "mass": 3,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59 * 0.333,
                "z": 0.15 * 0.333
            },
            "dimensions": {
                "x": 0.975 * 0.333,
                "y": 0,
                "z": 0.65 * 0.333
            }
        }],
        "dimensions": {
            "x": 1.425 * 0.333,
            "y": 1.25 * 0.333,
            "z": 0.95 * 0.333
        },
        "offset": {
            "x": 0,
            "y": 0.625 * 0.333,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.333,
            "y": 0.333,
            "z": 0.333
        }
    }, {
        "type": "sofa_chair_2",
        "materialCategory": ["sofa_2"],
        "size": "medium",
        "mass": 10,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59 * 0.5,
                "z": 0.15 * 0.5
            },
            "dimensions": {
                "x": 0.975 * 0.5,
                "y": 0,
                "z": 0.65 * 0.5
            }
        }],
        "dimensions": {
            "x": 1.425 * 0.5,
            "y": 1.25 * 0.5,
            "z": 0.95 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.625 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_SOFA_CHAIR_1 = {
    "type": "sofa_chair_1",
    "shape": ["sofa chair"],
    "materialCategory": ["sofa_chair_1"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 30,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.62,
                "z": 0.24
            },
            "dimensions": {
                "x": 0.77,
                "y": 0,
                "z": 0.6
            }
        }],
        "dimensions": {
            "x": 1.43,
            "y": 1.15,
            "z": 1.23
        },
        "offset": {
            "x": 0,
            "y": 0.575,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_SOFA_CHAIR_2 = {
    "type": "sofa_chair_2",
    "shape": ["sofa chair"],
    "materialCategory": ["sofa_2"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 30,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 0.975,
                "y": 0,
                "z": 0.65
            }
        }],
        "dimensions": {
            "x": 1.425,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_SOFA_CHAIR_3 = {
    "type": "sofa_chair_3",
    "shape": ["sofa chair"],
    "materialCategory": ["sofa_3"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget", "occluder"],
    "chooseSize": [{
        "size": "huge",
        "mass": 30,
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.59,
                "z": 0.15
            },
            "dimensions": {
                "x": 0.975,
                "y": 0,
                "z": 0.65
            }
        }],
        "dimensions": {
            "x": 1.425,
            "y": 1.25,
            "z": 0.95
        },
        "offset": {
            "x": 0,
            "y": 0.625,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_WARDROBE = {
    "type": "wardrobe",
    "shape": ["wardrobe"],
    "size": "huge",
    "mass": 50,
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "attributes": ["receptacle", "openable", "occluder"],
    "enclosedAreas": [{
        # Remove the top drawers and shelves for now.
        #        "id": "_middle_shelf_right",
        #        "position": {
        #            "x": 0.255,
        #            "y": 1.165,
        #            "z": 0.005
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 1.24,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_middle_shelf_left",
        #        "position": {
        #            "x": -0.255,
        #            "y": 1.295,
        #            "z": 0.005
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 0.98,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_bottom_shelf_left",
        #        "position": {
        #            "x": -0.255,
        #            "y": 0.665,
        #            "z": 0.005
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 0.24,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_lower_drawer_top_left",
        #        "position": {
        #            "x": -0.265,
        #            "y": 0.42,
        #            "z": 0.015
        #        },
        #        "dimensions": {
        #            "x": 0.445,
        #            "y": 0.16
        #            "z": 0.425
        #        }
        #    }, {
        #        "id": "_lower_drawer_top_right",
        #        "position": {
        #            "x": 0.265,
        #            "y": 0.42,
        #            "z": 0.015
        #        },
        #        "dimensions": {
        #            "x": 0.445,
        #            "y": 0.16
        #            "z": 0.425
        #        }
        #    }, {
        "id": "_lower_drawer_bottom_left",
        "position": {
            "x": -0.265,
            "y": 0.21,
            "z": 0.015
        },
        "dimensions": {
            "x": 0.445,
            "y": 0.16,
            "z": 0.425
        }
    }, {
        "id": "_lower_drawer_bottom_right",
        "position": {
            "x": 0.265,
            "y": 0.21,
            "z": 0.015
        },
        "dimensions": {
            "x": 0.445,
            "y": 0.16,
            "z": 0.425
        }
    }],
    "dimensions": {
        "x": 1.07,
        "y": 2.1,
        "z": 1
    },
    "offset": {
        "x": 0,
        "y": 1.05,
        "z": 0.17
    },
    "closedDimensions": {
        "x": 1.07,
        "y": 2.1,
        "z": 0.49
    },
    "closedOffset": {
        "x": 0,
        "y": 1.05,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CASE_1_SUITCASE = {
    "type": "case_1",
    "shape": ["case"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.0925 * 2.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.69 * 2.5,
                "y": 0.175 * 2.5,
                "z": 0.4 * 2.5
            }
        }],
        "dimensions": {
            "x": 0.71 * 2.5,
            "y": 0.19 * 2.5,
            "z": 0.42 * 2.5
        },
        "offset": {
            "x": 0,
            "y": 0.095 * 2.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.5,
            "y": 2.5,
            "z": 2.5
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.0925 * 2.25,
                "z": 0
            },
            "dimensions": {
                "x": 0.69 * 2.25,
                "y": 0.175 * 2.25,
                "z": 0.4 * 2.25
            }
        }],
        "dimensions": {
            "x": 0.71 * 2.25,
            "y": 0.19 * 2.25,
            "z": 0.42 * 2.25
        },
        "offset": {
            "x": 0,
            "y": 0.095 * 2.25,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.25,
            "y": 2.25,
            "z": 2.25
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.0925 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.69 * 2,
                "y": 0.175 * 2,
                "z": 0.4 * 2
            }
        }],
        "dimensions": {
            "x": 0.71 * 2,
            "y": 0.19 * 2,
            "z": 0.42 * 2
        },
        "offset": {
            "x": 0,
            "y": 0.095 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.0925 * 1.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.69 * 1.5,
                "y": 0.175 * 1.5,
                "z": 0.4 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.71 * 1.5,
            "y": 0.19 * 1.5,
            "z": 0.42 * 1.5
        },
        "offset": {
            "x": 0,
            "y": 0.095 * 1.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.0925 * 1,
                "z": 0
            },
            "dimensions": {
                "x": 0.69 * 1,
                "y": 0.175 * 1,
                "z": 0.4 * 1
            }
        }],
        "dimensions": {
            "x": 0.71 * 1,
            "y": 0.19 * 1,
            "z": 0.42 * 1
        },
        "offset": {
            "x": 0,
            "y": 0.095 * 1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_CASE_3 = {
    "type": "case_3",
    "shape": ["case"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.105 * 2.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.79 * 2.5,
                "y": 0.17 * 2.5,
                "z": 0.53 * 2.5
            }
        }],
        "dimensions": {
            "x": 0.81 * 2.5,
            "y": 0.21 * 2.5,
            "z": 0.56 * 2.5
        },
        "offset": {
            "x": 0,
            "y": 0.105 * 2.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.5,
            "y": 2.5,
            "z": 2.5
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.75,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.105 * 2.25,
                "z": 0
            },
            "dimensions": {
                "x": 0.79 * 2.25,
                "y": 0.17 * 2.25,
                "z": 0.53 * 2.25
            }
        }],
        "dimensions": {
            "x": 0.81 * 2.25,
            "y": 0.21 * 2.25,
            "z": 0.56 * 2.25
        },
        "offset": {
            "x": 0,
            "y": 0.105 * 2.25,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.25,
            "y": 2.25,
            "z": 2.25
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.105 * 1.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.79 * 1.5,
                "y": 0.17 * 1.5,
                "z": 0.53 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.81 * 1.5,
            "y": 0.21 * 1.5,
            "z": 0.56 * 1.5
        },
        "offset": {
            "x": 0,
            "y": 0.105 * 1.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.105 * 1,
                "z": 0
            },
            "dimensions": {
                "x": 0.79 * 1,
                "y": 0.17 * 1,
                "z": 0.53 * 1
            }
        }],
        "dimensions": {
            "x": 0.81 * 1,
            "y": 0.21 * 1,
            "z": 0.56 * 1
        },
        "offset": {
            "x": 0,
            "y": 0.105 * 1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_CHEST_1_CUBOID = {
    "type": "chest_1",
    "shape": ["chest"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 1.3,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 1.3,
                "y": 0.33 * 1.3,
                "z": 0.49 * 1.3
            }
        }],
        "dimensions": {
            "x": 0.83 * 1.3,
            "y": 0.42 * 1.3,
            "z": 0.55 * 1.3
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 1.3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.3,
            "y": 1.3,
            "z": 1.3
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.25,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 1.1,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 1.1,
                "y": 0.33 * 1.1,
                "z": 0.49 * 1.1
            }
        }],
        "dimensions": {
            "x": 0.83 * 1.1,
            "y": 0.42 * 1.1,
            "z": 0.55 * 1.1
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 1.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.1,
            "y": 1.1,
            "z": 1.1
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 0.9,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.9,
                "y": 0.33 * 0.9,
                "z": 0.49 * 0.9
            }
        }],
        "dimensions": {
            "x": 0.83 * 0.9,
            "y": 0.42 * 0.9,
            "z": 0.55 * 0.9
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 0.9,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 0.7,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.7,
                "y": 0.33 * 0.7,
                "z": 0.49 * 0.7
            }
        }],
        "dimensions": {
            "x": 0.83 * 0.7,
            "y": 0.42 * 0.7,
            "z": 0.55 * 0.7
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 0.7,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.49 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.83 * 0.5,
            "y": 0.42 * 0.5,
            "z": 0.55 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.195 * 0.3,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.3,
                "y": 0.33 * 0.3,
                "z": 0.49 * 0.3
            }
        }],
        "dimensions": {
            "x": 0.83 * 0.3,
            "y": 0.42 * 0.3,
            "z": 0.55 * 0.3
        },
        "offset": {
            "x": 0,
            "y": 0.205 * 0.3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.3,
            "y": 0.3,
            "z": 0.3
        }
    }]
}


_CHEST_2_SEMICYLINDER = {
    "type": "chest_2",
    "shape": ["chest"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 2,
                "y": 0.25 * 2,
                "z": 0.31 * 2
            }
        }],
        "dimensions": {
            "x": 0.52 * 2,
            "y": 0.42 * 2,
            "z": 0.38 * 2
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.25,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 1.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 1.75,
                "y": 0.25 * 1.75,
                "z": 0.31 * 1.75
            }
        }],
        "dimensions": {
            "x": 0.52 * 1.75,
            "y": 0.42 * 1.75,
            "z": 0.38 * 1.75
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 1.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.75,
            "y": 1.75,
            "z": 1.75
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 1.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 1.5,
                "y": 0.25 * 1.5,
                "z": 0.31 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.52 * 1.5,
            "y": 0.42 * 1.5,
            "z": 0.38 * 1.5
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 1.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 1.25,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 1.25,
                "y": 0.25 * 1.25,
                "z": 0.31 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.52 * 1.25,
            "y": 0.42 * 1.25,
            "z": 0.38 * 1.25
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 1.25,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.25,
            "y": 1.25,
            "z": 1.25
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 1,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 1,
                "y": 0.25 * 1,
                "z": 0.31 * 1
            }
        }],
        "dimensions": {
            "x": 0.52 * 1,
            "y": 0.42 * 1,
            "z": 0.38 * 1
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 0.75,
                "y": 0.25 * 0.75,
                "z": 0.31 * 0.75
            }
        }],
        "dimensions": {
            "x": 0.52 * 0.75,
            "y": 0.42 * 0.75,
            "z": 0.38 * 0.75
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 0.75,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.165 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.44 * 0.5,
                "y": 0.25 * 0.5,
                "z": 0.31 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.52 * 0.5,
            "y": 0.42 * 0.5,
            "z": 0.38 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.21 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_CHEST_3_CUBOID = {
    "type": "chest_3",
    "shape": ["chest"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 2.4,
                "z": 0
            },
            "dimensions": {
                "x": 0.35 * 2.4,
                "y": 0.12 * 2.4,
                "z": 0.21 * 2.4
            }
        }],
        "dimensions": {
            "x": 0.46 * 2.4,
            "y": 0.26 * 2.4,
            "z": 0.32 * 2.4
        },
        "offset": {
            "x": 0,
            "y": 0.13 * 2.4,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.4,
            "y": 2.4,
            "z": 2.4
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.35 * 2,
                "y": 0.12 * 2,
                "z": 0.21 * 2
            }
        }],
        "dimensions": {
            "x": 0.46 * 2,
            "y": 0.26 * 2,
            "z": 0.32 * 2
        },
        "offset": {
            "x": 0,
            "y": 0.13 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 1.6,
                "z": 0
            },
            "dimensions": {
                "x": 0.35 * 1.6,
                "y": 0.12 * 1.6,
                "z": 0.21 * 1.6
            }
        }],
        "dimensions": {
            "x": 0.46 * 1.6,
            "y": 0.26 * 1.6,
            "z": 0.32 * 1.6
        },
        "offset": {
            "x": 0,
            "y": 0.13 * 1.6,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.6,
            "y": 1.6,
            "z": 1.6
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 1.2,
                "z": 0
            },
            "dimensions": {
                "x": 0.35 * 1.2,
                "y": 0.12 * 1.2,
                "z": 0.21 * 1.2
            }
        }],
        "dimensions": {
            "x": 0.46 * 1.2,
            "y": 0.26 * 1.2,
            "z": 0.32 * 1.2
        },
        "offset": {
            "x": 0,
            "y": 0.13 * 1.2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.2,
            "y": 1.2,
            "z": 1.2
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 0.8,
                "z": 0
            },
            "dimensions": {
                "x": 0.35 * 0.8,
                "y": 0.12 * 0.8,
                "z": 0.21 * 0.8
            }
        }],
        "dimensions": {
            "x": 0.46 * 0.8,
            "y": 0.26 * 0.8,
            "z": 0.32 * 0.8
        },
        "offset": {
            "x": 0,
            "y": 0.13 * 0.8,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }]
}


_CHEST_8_SEMICYLINDER = {
    "type": "chest_8",
    "shape": ["chest"],
    "attributes": ["receptacle", "openable", "occluder"],
    "chooseMaterial": [{
        "massMultiplier": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "massMultiplier": 3,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 3,
                "z": 0
            },
            "dimensions": {
                "x": 0.36 * 3,
                "y": 0.135 * 3,
                "z": 0.28 * 3
            }
        }],
        "dimensions": {
            "x": 0.42 * 3,
            "y": 0.32 * 3,
            "z": 0.36 * 3
        },
        "offset": {
            "x": 0,
            "y": 0.16 * 3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 4,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 2.4,
                "z": 0
            },
            "dimensions": {
                "x": 0.36 * 2.4,
                "y": 0.135 * 2.4,
                "z": 0.28 * 2.4
            }
        }],
        "dimensions": {
            "x": 0.42 * 2.4,
            "y": 0.32 * 2.4,
            "z": 0.36 * 2.4
        },
        "offset": {
            "x": 0,
            "y": 0.16 * 2.4,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.4,
            "y": 2.4,
            "z": 2.4
        }
    }, {
        # Big enough to fit a soccer ball inside
        "size": "medium",
        "mass": 3.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 1.8,
                "z": 0
            },
            "dimensions": {
                "x": 0.36 * 1.8,
                "y": 0.135 * 1.8,
                "z": 0.28 * 1.8
            }
        }],
        "dimensions": {
            "x": 0.42 * 1.8,
            "y": 0.32 * 1.8,
            "z": 0.36 * 1.8
        },
        "offset": {
            "x": 0,
            "y": 0.16 * 1.8,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.8,
            "y": 1.8,
            "z": 1.8
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "medium",
        "mass": 3,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 1.2,
                "z": 0
            },
            "dimensions": {
                "x": 0.36 * 1.2,
                "y": 0.135 * 1.2,
                "z": 0.28 * 1.2
            }
        }],
        "dimensions": {
            "x": 0.42 * 1.2,
            "y": 0.32 * 1.2,
            "z": 0.36 * 1.2
        },
        "offset": {
            "x": 0,
            "y": 0.16 * 1.2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.2,
            "y": 1.2,
            "z": 1.2
        }
    }, {
        # Too little to fit a soccer ball inside
        "size": "small",
        "mass": 2.5,
        "enclosedAreas": [{
            "position": {
                "x": 0,
                "y": 0.09 * 0.8,
                "z": 0
            },
            "dimensions": {
                "x": 0.36 * 0.8,
                "y": 0.135 * 0.8,
                "z": 0.28 * 0.8
            }
        }],
        "dimensions": {
            "x": 0.42 * 0.8,
            "y": 0.32 * 0.8,
            "z": 0.36 * 0.8
        },
        "offset": {
            "x": 0,
            "y": 0.16 * 0.8,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }]
}


_POTTED_PLANT_LARGE = {
    "shape": ["potted plant"],
    "size": "large",
    "mass": 5,
    "materialCategory": [],
    "salientMaterials": ["organic", "ceramic"],
    "attributes": [],
    "chooseType": [{
        "type": "plant_1",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.931 * 2,
            "y": 0.807 * 2,
            "z": 0.894
        },
        "offset": {
            "x": -0.114 * 2,
            "y": 0.399 * 2,
            "z": -0.118
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_5",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.522 * 2,
            "y": 0.656 * 2,
            "z": 0.62
        },
        "offset": {
            "x": -0.024 * 2,
            "y": 0.32 * 2,
            "z": -0.018
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_7",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.72 * 2,
            "y": 1.094 * 2,
            "z": 0.755
        },
        "offset": {
            "x": 0 * 2,
            "y": 0.546 * 2,
            "z": -0.017
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_9",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.679 * 2,
            "y": 0.859 * 2,
            "z": 0.546
        },
        "offset": {
            "x": 0.037 * 2,
            "y": 0.41 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_14",
        "color": ["red", "brown"],
        "dimensions": {
            "x": 0.508 * 2,
            "y": 0.815 * 2,
            "z": 0.623
        },
        "offset": {
            "x": 0.036 * 2,
            "y": 0.383 * 2,
            "z": 0.033
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_16",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.702 * 2,
            "y": 1.278 * 2,
            "z": 0.813
        },
        "offset": {
            "x": -0.008 * 2,
            "y": 0.629 * 2,
            "z": -0.012
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST = [{
    "materialCategory": ["intuitive_physics_block"],
    "salientMaterials": ["wood"],
}, {
    "materialCategory": ["intuitive_physics_plastic"],
    "salientMaterials": ["plastic"],
}, {
    "materialCategory": ["intuitive_physics_wood"],
    "salientMaterials": ["wood"]
}]


# Size data for non-cylinder primitive objects (cones, cubes, spheres, etc.)
_STANDARD_BASE_SIZE = {
    "dimensions": {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0
    },
    "mass": 1.0,
    "positionY": 0.5,
    "scale": {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0
    }
}


# Size data for cylinder primitive objects.
_CYLINDER_BASE_SIZE = {
    "dimensions": {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0
    },
    "mass": 1.0,
    "positionY": 0.5,
    "scale": {
        "x": 1.0,
        # Unity cylinders always double their height (I don't know why).
        "y": 0.5,
        "z": 1.0
    }
}


# Size data for rectangular primitive objects.
_RECT_BASE_SIZE = {
    "dimensions": {
        "x": 1.0,
        "y": 0.5,
        "z": 1.0
    },
    "mass": 1.0,
    "positionY": 0.25,
    "scale": {
        "x": 1.0,
        "y": 0.5,
        "z": 1.0
    }
}


_INTUITIVE_PHYSICS_CIRCLE_FRUSTUM = {
    "type": "circle_frustum",
    "shape": ["circle frustum"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_CONE = {
    "type": "cone",
    "shape": ["cone"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_CUBE = {
    "type": "cube",
    "shape": ["cube"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_CYLINDER = {
    "type": "cylinder",
    "shape": ["cylinder"],
    "rotation": {
        # Rotate the cylinder onto its curved side so it can roll sideways.
        "x": 90,
        "y": 0,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(0.4, 'small', _CYLINDER_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _CYLINDER_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _CYLINDER_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_PYRAMID = {
    "type": "pyramid",
    "shape": ["pyramid"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_RECTANGULAR_PRISM = {
    "type": "cube",
    "shape": ["rectangle"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _RECT_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _RECT_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _RECT_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_SPHERE = {
    "type": "sphere",
    "shape": ["sphere"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_SQUARE_FRUSTUM = {
    "type": "square_frustum",
    "shape": ["square frustum"],
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_TUBE_NARROW = {
    "type": "tube_narrow",
    "shape": ["narrow tube"],
    "rotation": {
        # Rotate the tube onto its curved side so it can roll sideways.
        "x": 90,
        "y": 0,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_INTUITIVE_PHYSICS_TUBE_WIDE = {
    "type": "tube_wide",
    "shape": ["wide tube"],
    "rotation": {
        # Rotate the tube onto its curved side so it can roll sideways.
        "x": 90,
        "y": 0,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(0.4, 'small', _STANDARD_BASE_SIZE, True),
        _create_size_option(0.5, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.55, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.6, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.65, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.7, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.75, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.8, 'medium', _STANDARD_BASE_SIZE, False),
        _create_size_option(0.9, 'large', _STANDARD_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_DUCK_BASE_SIZE = {
    "dimensions": {
        "x": 0.21,
        "y": 0.17,
        "z": 0.065
    },
    "positionY": 0,
    "mass": 0.25,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_DUCK = {
    "type": "duck_on_wheels",
    "shape": ["duck"],
    "chooseSize": [
        _create_size_option(2.5, 'small', _DUCK_BASE_SIZE, True),
        _create_size_option(3.25, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(3.5, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(3.75, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(4, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(4.25, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(4.5, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(4.75, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(5, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(5.25, 'medium', _DUCK_BASE_SIZE, False),
        _create_size_option(5.75, 'large', _DUCK_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_TURTLE_BASE_SIZE = {
    "dimensions": {
        "x": 0.24,
        "y": 0.14,
        "z": 0.085
    },
    "mass": 0.25,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_TURTLE = {
    "type": "turtle_on_wheels",
    "shape": ["turtle"],
    "chooseSize": [
        _create_size_option(2.25, 'small', _TURTLE_BASE_SIZE, True),
        _create_size_option(2.75, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(3, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(3.25, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(3.5, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(3.75, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(4, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(4.25, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(4.5, 'medium', _TURTLE_BASE_SIZE, False),
        _create_size_option(5, 'large', _TURTLE_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_CAR_1_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.14,
        "y": 0.065,
        "z": 0.075
    },
    "mass": 0.25,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_CAR = {
    "type": "car_1",
    "shape": ["car"],
    "rotation": {
        "x": 0,
        # Turn the car so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(3.5, 'small', _CAR_1_BASE_SIZE, True),
        _create_size_option(4.5, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(5, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(5.5, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(6, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(6.5, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(7, 'medium', _CAR_1_BASE_SIZE, False),
        _create_size_option(8, 'large', _CAR_1_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_RACECAR_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.15,
        "y": 0.06,
        "z": 0.07
    },
    "mass": 0.25,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_RACECAR = {
    "type": "racecar_red",
    "shape": ["car"],
    "rotation": {
        "x": 0,
        # Turn the racecar so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(3.5, 'small', _RACECAR_BASE_SIZE, True),
        _create_size_option(4.25, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(4.75, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(5.25, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(5.75, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(6.25, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(6.75, 'medium', _RACECAR_BASE_SIZE, False),
        _create_size_option(7.75, 'large', _RACECAR_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_DOG_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.355,
        "y": 0.134,
        "z": 0.071
    },
    "mass": 0.5,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_DOG = {
    "type": "dog_on_wheels",
    "shape": ["dog"],
    "rotation": {
        "x": 0,
        # Turn the dog so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(1.5, 'small', _DOG_BASE_SIZE, True),
        _create_size_option(2, 'medium', _DOG_BASE_SIZE, False),
        _create_size_option(2.25, 'medium', _DOG_BASE_SIZE, False),
        _create_size_option(2.5, 'medium', _DOG_BASE_SIZE, False),
        _create_size_option(2.75, 'medium', _DOG_BASE_SIZE, False),
        _create_size_option(3, 'medium', _DOG_BASE_SIZE, False),
        _create_size_option(3.5, 'large', _DOG_BASE_SIZE, True)
    ],
    "chooseMaterial": [{
        'materialCategory': item['materialCategory'] * 2,
        'salientMaterials': item['salientMaterials']
    } for item in INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST],
    "attributes": ["moveable"]
}


_TRAIN_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.23,
        "y": 0.2,
        "z": 0.16
    },
    "mass": 0.25,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_TRAIN = {
    "type": "train_1",
    "shape": ["train"],
    "rotation": {
        "x": 0,
        # Turn the train so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(2, 'small', _TRAIN_BASE_SIZE, True),
        _create_size_option(2.5, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(2.75, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(3, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(3.25, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(3.5, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(3.75, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(4, 'medium', _TRAIN_BASE_SIZE, False),
        _create_size_option(4.5, 'large', _TRAIN_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_TROLLEY_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.23,
        "y": 0.2,
        "z": 0.16
    },
    "mass": 0.25,
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_TROLLEY = {
    "type": "trolley_1",
    "shape": ["trolley"],
    "rotation": {
        "x": 0,
        # Turn the trolley so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(2, 'small', _TROLLEY_BASE_SIZE, True),
        _create_size_option(2.5, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(2.75, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(3, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(3.25, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(3.5, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(3.75, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(4, 'medium', _TROLLEY_BASE_SIZE, False),
        _create_size_option(4.5, 'large', _TROLLEY_BASE_SIZE, True)
    ],
    "chooseMaterial": INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST,
    "attributes": ["moveable"]
}


_TRUCK_BASE_SIZE = {
    "dimensions": {
        # The X and Z dimensions are switched due to the Y rotation.
        "x": 0.25,
        "y": 0.18,
        "z": 0.2
    },
    "mass": 0.25,
    "positionY": 0.1,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_INTUITIVE_PHYSICS_TRUCK = {
    "type": "truck_1",
    "shape": ["truck"],
    "rotation": {
        "x": 0,
        # Turn the truck so its side is facing the camera.
        "y": 90,
        "z": 0
    },
    "chooseSize": [
        _create_size_option(1.75, 'small', _TRUCK_BASE_SIZE, True),
        _create_size_option(2.25, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(2.5, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(2.75, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(3, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(3.25, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(3.5, 'medium', _TRUCK_BASE_SIZE, False),
        _create_size_option(4, 'large', _TRUCK_BASE_SIZE, True)
    ],
    "chooseMaterial": [{
        'materialCategory': item['materialCategory'] * 2,
        'salientMaterials': item['salientMaterials']
    } for item in INTUITIVE_PHYSICS_OBJECT_CHOOSE_MATERIAL_LIST],
    "attributes": ["moveable"]
}


# Same random chance of balls, blocks, toys, or misc objects.
_PICKUPABLES = [
    [_BALL],
    [_BLOCK_BLANK_CUBE, _BLOCK_BLANK_CYLINDER, _BLOCK_LETTER, _BLOCK_NUMBER],
    [
        _TOY_CAR,
        _TOY_RACECAR,
        _DUCK_ON_WHEELS,
        _TURTLE_ON_WHEELS
    ],
    [
        _APPLE,
        _BOWL,
        _CUP,
        _PLATE,
        _CAKE,
        _CRAYON,
        _PACIFIER
    ]
]


_NOT_PICKUPABLES = [
    [_BLOCK_BLANK_CUBE_NOT_PICKUPABLE, _BLOCK_BLANK_CYLINDER_NOT_PICKUPABLE],
    [_CHAIR_1_NORMAL],
    [_CHAIR_1_NORMAL_BABY_SIZE, _CHAIR_2_STOOL_CIRCLE_BABY_SIZE],
    [_CHAIR_2_STOOL_CIRCLE],
    [_CRIB],
    [_SHELF_1_CUBBY, _SHELF_1_CUBBY_BABY_SIZE],
    [_SHELF_2_TABLE_SQUARE, _SHELF_2_TABLE_RECT],
    [_SOFA_1, _SOFA_2, _SOFA_BABY_SIZE],
    [_SOFA_CHAIR_1, _SOFA_CHAIR_2, _SOFA_CHAIR_BABY_SIZE],
    [_TABLE_1_RECT_ACCESSIBLE, _TABLE_1_RECT_INACCESSIBLE],
    [_TABLE_1_RECT_BABY_SIZE, _TABLE_3_CIRCLE_BABY_SIZE],
    [_TABLE_3_CIRCLE_ACCESSIBLE, _TABLE_3_CIRCLE_INACCESSIBLE],
    [_TABLE_5_RECT_ACCESSIBLE, _TABLE_5_RECT_INACCESSIBLE],
    # Eval 3 Untrained Shapes
    [_BOOKCASE],
    [_BOOKCASE_SIDELESS],
    [_CART],
    [_CHAIR_4_OFFICE],
    [_CHAIR_3_STOOL_RECT],
    [_SOFA_3, _SOFA_CHAIR_3],
    [_TABLE_2_CIRCLE_ACCESSIBLE, _TABLE_2_CIRCLE_INACCESSIBLE],
    [_TABLE_4_SEMICIRCLE_ACCESSIBLE, _TABLE_4_SEMICIRCLE_INACCESSIBLE],
    [_TABLE_7_RECT_ACCESSIBLE, _TABLE_7_RECT_INACCESSIBLE],
    [_TABLE_8_RECT_ACCESSIBLE, _TABLE_8_RECT_INACCESSIBLE],
    [_TABLE_11_T_LEGS, _TABLE_12_X_LEGS],
    [_TV]
    # Do not use containers as possible occluders in Eval 3
    # [_CHANGING_TABLE],
    # [_CASE_1_SUITCASE],
    # [_CHEST_1_CUBOID],
    # [_CHEST_2_SEMICYLINDER],
    # [_WARDROBE]
]


_CONTAINERS = [
    [_CASE_1_SUITCASE],
    [_CHEST_1_CUBOID],
    [_CHEST_2_SEMICYLINDER],
    # Eval 3 Untrained Shapes
    [_CASE_3],
    [_CHEST_3_CUBOID],
    [_CHEST_8_SEMICYLINDER]
]


_OBSTACLES = [
    object_list for object_list in _NOT_PICKUPABLES if all([
        ('obstacle' in item.get('attributes', [])) for item in object_list
    ])
]

_OCCLUDERS = [
    object_list for object_list in _NOT_PICKUPABLES if all([
        ('occluder' in item.get('attributes', [])) for item in object_list
    ])
]


_STACK_TARGETS = [
    [_BOOKCASE],
    [_BOOKCASE_SIDELESS],
    [_BLOCK_LETTER, _BLOCK_NUMBER],
    [_BLOCK_BLANK_CUBE, _BLOCK_BLANK_CUBE_NOT_PICKUPABLE],
    [_BOWL, _CUP, _PLATE],
    [_CART],
    [_CHAIR_1_NORMAL, _CHAIR_1_NORMAL_BABY_SIZE],
    [_CHAIR_2_STOOL_CIRCLE, _CHAIR_2_STOOL_CIRCLE_BABY_SIZE],
    [_CHAIR_3_STOOL_RECT],
    [_CHAIR_4_OFFICE],
    [_SHELF_1_CUBBY, _SHELF_1_CUBBY_BABY_SIZE],
    [_SHELF_2_TABLE_SQUARE, _SHELF_2_TABLE_RECT],
    [_SOFA_1, _SOFA_2, _SOFA_3, _SOFA_BABY_SIZE],
    [_SOFA_CHAIR_1, _SOFA_CHAIR_2, _SOFA_CHAIR_3, _SOFA_CHAIR_BABY_SIZE],
    [_TABLE_1_RECT_ACCESSIBLE, _TABLE_1_RECT_BABY_SIZE],
    [_TABLE_3_CIRCLE_ACCESSIBLE, _TABLE_3_CIRCLE_BABY_SIZE],
    [_TABLE_5_RECT_ACCESSIBLE],
    [_TABLE_2_CIRCLE_ACCESSIBLE],
    [_TABLE_4_SEMICIRCLE_ACCESSIBLE],
    [_TABLE_7_RECT_ACCESSIBLE],
    [_TABLE_8_RECT_ACCESSIBLE],
    [_TABLE_11_T_LEGS, _TABLE_12_X_LEGS]
]


_ALL = _PICKUPABLES + _NOT_PICKUPABLES


# Only use rollable objects in move-across setups.
_MOVE_ACROSS_BASIC = [
    _INTUITIVE_PHYSICS_CYLINDER,
    _INTUITIVE_PHYSICS_SPHERE,
    # Eval 3 Untrained Shapes
    _INTUITIVE_PHYSICS_TUBE_NARROW,
    _INTUITIVE_PHYSICS_TUBE_WIDE
]

_FALL_DOWN_BASIC = _MOVE_ACROSS_BASIC + [
    _INTUITIVE_PHYSICS_CONE,
    _INTUITIVE_PHYSICS_CUBE,
    _INTUITIVE_PHYSICS_RECTANGULAR_PRISM,
    _INTUITIVE_PHYSICS_SQUARE_FRUSTUM,
    # Eval 3 Untrained Shapes
    _INTUITIVE_PHYSICS_CIRCLE_FRUSTUM,
    _INTUITIVE_PHYSICS_PYRAMID
]

# Only use rollable objects in move-across setups.
_MOVE_ACROSS_COMPLEX = [
    _INTUITIVE_PHYSICS_DUCK,
    _INTUITIVE_PHYSICS_TURTLE,
    _INTUITIVE_PHYSICS_CAR,
    _INTUITIVE_PHYSICS_RACECAR,
    # Eval 3 Untrained Shapes
    # _INTUITIVE_PHYSICS_DOG,
    _INTUITIVE_PHYSICS_TRAIN,
    _INTUITIVE_PHYSICS_TROLLEY
    # _INTUITIVE_PHYSICS_TRUCK
]

_FALL_DOWN_COMPLEX = _MOVE_ACROSS_COMPLEX.copy()

_MOVE_ACROSS_ALL = _MOVE_ACROSS_BASIC + _MOVE_ACROSS_COMPLEX
_FALL_DOWN_ALL = _FALL_DOWN_BASIC + _FALL_DOWN_COMPLEX


class ObjectDefinitionList(Enum):
    ALL = 'ALL'
    CONTAINERS = 'CONTAINERS'
    INTUITIVE_PHYSICS_FALL_DOWN_BASIC = 'FALL_DOWN_BASIC'
    INTUITIVE_PHYSICS_FALL_DOWN_COMPLEX = 'FALL_DOWN_COMPLEX'
    INTUITIVE_PHYSICS_MOVE_ACROSS_BASIC = 'MOVE_ACROSS_BASIC'
    INTUITIVE_PHYSICS_MOVE_ACROSS_COMPLEX = 'MOVE_ACROSS_COMPLEX'
    NOT_PICKUPABLES = 'NOT_PICKUPABLES'
    OBSTACLES = 'OBSTACLES'
    OCCLUDERS = 'OCCLUDERS'
    PICKUPABLES = 'PICKUPABLES'
    STACK_TARGETS = 'STACK_TARGETS'


def _get(prop: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def get(item: ObjectDefinitionList) -> List[Dict[str, Any]]:
    """Returns a deep copy of the given ObjectDefinitionList."""
    return _get(item.value)


def get_intuitive_physics(
    is_fall_down: bool,
    only_basic_shapes=False,
    only_complex_shapes=False
) -> List[Dict[str, Any]]:
    """Returns a deep copy of the intuitive physics definition list."""
    return _get(('FALL_DOWN' if is_fall_down else 'MOVE_ACROSS') + (
        '_COMPLEX' if only_complex_shapes else (
            '_BASIC' if only_basic_shapes else '_ALL'
        )
    ))


def get_soccer_ball() -> Dict[str, Any]:
    """Returns a deep copy of the soccer ball (Eval 4 interactive target)."""
    return _get('SOCCER_BALL')
