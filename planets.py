from pygame import Vector2

# astral bodies
BODIES = {
    "Orion": {  # star
        "bodyRadius": 3000,
        "cloudRadius": 3050,
        "bodyPos": Vector2(16410, 5917),
        "lightDirection": [0.0, 0.0, 0.0],
    },
    "Albasee": {
        "bodyRadius": 600,  # pixels
        "cloudRadius": 610,
        "bodyPos": Vector2(11_300, 27_450),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Vulakit": {
        "bodyRadius": 250,
        "cloudRadius": 300,
        "bodyPos": Vector2(9_000, 7_750),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Platee": {
        "bodyRadius": 350,
        "cloudRadius": 370,
        "bodyPos": Vector2(0, 0),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
}
