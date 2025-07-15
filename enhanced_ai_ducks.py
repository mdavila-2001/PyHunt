"""
Enhanced AI Ducks System for PyHunt
Advanced AI behavior with machine learning-inspired patterns
"""
import pygame
import random
import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class BehaviorState(Enum):
    """Different AI behavior states"""
    NORMAL = "normal"
    EVASIVE = "evasive"
    AGGRESSIVE = "aggressive"
    PATROL = "patrol"
    HUNTING = "hunting"
    RETREATING = "retreating"

@dataclass
class AIMemory:
    """AI memory for learning patterns"""
    player_positions: List[Tuple[int, int]]
    successful_evasions: List[Tuple[int, int]]
    dangerous_areas: List[Tuple[int, int, float]]  # x, y, danger_level
    last_hit_position: Optional[Tuple[int, int]]
    player_accuracy: float
    player_speed: float
    
    def __post_init__(self):
        if self.player_positions is None:
            self.player_positions = []
        if self.successful_evasions is None:
            self.successful_evasions = []
        if self.dangerous_areas is None:
            self.dangerous_areas = []

class EnhancedAIDuck(pygame.sprite.Sprite):
    """Enhanced AI duck with advanced behavior patterns"""
    
    def __init__(self, game, color: str, ai_level: int = 1):
        super().__init__()
        self.game = game
        self.color = color
        self.ai_level = ai_level
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
        self.die_duration = 1000
        
        # Enhanced AI attributes
        self.behavior_state = BehaviorState.NORMAL
        self.state_timer = 0
        self.state_duration = random.randint(3000, 8000)
        
        # Movement
        self.base_speed = 100
        self.speed = self.base_speed + (ai_level * 15)
        self.direction = random.choice([-1, 1])
        self.vertical_speed = random.uniform(-40, 40)
        self.target_position = None
        self.path_points = []
        
        # AI Memory and Learning
        self.memory = AIMemory(
            player_positions=[],
            successful_evasions=[],
            dangerous_areas=[],
            last_hit_position=None,
            player_accuracy=0.5,
            player_speed=0.0
        )
        
        # Personality traits (affects behavior)
        self.courage = random.uniform(0.3, 0.8)  # Higher = more aggressive
        self.intelligence = random.uniform(0.5, 1.0)  # Higher = better learning
        self.agility = random.uniform(0.6, 1.0)  # Higher = better evasion
        
        # Advanced AI features
        self.prediction_horizon = 2.0  # seconds
        self.evasion_cooldown = 0
        self.last_evasion_time = 0
        self.threat_assessment = 0.0
        
        # Position
        self.spawn_position()
        
    def _get_points(self) -> int:
        """Get points based on duck color and AI level"""
        base_points = {
            'black': 75,
            'red': 50,
            'blue': 25
        }
        base = base_points.get(self.color, 25)
        return base + (self.ai_level * 10)
        
    def spawn_position(self):
        """Set initial spawn position"""
        if self.direction == 1:  # Moving right
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(50, 480 // 2)
        else:  # Moving left
            self.rect.x = 640
            self.rect.y = random.randint(50, 480 // 2)
            
    def update(self, delta_time: float):
        """Update duck state with enhanced AI behavior"""
        if self.alive:
            self.update_ai_behavior(delta_time)
        elif self.dying:
            self.update_dying(delta_time)
            
        self.animate(delta_time)
        
    def update_ai_behavior(self, delta_time: float):
        """Update enhanced AI behavior"""
        # Update timers
        self.state_timer += delta_time * 1000
        self.evasion_cooldown = max(0, self.evasion_cooldown - delta_time * 1000)
        
        # Update memory
        self._update_memory(delta_time)
        
        # Assess current threat level
        self._assess_threat()
        
        # Change behavior state if needed
        if self.state_timer > self.state_duration:
            self._change_behavior_state()
            
        # Execute behavior based on current state
        self._execute_behavior(delta_time)
        
        # Apply movement
        self._apply_movement(delta_time)
        
        # Handle screen bounds
        self._handle_screen_bounds()
        
    def _update_memory(self, delta_time: float):
        """Update AI memory with current information"""
        player_pos = self.game.get_player_position()
        
        if player_pos:
            # Update player positions (keep last 10)
            self.memory.player_positions.append(player_pos)
            if len(self.memory.player_positions) > 10:
                self.memory.player_positions.pop(0)
                
            # Calculate player speed
            if len(self.memory.player_positions) >= 2:
                prev_pos = self.memory.player_positions[-2]
                current_pos = self.memory.player_positions[-1]
                distance = math.sqrt((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)
                self.memory.player_speed = distance / delta_time
                
    def _assess_threat(self):
        """Assess current threat level from player"""
        player_pos = self.game.get_player_position()
        if not player_pos:
            self.threat_assessment = 0.0
            return
            
        # Calculate distance to player
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Base threat from distance
        distance_threat = max(0, 1.0 - (distance / 300.0))
        
        # Threat from player accuracy
        accuracy_threat = self.memory.player_accuracy / 100.0
        
        # Threat from player speed (fast movement = more dangerous)
        speed_threat = min(1.0, self.memory.player_speed / 500.0)
        
        # Combine threats
        self.threat_assessment = (distance_threat * 0.4 + 
                                accuracy_threat * 0.4 + 
                                speed_threat * 0.2)
                                
    def _change_behavior_state(self):
        """Change to a new behavior state"""
        # Determine new state based on threat level and personality
        if self.threat_assessment > 0.7 and self.courage < 0.6:
            new_state = BehaviorState.EVASIVE
        elif self.threat_assessment < 0.3 and self.courage > 0.7:
            new_state = BehaviorState.AGGRESSIVE
        elif self.threat_assessment > 0.5:
            new_state = BehaviorState.PATROL
        else:
            new_state = random.choice(list(BehaviorState))
            
        # Don't change to same state
        if new_state != self.behavior_state:
            self.behavior_state = new_state
            self.state_timer = 0
            self.state_duration = random.randint(3000, 8000)
            
    def _execute_behavior(self, delta_time: float):
        """Execute behavior based on current state"""
        if self.behavior_state == BehaviorState.NORMAL:
            self._normal_behavior(delta_time)
        elif self.behavior_state == BehaviorState.EVASIVE:
            self._evasive_behavior(delta_time)
        elif self.behavior_state == BehaviorState.AGGRESSIVE:
            self._aggressive_behavior(delta_time)
        elif self.behavior_state == BehaviorState.PATROL:
            self._patrol_behavior(delta_time)
        elif self.behavior_state == BehaviorState.HUNTING:
            self._hunting_behavior(delta_time)
        elif self.behavior_state == BehaviorState.RETREATING:
            self._retreating_behavior(delta_time)
            
    def _normal_behavior(self, delta_time: float):
        """Normal flying behavior"""
        # Slight random movement
        if random.random() < 0.01:
            self.vertical_speed += random.uniform(-20, 20)
            self.vertical_speed = max(-60, min(60, self.vertical_speed))
            
    def _evasive_behavior(self, delta_time: float):
        """Evasive behavior - avoid player"""
        if self.evasion_cooldown <= 0:
            player_pos = self.game.get_player_position()
            if player_pos:
                # Calculate escape direction
                dx = self.rect.centerx - player_pos[0]
                dy = self.rect.centery - player_pos[1]
                
                # Normalize and apply
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    escape_x = (dx / distance) * self.speed * 1.5
                    escape_y = (dy / distance) * self.speed * 1.5
                    
                    # Apply escape movement
                    self.rect.x += escape_x * delta_time
                    self.rect.y += escape_y * delta_time
                    
                    # Update direction
                    if escape_x > 0:
                        self.direction = 1
                    else:
                        self.direction = -1
                        
                    self.evasion_cooldown = 1000
                    
                    # Record successful evasion
                    self.memory.successful_evasions.append(player_pos)
                    if len(self.memory.successful_evasions) > 5:
                        self.memory.successful_evasions.pop(0)
                        
    def _aggressive_behavior(self, delta_time: float):
        """Aggressive behavior - move towards player"""
        player_pos = self.game.get_player_position()
        if player_pos and self.courage > 0.6:
            # Calculate direction to player
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            
            # Move towards player with some randomness
            if abs(dx) > 20:
                self.direction = 1 if dx > 0 else -1
                self.rect.x += self.direction * self.speed * 0.8 * delta_time
                
            if abs(dy) > 20:
                self.vertical_speed = 40 if dy > 0 else -40
                
    def _patrol_behavior(self, delta_time: float):
        """Patrol behavior - systematic movement"""
        # Create patrol path if none exists
        if not self.path_points:
            self._generate_patrol_path()
            
        # Follow patrol path
        if self.path_points:
            target = self.path_points[0]
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            
            # Move towards target
            if abs(dx) > 10:
                self.direction = 1 if dx > 0 else -1
                self.rect.x += self.direction * self.speed * 0.6 * delta_time
                
            if abs(dy) > 10:
                self.vertical_speed = 30 if dy > 0 else -30
                
            # Check if reached target
            if abs(dx) < 20 and abs(dy) < 20:
                self.path_points.pop(0)
                
    def _hunting_behavior(self, delta_time: float):
        """Hunting behavior - search for player"""
        # Predict player position
        predicted_pos = self._predict_player_position()
        if predicted_pos:
            # Move towards predicted position
            dx = predicted_pos[0] - self.rect.centerx
            dy = predicted_pos[1] - self.rect.centery
            
            if abs(dx) > 15:
                self.direction = 1 if dx > 0 else -1
                self.rect.x += self.direction * self.speed * 0.7 * delta_time
                
            if abs(dy) > 15:
                self.vertical_speed = 35 if dy > 0 else -35
                
    def _retreating_behavior(self, delta_time: float):
        """Retreating behavior - move away from danger"""
        # Move towards screen edges
        if self.rect.centerx < 320:  # Left side
            self.direction = -1
        else:  # Right side
            self.direction = 1
            
        self.rect.x += self.direction * self.speed * 1.2 * delta_time
        
        # Move up
        self.vertical_speed = -50
        
    def _generate_patrol_path(self):
        """Generate patrol path points"""
        self.path_points = []
        num_points = random.randint(3, 6)
        
        for i in range(num_points):
            x = random.randint(100, 540)
            y = random.randint(50, 300)
            self.path_points.append((x, y))
            
    def _predict_player_position(self) -> Optional[Tuple[int, int]]:
        """Predict player position based on movement history"""
        if len(self.memory.player_positions) < 3:
            return None
            
        # Simple linear prediction
        recent_positions = self.memory.player_positions[-3:]
        
        # Calculate velocity
        vx = (recent_positions[-1][0] - recent_positions[0][0]) / 2
        vy = (recent_positions[-1][1] - recent_positions[0][1]) / 2
        
        # Predict future position
        last_pos = recent_positions[-1]
        predicted_x = last_pos[0] + vx * self.prediction_horizon
        predicted_y = last_pos[1] + vy * self.prediction_horizon
        
        # Clamp to screen bounds
        predicted_x = max(0, min(640, predicted_x))
        predicted_y = max(0, min(480, predicted_y))
        
        return (int(predicted_x), int(predicted_y))
        
    def _apply_movement(self, delta_time: float):
        """Apply movement based on current direction and speed"""
        self.rect.x += self.direction * self.speed * delta_time
        self.rect.y += self.vertical_speed * delta_time
        
    def _handle_screen_bounds(self):
        """Handle screen boundary collisions"""
        # Horizontal bounds
        if self.rect.left < -self.rect.width or self.rect.right > 640 + self.rect.width:
            self.direction *= -1
            self.rect.x = max(-self.rect.width, min(self.rect.x, 640))
            
        # Vertical bounds
        if self.rect.top < 0 or self.rect.bottom > 480:
            self.vertical_speed *= -1
            self.rect.y = max(0, min(self.rect.y, 480 - self.rect.height))
            
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
            
    def hit(self):
        """Handle duck being hit"""
        if self.alive:
            self.alive = False
            self.dying = True
            self.die_timer = 0
            
            # Update memory with hit position
            player_pos = self.game.get_player_position()
            if player_pos:
                self.memory.last_hit_position = player_pos
                
            # Play hit sound
            self.game.asset_manager.beep_sound.play()
            
    def freeze(self):
        """Freeze duck movement (for power-ups)"""
        self.speed = 0
        self.vertical_speed = 0
        
    def unfreeze(self):
        """Unfreeze duck movement"""
        self.speed = self.base_speed + (self.ai_level * 15)
        self.vertical_speed = random.uniform(-40, 40)
        
    def animate(self, delta_time: float):
        """Animate duck sprite"""
        self.animation_timer += delta_time
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.sprites[self.current_animation])
            
        # Update image
        self.image = self.sprites[self.current_animation][self.animation_frame]
        
    def get_ai_info(self) -> Dict[str, Any]:
        """Get AI information for debugging/display"""
        return {
            'behavior_state': self.behavior_state.value,
            'threat_assessment': self.threat_assessment,
            'courage': self.courage,
            'intelligence': self.intelligence,
            'agility': self.agility,
            'ai_level': self.ai_level,
            'memory_size': len(self.memory.player_positions)
        } 