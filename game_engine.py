"""
Game Engine Module
Handles core game logic, sprites, and physics
"""
import pygame
import os
import random
import math
from typing import List, Dict, Any, Optional

# Game constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

class Duck(pygame.sprite.Sprite):
    """Duck sprite with animation and physics"""
    
    def __init__(self, game, color: str):
        super().__init__()
        self.game = game
        self.color = color
        self.points = self._get_points()
        
        # Load sprites
        self.sprites = game.asset_manager.duck_sprites[color]
        self.current_animation = 'fly_right'
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Set initial image
        self.image = self.sprites[self.current_animation][0]
        self.rect = self.image.get_rect()
        
        # Physics
        self.alive = True
        self.dying = False
        self.die_timer = 0
        self.die_duration = 1000  # milliseconds
        
        # Movement
        self.speed = random.uniform(100, 200)
        self.direction = random.choice([-1, 1])  # -1 for left, 1 for right
        self.vertical_speed = random.uniform(-50, 50)
        
        # Position
        self.spawn_position()
        
        # State
        self.state_timer = 0
        self.change_direction_timer = 0
        
    def _get_points(self) -> int:
        """Get points based on duck color"""
        points_map = {
            'black': 75,
            'red': 50,
            'blue': 25
        }
        return points_map.get(self.color, 25)
        
    def spawn_position(self):
        """Set initial spawn position"""
        # Spawn from left or right side
        if self.direction == 1:  # Moving right
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(50, SCREEN_HEIGHT // 2)
        else:  # Moving left
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(50, SCREEN_HEIGHT // 2)
            
    def update(self, delta_time: float):
        """Update duck state"""
        if self.alive:
            self.update_alive(delta_time)
        elif self.dying:
            self.update_dying(delta_time)
            
        self.animate(delta_time)
        
    def update_alive(self, delta_time: float):
        """Update alive duck movement"""
        # Update timers
        self.state_timer += delta_time * 1000
        self.change_direction_timer += delta_time * 1000
        
        # Change direction occasionally
        if self.change_direction_timer > random.randint(2000, 5000):
            self.change_direction()
            self.change_direction_timer = 0
            
        # Move duck
        self.rect.x += self.direction * self.speed * delta_time
        self.rect.y += self.vertical_speed * delta_time
        
        # Bounce off screen edges
        if self.rect.left < -self.rect.width or self.rect.right > SCREEN_WIDTH + self.rect.width:
            self.direction *= -1
            self.rect.x = max(-self.rect.width, min(self.rect.x, SCREEN_WIDTH))
            
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.vertical_speed *= -1
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))
            
        # Update animation based on direction
        if self.direction > 0:
            self.current_animation = 'fly_right'
        else:
            self.current_animation = 'fly_left'
            
    def update_dying(self, delta_time: float):
        """Update dying duck animation"""
        self.die_timer += delta_time * 1000
        self.current_animation = 'die'
        
        # Fall down
        self.rect.y += 200 * delta_time
        
        # Remove when animation is complete
        if self.die_timer > self.die_duration:
            self.kill()
            
    def change_direction(self):
        """Change duck direction"""
        self.direction *= -1
        self.vertical_speed = random.uniform(-50, 50)
        
    def hit(self):
        """Handle duck being hit"""
        if self.alive:
            self.alive = False
            self.dying = True
            self.die_timer = 0
            self.game.beep_sound.play()
            
    def animate(self, delta_time: float):
        """Animate duck sprite"""
        self.animation_timer += delta_time
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.sprites[self.current_animation])
            
        # Update image
        self.image = self.sprites[self.current_animation][self.animation_frame]

class Cursor(pygame.sprite.Sprite):
    """Custom cursor sprite"""
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.asset_manager.cursor_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
    def update(self, position: tuple):
        """Update cursor position"""
        if position and len(position) == 2:
            self.rect.center = position

class Background(pygame.sprite.Sprite):
    """Background sprite"""
    
    def __init__(self, game):
        super().__init__()
        self.image = game.asset_manager.background_img
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

class Foreground(pygame.sprite.Sprite):
    """Foreground sprite"""
    
    def __init__(self, game):
        super().__init__()
        self.image = game.asset_manager.foreground_img
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (0, SCREEN_HEIGHT)

class GameEngine:
    """Core game engine handling game logic"""
    
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
        # Game state
        self.state = MENU
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        self.game_time = 60000  # 60 seconds
        self.start_time = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ducks = pygame.sprite.Group()
        
        # Game objects
        self.cursor = None
        self.background = None
        self.foreground = None
        
        # Game variables
        self.spawn_timer = 0
        self.spawn_delay = 2000  # milliseconds
        
        # Initialize game objects
        self._init_game_objects()
        
    def _init_game_objects(self):
        """Initialize game objects"""
        # Create cursor
        self.cursor = Cursor(self)
        self.all_sprites.add(self.cursor)
        
        # Create background and foreground
        self.background = Background(self)
        self.foreground = Foreground(self)
        self.all_sprites.add(self.background)
        self.all_sprites.add(self.foreground)
        
    def start_game(self):
        """Start a new game"""
        self.state = PLAYING
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        self.start_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        
        # Clear existing ducks
        for duck in self.ducks:
            duck.kill()
            
    def reset_game(self):
        """Reset game to menu"""
        self.state = MENU
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        
        # Clear ducks
        for duck in self.ducks:
            duck.kill()
            
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING
            
    def spawn_duck(self):
        """Spawn a new duck"""
        colors = list(self.asset_manager.duck_sprites.keys())
        weights = [0.5, 0.3, 0.2]  # Probability weights
        color = random.choices(colors, weights=weights)[0]
        
        duck = Duck(self, color)
        self.ducks.add(duck)
        self.all_sprites.add(duck)
        self.total_ducks += 1
        
    def shoot(self, position: tuple):
        """Handle shooting at position"""
        self.total_shots += 1
        self.asset_manager.shot_sound.play()
        
        # Check for duck hits
        for duck in self.ducks:
            if duck.alive and duck.rect.collidepoint(position):
                duck.hit()
                self.score += duck.points
                self.ducks_shot += 1
                break
                
    def update(self, delta_time: float):
        """Update game state"""
        if self.state != PLAYING:
            return
            
        # Update spawn timer
        self.spawn_timer += delta_time * 1000
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_duck()
            self.spawn_timer = 0
            
        # Update all sprites except cursor
        for sprite in self.all_sprites:
            if isinstance(sprite, Cursor):
                continue
            sprite.update(delta_time)
        # El cursor se actualiza solo con update_cursor()
        
        # Check game time
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.game_time:
            self.state = GAME_OVER
            
    def update_cursor(self, position: tuple):
        """Update cursor position"""
        if self.cursor and position and len(position) == 2:
            self.cursor.update(position)
            
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information"""
        current_time = pygame.time.get_ticks()
        time_remaining = max(0, self.game_time - (current_time - self.start_time))
        
        return {
            "state": self.state,
            "score": self.score,
            "ducks_shot": self.ducks_shot,
            "total_shots": self.total_shots,
            "accuracy": (self.ducks_shot / max(1, self.total_shots)) * 100,
            "time_remaining": time_remaining,
            "total_ducks": self.total_ducks
        }
        
    def get_sprites(self) -> pygame.sprite.LayeredUpdates:
        """Get sprite group for rendering"""
        return self.all_sprites 