"""
Power-up System for PyHunt
Adds special abilities and temporary boosts to the game
"""
import random
import pygame
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class PowerUpType(Enum):
    """Types of power-ups available"""
    RAPID_FIRE = "rapid_fire"
    DOUBLE_POINTS = "double_points"
    SLOW_MOTION = "slow_motion"
    MULTI_SHOT = "multi_shot"
    SHIELD = "shield"
    MAGNET = "magnet"
    FREEZE = "freeze"

class PowerUp(pygame.sprite.Sprite):
    """Power-up sprite that falls from the sky"""
    
    def __init__(self, powerup_type: PowerUpType, position: Tuple[int, int]):
        super().__init__()
        self.powerup_type = powerup_type
        self.duration = self._get_duration()
        self.icon = self._get_icon()
        
        # Create visual representation
        self.image = self._create_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = position
        
        # Physics
        self.velocity_y = 50
        self.rotation = 0
        self.rotation_speed = 2
        
    def _get_duration(self) -> int:
        """Get power-up duration in milliseconds"""
        durations = {
            PowerUpType.RAPID_FIRE: 10000,      # 10 seconds
            PowerUpType.DOUBLE_POINTS: 15000,   # 15 seconds
            PowerUpType.SLOW_MOTION: 8000,      # 8 seconds
            PowerUpType.MULTI_SHOT: 12000,      # 12 seconds
            PowerUpType.SHIELD: 10000,          # 10 seconds
            PowerUpType.MAGNET: 12000,          # 12 seconds
            PowerUpType.FREEZE: 6000            # 6 seconds
        }
        return durations.get(self.powerup_type, 10000)
        
    def _get_icon(self) -> str:
        """Get power-up icon"""
        icons = {
            PowerUpType.RAPID_FIRE: "⚡",
            PowerUpType.DOUBLE_POINTS: "💰",
            PowerUpType.SLOW_MOTION: "⏰",
            PowerUpType.MULTI_SHOT: "🎯",
            PowerUpType.SHIELD: "🛡️",
            PowerUpType.MAGNET: "🧲",
            PowerUpType.FREEZE: "❄️"
        }
        return icons.get(self.powerup_type, "❓")
        
    def _create_sprite(self) -> pygame.Surface:
        """Create power-up sprite surface"""
        # Create a colored circle with icon
        size = 32
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Background color based on type
        colors = {
            PowerUpType.RAPID_FIRE: (255, 165, 0),    # Orange
            PowerUpType.DOUBLE_POINTS: (255, 215, 0), # Gold
            PowerUpType.SLOW_MOTION: (0, 191, 255),   # Deep sky blue
            PowerUpType.MULTI_SHOT: (255, 0, 255),    # Magenta
            PowerUpType.SHIELD: (0, 255, 0),          # Green
            PowerUpType.MAGNET: (128, 0, 128),        # Purple
            PowerUpType.FREEZE: (173, 216, 230)       # Light blue
        }
        
        color = colors.get(self.powerup_type, (128, 128, 128))
        
        # Draw circle
        pygame.draw.circle(surface, color, (size//2, size//2), size//2)
        pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), size//2, 2)
        
        # Add icon (simplified - just text)
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(self.icon, True, (255, 255, 255))
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface
        
    def update(self, delta_time: float):
        """Update power-up physics"""
        # Fall down
        self.rect.y += self.velocity_y * delta_time
        
        # Rotate
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
            
        # Remove if off screen
        if self.rect.top > 480:
            self.kill()

class PowerUpEffect:
    """Represents an active power-up effect"""
    
    def __init__(self, powerup_type: PowerUpType, duration: int):
        self.powerup_type = powerup_type
        self.duration = duration
        self.remaining_time = duration
        self.active = True
        
    def update(self, delta_time: float):
        """Update effect timer"""
        self.remaining_time -= delta_time * 1000
        if self.remaining_time <= 0:
            self.active = False
            
    def get_remaining_percentage(self) -> float:
        """Get remaining time as percentage"""
        return max(0.0, self.remaining_time / self.duration)

class PowerUpSystem:
    """Main power-up system"""
    
    def __init__(self, game_engine):
        self.game_engine = game_engine
        self.active_effects: List[PowerUpEffect] = []
        self.powerup_sprites = pygame.sprite.Group()
        
        # Spawn settings
        self.spawn_timer = 0
        self.spawn_delay = 15000  # 15 seconds between power-ups
        self.spawn_chance = 0.3   # 30% chance when timer expires
        
        # Effect multipliers
        self.rapid_fire_multiplier = 1.0
        self.points_multiplier = 1.0
        self.time_scale = 1.0
        
    def update(self, delta_time: float):
        """Update power-up system"""
        # Update active effects
        for effect in self.active_effects[:]:
            effect.update(delta_time)
            if not effect.active:
                self.active_effects.remove(effect)
                self._remove_effect(effect.powerup_type)
                
        # Update power-up sprites
        self.powerup_sprites.update(delta_time)
        
        # Spawn new power-ups
        self.spawn_timer += delta_time * 1000
        if self.spawn_timer >= self.spawn_delay:
            if random.random() < self.spawn_chance:
                self.spawn_powerup()
            self.spawn_timer = 0
            
    def spawn_powerup(self):
        """Spawn a random power-up"""
        powerup_types = list(PowerUpType)
        powerup_type = random.choice(powerup_types)
        
        # Random position at top of screen
        x = random.randint(50, 590)
        position = (x, -32)
        
        powerup = PowerUp(powerup_type, position)
        self.powerup_sprites.add(powerup)
        
    def collect_powerup(self, powerup: PowerUp):
        """Collect a power-up and apply its effect"""
        # Remove the power-up sprite
        powerup.kill()
        
        # Apply effect
        self._apply_effect(powerup.powerup_type, powerup.duration)
        
        # Play collection sound (if available)
        if hasattr(self.game_engine.asset_manager, 'powerup_sound'):
            self.game_engine.asset_manager.powerup_sound.play()
            
    def _apply_effect(self, powerup_type: PowerUpType, duration: int):
        """Apply power-up effect"""
        # Remove existing effect of same type
        for effect in self.active_effects[:]:
            if effect.powerup_type == powerup_type:
                self.active_effects.remove(effect)
                self._remove_effect(powerup_type)
                
        # Add new effect
        effect = PowerUpEffect(powerup_type, duration)
        self.active_effects.append(effect)
        
        # Apply immediate effect
        if powerup_type == PowerUpType.RAPID_FIRE:
            self.rapid_fire_multiplier = 3.0
        elif powerup_type == PowerUpType.DOUBLE_POINTS:
            self.points_multiplier = 2.0
        elif powerup_type == PowerUpType.SLOW_MOTION:
            self.time_scale = 0.5
        elif powerup_type == PowerUpType.FREEZE:
            self._freeze_ducks()
            
    def _remove_effect(self, powerup_type: PowerUpType):
        """Remove power-up effect"""
        if powerup_type == PowerUpType.RAPID_FIRE:
            self.rapid_fire_multiplier = 1.0
        elif powerup_type == PowerUpType.DOUBLE_POINTS:
            self.points_multiplier = 1.0
        elif powerup_type == PowerUpType.SLOW_MOTION:
            self.time_scale = 1.0
        elif powerup_type == PowerUpType.FREEZE:
            self._unfreeze_ducks()
            
    def _freeze_ducks(self):
        """Freeze all ducks temporarily"""
        for duck in self.game_engine.ducks:
            if hasattr(duck, 'freeze'):
                duck.freeze()
                
    def _unfreeze_ducks(self):
        """Unfreeze all ducks"""
        for duck in self.game_engine.ducks:
            if hasattr(duck, 'unfreeze'):
                duck.unfreeze()
                
    def get_active_effects(self) -> List[PowerUpEffect]:
        """Get list of active effects"""
        return self.active_effects
        
    def has_effect(self, powerup_type: PowerUpType) -> bool:
        """Check if a specific effect is active"""
        return any(effect.powerup_type == powerup_type and effect.active 
                  for effect in self.active_effects)
                  
    def get_effect_multiplier(self, powerup_type: PowerUpType) -> float:
        """Get multiplier for a specific effect"""
        for effect in self.active_effects:
            if effect.powerup_type == powerup_type and effect.active:
                if powerup_type == PowerUpType.RAPID_FIRE:
                    return self.rapid_fire_multiplier
                elif powerup_type == PowerUpType.DOUBLE_POINTS:
                    return self.points_multiplier
                elif powerup_type == PowerUpType.SLOW_MOTION:
                    return self.time_scale
        return 1.0
        
    def get_sprites(self) -> pygame.sprite.Group:
        """Get power-up sprites for rendering"""
        return self.powerup_sprites
        
    def reset(self):
        """Reset power-up system"""
        self.active_effects.clear()
        self.powerup_sprites.empty()
        self.spawn_timer = 0
        self.rapid_fire_multiplier = 1.0
        self.points_multiplier = 1.0
        self.time_scale = 1.0 