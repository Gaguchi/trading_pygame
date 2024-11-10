SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

SETTLEMENTS = [
    {"name": "King's Haven", "type": "castle", "x": SCREEN_WIDTH//2, "y": SCREEN_HEIGHT//2},
    {"name": "Riverwood", "type": "town"},
    {"name": "Oakvale", "type": "town"},
    {"name": "Millbrook", "type": "village"},
    {"name": "Ironforge", "type": "village"},
    {"name": "Meadowbrook", "type": "village"}
]

SETTLEMENT_COLORS = {
    'castle': (120, 120, 180),
    'town': (180, 140, 100),
    'village': (150, 120, 90)
}

SETTLEMENT_SIZES = {
    'castle': 30,
    'town': 25,
    'village': 20
}
