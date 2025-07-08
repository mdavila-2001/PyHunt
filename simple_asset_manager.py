"""
Simple Asset Manager for AI Duck Hunt
Handles loading and managing all game assets
"""
import pygame
import os
from typing import Dict, List, Optional
from pygame import mixer

class AssetManager:
    """Manages all game assets"""
    
    def __init__(self):
        # Initialize pygame mixer
        mixer.init()
        
        # Asset storage
        self.images = {}
        self.sounds = {}
        self.duck_sprites = {}
        
        # Load all assets
        self.load_all_assets()
        
    def load_all_assets(self):
        """Load all game assets"""
        self._create_directories()
        self._load_sounds()
        self._load_images()
        self._load_duck_sprites()
        
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = ['Sprites', 'Sounds']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
    def _load_sounds(self):
        """Load all sound files"""
        sound_files = {
            'shot_sound': 'shot.wav',
            'beep_sound': 'beep.wav'
        }
        
        for key, filename in sound_files.items():
            self.sounds[key] = self._load_sound(filename)
            
    def _load_images(self):
        """Load all image files"""
        image_files = {
            'cursor_img': 'cursor.png',
            'foreground_img': 'foreground.png',
            'paused_img': 'paused.png',
            'background_img': 'background.png'  # In root directory
        }
        
        for key, filename in image_files.items():
            self.images[key] = self._load_image(filename)
            
    def _load_duck_sprites(self):
        """Load all duck sprite animations"""
        colors = ['blue', 'red', 'black']
        
        for color in colors:
            self.duck_sprites[color] = self._load_duck_sprites_for_color(color)
            
    def _load_sound(self, filename: str) -> mixer.Sound:
        """Load a sound file"""
        try:
            path = os.path.join('Sounds', filename)
            return mixer.Sound(path)
        except Exception as e:
            print(f"Warning: Could not load sound {filename}: {e}")
            # Return a silent sound
            return mixer.Sound(buffer=bytearray(44))
            
    def _load_image(self, filename: str, scale: float = 1.0, use_alpha: bool = True) -> pygame.Surface:
        """Load an image file"""
        try:
            # Try loading from Sprites directory first
            path = os.path.join('Sprites', filename)
            if not os.path.exists(path):
                # If not found in Sprites, try root directory
                path = filename
                
            if use_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
                
            if scale != 1.0:
                new_width = int(image.get_width() * scale)
                new_height = int(image.get_height() * scale)
                image = pygame.transform.scale(image, (new_width, new_height))
                
            return image
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            # Return a placeholder surface
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 255))  # Magenta placeholder
            return surf
            
    def _load_duck_sprites_for_color(self, color: str) -> Dict[str, List[pygame.Surface]]:
        """Load all sprites for a duck of a specific color"""
        sprites = {}
        
        # Define sprite categories and their frame ranges
        sprite_categories = {
            'fly_right': [1, 2, 3],
            'fly_straight_right': [4, 5, 6],
            'fly_left': [7, 8, 9],
            'fly_straight_left': [10, 11, 12],
            'die': ['Die1', 'Die2', 'Die3']
        }
        
        for category, frame_numbers in sprite_categories.items():
            sprites[category] = []
            
            for frame_num in frame_numbers:
                if category == 'die':
                    filename = f"{color}/duck{frame_num}.png"
                else:
                    filename = f"{color}/duck{frame_num}.png"
                    
                sprite = self._load_image(filename)
                sprites[category].append(sprite)
                
        return sprites
        
    def get_image(self, key: str) -> pygame.Surface:
        """Get an image by key"""
        return self.images.get(key)
        
    def get_sound(self, key: str) -> mixer.Sound:
        """Get a sound by key"""
        return self.sounds.get(key)
        
    def get_duck_sprites(self, color: str) -> Dict[str, List[pygame.Surface]]:
        """Get duck sprites for a specific color"""
        return self.duck_sprites.get(color, {})
        
    def get_all_duck_sprites(self) -> Dict[str, Dict[str, List[pygame.Surface]]]:
        """Get all duck sprites"""
        return self.duck_sprites
        
    # Property accessors for convenience
    @property
    def cursor_img(self) -> pygame.Surface:
        return self.get_image('cursor_img')
        
    @property
    def background_img(self) -> pygame.Surface:
        return self.get_image('background_img')
        
    @property
    def foreground_img(self) -> pygame.Surface:
        return self.get_image('foreground_img')
        
    @property
    def paused_img(self) -> pygame.Surface:
        return self.get_image('paused_img')
        
    @property
    def shot_sound(self) -> mixer.Sound:
        return self.get_sound('shot_sound')
        
    @property
    def beep_sound(self) -> mixer.Sound:
        return self.get_sound('beep_sound') 