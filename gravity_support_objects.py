import copy
from typing import Any, Dict, List, Union
import uuid


POLE_MOVE_AMOUNT = 0.1
POLE_WAIT_TIME = 1


_VISIBLE_SUPPORT = {
    "type": "cube",
    "role": "structural",
    "shape": ["rectangular prism"],
    "salientMaterials": [],
    "attributes": ["kinematic", "structure"],
    "chooseSize": [{
        "mass": 50,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 55,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.6,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 60,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.7,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 65,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.8,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 70,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.9,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 55,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.5,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 60,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 65,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.7,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 70,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.8,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.9,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 1.0,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 60,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.5,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 65,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.6,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 70,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.8,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.9,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 1.0,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 65,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.5,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 70,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.6,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.7,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.9,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 1.0,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 70,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.5,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.6,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.7,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.8,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 1.0,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 75,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 0.5,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 0.6,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 0.7,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 0.8,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 0.9,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 80,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 0.5,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 0.6,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 0.7,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 0.8,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 0.9,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 105,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.1,
            "z": 1.0
        },
        "positionY": 0.55,
        "scale": {
            "x": 1.0,
            "y": 1.1,
            "z": 1.0
        }
    }, {
        "mass": 85,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 0.5,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 0.6,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 0.7,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 0.8,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 105,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 0.9,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 110,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.2,
            "z": 1.0
        },
        "positionY": 0.6,
        "scale": {
            "x": 1.0,
            "y": 1.2,
            "z": 1.0
        }
    }, {
        "mass": 90,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 0.5,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 0.6,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 0.7,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 105,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 0.8,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 110,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 0.9,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 115,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.3,
            "z": 1.0
        },
        "positionY": 0.65,
        "scale": {
            "x": 1.0,
            "y": 1.3,
            "z": 1.0
        }
    }, {
        "mass": 95,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 0.5,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 0.6,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 105,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 0.7,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 110,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 0.8,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 115,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 0.9,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 120,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.4,
            "z": 1.0
        },
        "positionY": 0.7,
        "scale": {
            "x": 1.0,
            "y": 1.4,
            "z": 1.0
        }
    }, {
        "mass": 100,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 0.5,
            "y": 1.5,
            "z": 1.0
        }
    }, {
        "mass": 105,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 0.6,
            "y": 1.5,
            "z": 1.0
        }
    }, {
        "mass": 110,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 0.7,
            "y": 1.5,
            "z": 1.0
        }
    }, {
        "mass": 115,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 0.8,
            "y": 1.5,
            "z": 1.0
        }
    }, {
        "mass": 120,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 0.9,
            "y": 1.5,
            "z": 1.0
        }
    }, {
        "mass": 125,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.5,
            "z": 1.0
        },
        "positionY": 0.75,
        "scale": {
            "x": 1.0,
            "y": 1.5,
            "z": 1.0
        }
    }]
}


