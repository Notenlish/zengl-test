from pygame import Vector2

# astral bodies
BODIES = {
    "Orion": {  # star
        "bodyRadius": 1000,
        "cloudRadius": 1050,
        "bodyPos": Vector2(16410, 5917),
        "lightDirection": [0.3, 0.6, -1.0],
        "isStar":True
    },
    "Albasee": {
        "bodyRadius": 500,  # pixels
        "cloudRadius": 530,
        "bodyPos": Vector2(11_300, 27_450),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Vulakit": {
        "bodyRadius": 200,
        "cloudRadius": 250,
        "bodyPos": Vector2(9_000, 7_750),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
    "Platee": {
        "bodyRadius": 330,
        "cloudRadius": 350,
        "bodyPos": Vector2(30083, 11523),
        "lightDirection": [0.3, 0.6, -1.0],  # I'll mess with this later
    },
}
