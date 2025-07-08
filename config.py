"""
Configuration file for Duck Hunt with Gesture Recognition
Adjust game parameters here
"""

# Display settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 50
WINDOW_TITLE = "Duck Hunt - Con Reconocimiento de Gestos"

# Game settings
GAME_DURATION = 60000  # 60 seconds in milliseconds
SPAWN_DELAY = 2000  # milliseconds between duck spawns

# Duck settings
DUCK_SPEED_MIN = 100
DUCK_SPEED_MAX = 200
DUCK_VERTICAL_SPEED_MIN = -50
DUCK_VERTICAL_SPEED_MAX = 50
DUCK_DIE_DURATION = 1000  # milliseconds

# Duck points
DUCK_POINTS = {
    'black': 75,
    'red': 50,
    'blue': 25
}

# Duck spawn probabilities (must sum to 1.0)
DUCK_SPAWN_WEIGHTS = {
    'blue': 0.5,   # 50% chance
    'red': 0.3,    # 30% chance
    'black': 0.2   # 20% chance
}

# Gesture detection settings
GESTURE_CONFIDENCE_THRESHOLD = 0.5
GESTURE_MOVEMENT_THRESHOLD = 0.3
GESTURE_COOLDOWN_TIME = 500  # milliseconds

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_ID = 0  # Default camera

# Skin detection HSV ranges (may need adjustment for different lighting)
SKIN_DETECTION = {
    'lower': [0, 20, 70],
    'upper': [20, 255, 255]
}

# Colors
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'LIGHT_BLUE': (135, 206, 250)
}

# UI settings
FONT_SIZES = {
    'SMALL': 18,
    'NORMAL': 24,
    'LARGE': 48
}

# Performance rating thresholds
PERFORMANCE_THRESHOLDS = {
    'EXCELLENT': {'accuracy': 80, 'ducks': 10},
    'VERY_GOOD': {'accuracy': 60, 'ducks': 7},
    'GOOD': {'accuracy': 40, 'ducks': 5},
    'REGULAR': {'accuracy': 20, 'ducks': 3}
} 