_LETTER_L_NARROW = {
    "type": "letter_l_narrow",
    "shape": ["letter l"],
    "poleOffsetX": -0.20,
    "chooseSize": [{
        "mass": 2.5,
        "size": "medium",
        "dimensions": {
            "x": 0.25,
            "y": 0.5,
            "z": 0.25
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.3,
            "y": 0.6,
            "z": 0.3
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.35,
            "y": 0.7,
            "z": 0.35
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.4,
            "y": 0.8,
            "z": 0.4
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.45,
            "y": 0.9,
            "z": 0.45
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.0,
            "z": 0.5
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 0.55,
            "y": 1.1,
            "z": 0.55
        },
        "positionY": 0.55,
        "scale": {
            "x": 1.1,
            "y": 1.1,
            "z": 1.1
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 1.2,
            "z": 0.6
        },
        "positionY": 0.6,
        "scale": {
            "x": 1.2,
            "y": 1.2,
            "z": 1.2
        }
    }, {
        "mass": 6.5,
        "size": "medium",
        "dimensions": {
            "x": 0.65,
            "y": 1.3,
            "z": 0.65
        },
        "positionY": 0.65,
        "scale": {
            "x": 1.3,
            "y": 1.3,
            "z": 1.3
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 1.4,
            "z": 0.7
        },
        "positionY": 0.7,
        "scale": {
            "x": 1.4,
            "y": 1.4,
            "z": 1.4
        }
    }, {
        "mass": 7.5,
        "size": "medium",
        "dimensions": {
            "x": 0.75,
            "y": 1.5,
            "z": 0.75
        },
        "positionY": 0.75,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 1.6,
            "z": 0.8
        },
        "positionY": 0.8,
        "scale": {
            "x": 1.6,
            "y": 1.6,
            "z": 1.6
        }
    }, {
        "mass": 8.5,
        "size": "medium",
        "dimensions": {
            "x": 0.85,
            "y": 1.7,
            "z": 0.85
        },
        "positionY": 0.85,
        "scale": {
            "x": 1.7,
            "y": 1.7,
            "z": 1.7
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 1.8,
            "z": 0.9
        },
        "positionY": 0.9,
        "scale": {
            "x": 1.8,
            "y": 1.8,
            "z": 1.8
        }
    }, {
        "mass": 9.5,
        "size": "medium",
        "dimensions": {
            "x": 0.95,
            "y": 1.9,
            "z": 0.95
        },
        "positionY": 0.95,
        "scale": {
            "x": 1.9,
            "y": 1.9,
            "z": 1.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 2.0,
            "z": 1.0
        },
        "positionY": 1.0,
        "scale": {
            "x": 2.0,
            "y": 2.0,
            "z": 2.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"],
    "poly": [
        {'x': 0.25, 'z': -0.5},
        {'x': -0.25, 'z': -0.5},
        {'x': -0.25, 'z': 0.5},
        {'x': -0.15, 'z': 0.5},
        {'x': -0.15, 'z': -0.4},
        {'x': 0.25, 'z': -0.4}
    ]
}


_LETTER_L_WIDE = {
    "type": "letter_l_wide",
    "shape": ["letter l"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"],
    "poly": [
        {'x': 0.5, 'z': -0.5},
        {'x': -0.5, 'z': -0.5},
        {'x': -0.5, 'z': 0.5},
        {'x': 0, 'z': 0.5},
        {'x': 0, 'z': 0},
        {'x': 0.5, 'z': 0}
    ]
}


_TRIANGLE_90_45_45 = {
    "type": "triangle",
    "shape": ["triangle"],
    "poleOffsetX": -0.45,
    "rotation": {
        "x": 0,
        "y": -90,
        "z": 0
    },
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"],
    "poly": [
        {'x': 0.5, 'z': -0.5},
        {'x': -0.5, 'z': -0.5},
        {'x': -0.5, 'z': 0.5}
    ]
}


_TRIANGLE_90_60_30 = {
    "type": "triangle",
    "shape": ["triangle"],
    "poleOffsetX": -0.45,
    "rotation": {
        "x": 0,
        "y": -90,
        "z": 0
    },
    "chooseSize": [{
        "mass": 2.5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        }
    }, {
        "mass": 2.5,
        "size": "medium",
        "dimensions": {
            "x": 0.25,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.25
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.3,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.3
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.35,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.35
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.4,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.4
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.45,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.45
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 0.5
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"],
    "poly": [
        {'x': 0.5, 'z': -0.25},
        {'x': -0.5, 'z': -0.25},
        {'x': -0.5, 'z': 0.25}
    ]
}


_CIRCLE_FRUSTUM = {
    "type": "circle_frustum",
    "shape": ["circle frustum"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_CONE = {
    "type": "cone",
    "shape": ["cone"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_CUBE = {
    "type": "cube",
    "shape": ["cube"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_CYLINDER = {
    "type": "cylinder",
    "shape": ["cylinder"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.25,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.3,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.35,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.4,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.45,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            # Unity cylinders always double their height (I don't know why).
            "y": 0.5,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_PYRAMID = {
    "type": "pyramid",
    "shape": ["pyramid"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_RECTANGULAR_PRISM_THIN = {
    "type": "cube",
    "shape": ["rectangular prism"],
    "chooseSize": [{
        "mass": 2.5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.25,
            "z": 0.6
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.6,
            "y": 0.25,
            "z": 0.6
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.25,
            "z": 0.7
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.7,
            "y": 0.25,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.25,
            "z": 0.8
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.8,
            "y": 0.25,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.25,
            "z": 0.9
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.9,
            "y": 0.25,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.25,
            "z": 1.0
        },
        "positionY": 0.125,
        "scale": {
            "x": 1.0,
            "y": 0.25,
            "z": 1.0
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.3,
            "z": 0.7
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.7,
            "y": 0.3,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.3,
            "z": 0.8
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.8,
            "y": 0.3,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.3,
            "z": 0.9
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.9,
            "y": 0.3,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.3,
            "z": 1.0
        },
        "positionY": 0.15,
        "scale": {
            "x": 1.0,
            "y": 0.3,
            "z": 1.0
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.35,
            "z": 0.8
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.8,
            "y": 0.35,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.35,
            "z": 0.9
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.9,
            "y": 0.35,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.35,
            "z": 1.0
        },
        "positionY": 0.175,
        "scale": {
            "x": 1.0,
            "y": 0.35,
            "z": 1.0
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.4,
            "z": 0.9
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.9,
            "y": 0.4,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.4,
            "z": 1.0
        },
        "positionY": 0.2,
        "scale": {
            "x": 1.0,
            "y": 0.4,
            "z": 1.0
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.45,
            "z": 1.0
        },
        "positionY": 0.225,
        "scale": {
            "x": 1.0,
            "y": 0.45,
            "z": 1.0
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_RECTANGULAR_PRISM_WIDE = {
    "type": "cube",
    "shape": ["rectangular prism"],
    "chooseSize": [{
        "mass": 2.5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        },
        "positionY": 0.125,
        "scale": {
            "x": 0.5,
            "y": 0.25,
            "z": 0.5
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.3,
            "z": 0.5
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.5,
            "y": 0.3,
            "z": 0.5
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.35,
            "z": 0.5
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.5,
            "y": 0.35,
            "z": 0.5
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.4,
            "z": 0.5
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.5,
            "y": 0.4,
            "z": 0.5
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.45,
            "z": 0.5
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.5,
            "y": 0.45,
            "z": 0.5
        }
    }, {
        "mass": 3,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.6,
            "y": 0.3,
            "z": 0.6
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.35,
            "z": 0.6
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.6,
            "y": 0.35,
            "z": 0.6
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.4,
            "z": 0.6
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.6,
            "y": 0.4,
            "z": 0.6
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.45,
            "z": 0.6
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.6,
            "y": 0.45,
            "z": 0.6
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.5,
            "z": 0.6
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.6,
            "y": 0.5,
            "z": 0.6
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.55,
            "z": 0.6
        },
        "positionY": 0.275,
        "scale": {
            "x": 0.6,
            "y": 0.55,
            "z": 0.6
        }
    }, {
        "mass": 3.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        },
        "positionY": 0.175,
        "scale": {
            "x": 0.7,
            "y": 0.35,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.4,
            "z": 0.7
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.7,
            "y": 0.4,
            "z": 0.7
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.45,
            "z": 0.7
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.7,
            "y": 0.45,
            "z": 0.7
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.5,
            "z": 0.7
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.7,
            "y": 0.5,
            "z": 0.7
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.55,
            "z": 0.7
        },
        "positionY": 0.275,
        "scale": {
            "x": 0.7,
            "y": 0.55,
            "z": 0.7
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.6,
            "z": 0.7
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.7,
            "y": 0.6,
            "z": 0.7
        }
    }, {
        "mass": 6.5,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.65,
            "z": 0.7
        },
        "positionY": 0.325,
        "scale": {
            "x": 0.7,
            "y": 0.65,
            "z": 0.7
        }
    }, {
        "mass": 4,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        },
        "positionY": 0.2,
        "scale": {
            "x": 0.8,
            "y": 0.4,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.45,
            "z": 0.8
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.8,
            "y": 0.45,
            "z": 0.8
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.5,
            "z": 0.8
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.8,
            "y": 0.5,
            "z": 0.8
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.55,
            "z": 0.8
        },
        "positionY": 0.275,
        "scale": {
            "x": 0.8,
            "y": 0.55,
            "z": 0.8
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.6,
            "z": 0.8
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.8,
            "y": 0.6,
            "z": 0.8
        }
    }, {
        "mass": 6.5,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.65,
            "z": 0.8
        },
        "positionY": 0.325,
        "scale": {
            "x": 0.8,
            "y": 0.65,
            "z": 0.8
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.7,
            "z": 0.8
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.8,
            "y": 0.7,
            "z": 0.8
        }
    }, {
        "mass": 7.5,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.75,
            "z": 0.8
        },
        "positionY": 0.375,
        "scale": {
            "x": 0.8,
            "y": 0.75,
            "z": 0.8
        }
    }, {
        "mass": 4.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        },
        "positionY": 0.225,
        "scale": {
            "x": 0.9,
            "y": 0.45,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.5,
            "z": 0.9
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.9,
            "y": 0.5,
            "z": 0.9
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.55,
            "z": 0.9
        },
        "positionY": 0.275,
        "scale": {
            "x": 0.9,
            "y": 0.55,
            "z": 0.9
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.6,
            "z": 0.9
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.9,
            "y": 0.6,
            "z": 0.9
        }
    }, {
        "mass": 6.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.65,
            "z": 0.9
        },
        "positionY": 0.325,
        "scale": {
            "x": 0.9,
            "y": 0.65,
            "z": 0.9
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.7,
            "z": 0.9
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.9,
            "y": 0.7,
            "z": 0.9
        }
    }, {
        "mass": 7.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.75,
            "z": 0.9
        },
        "positionY": 0.375,
        "scale": {
            "x": 0.9,
            "y": 0.75,
            "z": 0.9
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.8,
            "z": 0.9
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.9,
            "y": 0.8,
            "z": 0.9
        }
    }, {
        "mass": 8.5,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.85,
            "z": 0.9
        },
        "positionY": 0.425,
        "scale": {
            "x": 0.9,
            "y": 0.85,
            "z": 0.9
        }
    }, {
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        },
        "positionY": 0.25,
        "scale": {
            "x": 1.0,
            "y": 0.5,
            "z": 1.0
        }
    }, {
        "mass": 5.5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.55,
            "z": 1.0
        },
        "positionY": 0.275,
        "scale": {
            "x": 1.0,
            "y": 0.55,
            "z": 1.0
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.6,
            "z": 1.0
        },
        "positionY": 0.3,
        "scale": {
            "x": 1.0,
            "y": 0.6,
            "z": 1.0
        }
    }, {
        "mass": 6.5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.65,
            "z": 1.0
        },
        "positionY": 0.325,
        "scale": {
            "x": 1.0,
            "y": 0.65,
            "z": 1.0
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.7,
            "z": 1.0
        },
        "positionY": 0.35,
        "scale": {
            "x": 1.0,
            "y": 0.7,
            "z": 1.0
        }
    }, {
        "mass": 7.5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.75,
            "z": 1.0
        },
        "positionY": 0.375,
        "scale": {
            "x": 1.0,
            "y": 0.75,
            "z": 1.0
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.8,
            "z": 1.0
        },
        "positionY": 0.4,
        "scale": {
            "x": 1.0,
            "y": 0.8,
            "z": 1.0
        }
    }, {
        "mass": 8.5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.85,
            "z": 1.0
        },
        "positionY": 0.425,
        "scale": {
            "x": 1.0,
            "y": 0.85,
            "z": 1.0
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.9,
            "z": 1.0
        },
        "positionY": 0.45,
        "scale": {
            "x": 1.0,
            "y": 0.9,
            "z": 1.0
        }
    }, {
        "mass": 9.5,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 0.95,
            "z": 1.0
        },
        "positionY": 0.475,
        "scale": {
            "x": 1.0,
            "y": 0.95,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_SQUARE_FRUSTUM = {
    "type": "square_frustum",
    "shape": ["square frustum"],
    "chooseSize": [{
        "mass": 5,
        "size": "medium",
        "dimensions": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        },
        "positionY": 0.25,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "mass": 6,
        "size": "medium",
        "dimensions": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        },
        "positionY": 0.3,
        "scale": {
            "x": 0.6,
            "y": 0.6,
            "z": 0.6
        }
    }, {
        "mass": 7,
        "size": "medium",
        "dimensions": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        },
        "positionY": 0.35,
        "scale": {
            "x": 0.7,
            "y": 0.7,
            "z": 0.7
        }
    }, {
        "mass": 8,
        "size": "medium",
        "dimensions": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        },
        "positionY": 0.4,
        "scale": {
            "x": 0.8,
            "y": 0.8,
            "z": 0.8
        }
    }, {
        "mass": 9,
        "size": "medium",
        "dimensions": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        },
        "positionY": 0.45,
        "scale": {
            "x": 0.9,
            "y": 0.9,
            "z": 0.9
        }
    }, {
        "mass": 10,
        "size": "medium",
        "dimensions": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        },
        "positionY": 0.5,
        "scale": {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }
    }],
    "chooseMaterial": [{
        "materialCategory": ["intuitive_physics_block"],
        "salientMaterials": ["wood"],
    }, {
        "materialCategory": ["intuitive_physics_plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "materialCategory": ["intuitive_physics_wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["intuitive_physics_metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable"]
}


_POLE = {
    "id": "pole_",
    "role": "structural",
    "color": ["magenta", "cyan"],
    "info": [],
    "shape": ["pole"],
    "size": "medium",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 50,
    "materials": ["Custom/Materials/Magenta"],
    "dimensions": {
        "x": 0.2,
        "y": 10,
        "z": 0.2
    },
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 5,
            "z": 0
        },
        "scale": {
            "x": 0.2,
            "y": 5,
            "z": 0.2
        }
    }],
    "moves": [{
        "stepBegin": 0,
        "stepEnd": 0,
        "vector": {
            "x": 0,
            "y": POLE_MOVE_AMOUNT,
            "z": 0
        }
    }, {
        "stepBegin": 0,
        "stepEnd": 0,
        "vector": {
            "x": 0,
            "y": -POLE_MOVE_AMOUNT,
            "z": 0
        }
    }],
    "changeMaterials": [{
        "stepBegin": 0,
        "materials": ["Custom/Materials/Cyan"]
    }]
}


_ASYMMETRIC_TARGET_LIST = [
    _LETTER_L_NARROW,
    _LETTER_L_WIDE,
    _TRIANGLE_90_45_45,
    _TRIANGLE_90_60_30
]


_SYMMETRIC_TARGET_LIST = [
    _CIRCLE_FRUSTUM,
    _CONE,
    _CUBE,
    _CYLINDER,
    _PYRAMID,
    _RECTANGULAR_PRISM_THIN,
    _RECTANGULAR_PRISM_WIDE,
    _SQUARE_FRUSTUM
]


def _get(prop: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Returns a deep copy of the global property with the given name
    (normally either an object definition or an object definition list)."""
    return copy.deepcopy(globals()['_' + prop])


def create_pole_template(show_step: int) -> List[Dict[str, Any]]:
    pole = _get('POLE')
    pole['id'] = pole['id'] + str(uuid.uuid4())
    pole['shows'][0]['stepBegin'] = show_step
    pole['moves'][0]['stepBegin'] = show_step
    return pole


def get_asymmetric_target_definition_list() -> List[Dict[str, Any]]:
    return _get('ASYMMETRIC_TARGET_LIST')


def get_symmetric_target_definition_list() -> List[Dict[str, Any]]:
    return _get('SYMMETRIC_TARGET_LIST')


def get_visible_support_object_definition() -> Dict[str, Any]:
    return _get('VISIBLE_SUPPORT')
