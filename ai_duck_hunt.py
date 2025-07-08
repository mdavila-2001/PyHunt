"""
Duck Hunt with Adaptive AI
A modern version where ducks become smarter and faster based on player performance
"""
import pygame
import os
import random
import math
import json
from typing import Dict, List, Any, Optional
from pygame import mixer
from simple_asset_manager import AssetManager

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Game constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

class AIDuck(pygame.sprite.Sprite):
    """AI-powered duck that learns from player behavior"""
    
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
        
        # AI-enhanced movement
        self.base_speed = 100
        self.speed = self.base_speed + (ai_level * 20)  # Speed increases with AI level
        self.direction = random.choice([-1, 1])
        self.vertical_speed = random.uniform(-30, 30)
        
        # AI behavior patterns
        self.behavior_pattern = random.choice(['aggressive', 'evasive', 'predictable', 'unpredictable'])
        self.pattern_timer = 0
        self.pattern_duration = random.randint(2000, 5000)
        
        # Evasion AI
        self.last_player_pos = None
        self.evasion_cooldown = 0
        self.evasion_range = 100 + (ai_level * 10)
        
        # Position
        self.spawn_position()
        
        # State
        self.state_timer = 0
        self.change_direction_timer = 0
        
    def _get_points(self) -> int:
        """Get points based on duck color and AI level"""
        base_points = {
            'black': 75,
            'red': 50,
            'blue': 25
        }
        base = base_points.get(self.color, 25)
        return base + (self.ai_level * 5)  # More points for higher AI levels
        
    def spawn_position(self):
        """Set initial spawn position"""
        if self.direction == 1:  # Moving right
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(50, SCREEN_HEIGHT // 2)
        else:  # Moving left
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(50, SCREEN_HEIGHT // 2)
            
    def update(self, delta_time: float):
        """Update duck state with AI behavior"""
        if self.alive:
            self.update_ai_behavior(delta_time)
        elif self.dying:
            self.update_dying(delta_time)
            
        self.animate(delta_time)
        
    def update_ai_behavior(self, delta_time: float):
        """Update AI-enhanced behavior"""
        # Update timers
        self.state_timer += delta_time * 1000
        self.change_direction_timer += delta_time * 1000
        self.pattern_timer += delta_time * 1000
        self.evasion_cooldown = max(0, self.evasion_cooldown - delta_time * 1000)
        
        # Get current player position
        current_player_pos = self.game.get_player_position()
        
        # AI behavior based on pattern
        if self.behavior_pattern == 'aggressive':
            self.aggressive_behavior(current_player_pos, delta_time)
        elif self.behavior_pattern == 'evasive':
            self.evasive_behavior(current_player_pos, delta_time)
        elif self.behavior_pattern == 'predictable':
            self.predictable_behavior(delta_time)
        elif self.behavior_pattern == 'unpredictable':
            self.unpredictable_behavior(delta_time)
            
        # Change pattern occasionally
        if self.pattern_timer > self.pattern_duration:
            self.change_behavior_pattern()
            
        # Basic movement
        self.rect.x += self.direction * self.speed * delta_time
        self.rect.y += self.vertical_speed * delta_time
        
        # Bounce off screen edges with AI consideration
        self.handle_screen_bounds()
        
    def aggressive_behavior(self, player_pos: tuple, delta_time: float):
        """Aggressive behavior - moves towards player"""
        if player_pos and self.ai_level > 2:
            # Calculate direction to player
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            
            # Move towards player
            if abs(dx) > 10:
                self.direction = 1 if dx > 0 else -1
            if abs(dy) > 10:
                self.vertical_speed = 50 if dy > 0 else -50
                
    def evasive_behavior(self, player_pos: tuple, delta_time: float):
        """Evasive behavior - avoids player"""
        if player_pos and self.evasion_cooldown <= 0:
            # Calculate distance to player
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.evasion_range:
                # Move away from player
                if abs(dx) > 10:
                    self.direction = -1 if dx > 0 else 1
                if abs(dy) > 10:
                    self.vertical_speed = -50 if dy > 0 else 50
                self.evasion_cooldown = 1000
                
    def predictable_behavior(self, delta_time: float):
        """Predictable behavior - regular patterns"""
        if self.change_direction_timer > 3000:
            self.change_direction()
            self.change_direction_timer = 0
            
    def unpredictable_behavior(self, delta_time: float):
        """Unpredictable behavior - random changes"""
        if random.random() < 0.01:  # 1% chance per frame
            self.change_direction()
            self.vertical_speed = random.uniform(-80, 80)
            
    def change_behavior_pattern(self):
        """Change to a new behavior pattern"""
        patterns = ['aggressive', 'evasive', 'predictable', 'unpredictable']
        self.behavior_pattern = random.choice(patterns)
        self.pattern_timer = 0
        self.pattern_duration = random.randint(2000, 5000)
        
    def handle_screen_bounds(self):
        """Handle screen boundary collisions with AI consideration"""
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
            self.game.asset_manager.beep_sound.play()
            
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

class AIGameEngine:
    """AI-enhanced game engine"""
    
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
        
        # AI system
        self.ai_level = 1
        self.games_played = 0
        self.performance_history = []
        self.learning_rate = 0.1
        
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
        
        # Player tracking
        self.player_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player_accuracy = 0.0
        
        # Initialize game objects
        self._init_game_objects()
        
        # Load AI data
        self.load_ai_data()
        
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
        
    def load_ai_data(self):
        """Load AI learning data from file"""
        try:
            with open('ai_data.json', 'r') as f:
                data = json.load(f)
                self.ai_level = data.get('ai_level', 1)
                self.games_played = data.get('games_played', 0)
                self.performance_history = data.get('performance_history', [])
        except FileNotFoundError:
            # Create new AI data file
            self.save_ai_data()
            
    def save_ai_data(self):
        """Save AI learning data to file"""
        data = {
            'ai_level': self.ai_level,
            'games_played': self.games_played,
            'performance_history': self.performance_history
        }
        with open('ai_data.json', 'w') as f:
            json.dump(data, f, indent=2)
            
    def calculate_performance_score(self) -> float:
        """Calculate current performance score"""
        if self.total_shots == 0:
            return 0.0
            
        accuracy = self.ducks_shot / self.total_shots
        speed_bonus = min(1.0, self.ducks_shot / 10.0)  # Bonus for shooting many ducks
        time_bonus = max(0.0, (self.game_time - self.get_time_remaining()) / self.game_time)
        
        return (accuracy * 0.5) + (speed_bonus * 0.3) + (time_bonus * 0.2)
        
    def update_ai_level(self):
        """Update AI level based on player performance"""
        performance = self.calculate_performance_score()
        self.performance_history.append(performance)
        
        # Keep only last 10 games
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
            
        # Calculate average performance
        avg_performance = sum(self.performance_history) / len(self.performance_history)
        
        # Update AI level based on performance
        if avg_performance > 0.7:  # High performance
            self.ai_level = min(10, self.ai_level + 1)
        elif avg_performance < 0.3:  # Low performance
            self.ai_level = max(1, self.ai_level - 1)
            
        # Save updated data
        self.save_ai_data()
        
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
        # Update AI before resetting
        if self.state == GAME_OVER:
            self.update_ai_level()
            
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
        """Spawn a new AI-enhanced duck"""
        colors = list(self.asset_manager.duck_sprites.keys())
        weights = [0.5, 0.3, 0.2]  # Probability weights
        color = random.choices(colors, weights=weights)[0]
        
        duck = AIDuck(self, color, self.ai_level)
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
            
        # Check game time
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.game_time:
            self.state = GAME_OVER
            self.games_played += 1
            
    def update_cursor(self, position: tuple):
        """Update cursor position"""
        if self.cursor and position and len(position) == 2:
            self.cursor.update(position)
            self.player_position = position
            
    def get_player_position(self) -> tuple:
        """Get current player position"""
        return self.player_position
        
    def get_time_remaining(self) -> int:
        """Get time remaining in milliseconds"""
        current_time = pygame.time.get_ticks()
        return max(0, self.game_time - (current_time - self.start_time))
        
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information"""
        time_remaining = self.get_time_remaining()
        
        return {
            "state": self.state,
            "score": self.score,
            "ducks_shot": self.ducks_shot,
            "total_shots": self.total_shots,
            "accuracy": (self.ducks_shot / max(1, self.total_shots)) * 100,
            "time_remaining": time_remaining,
            "total_ducks": self.total_ducks,
            "ai_level": self.ai_level,
            "games_played": self.games_played
        }
        
    def get_sprites(self) -> pygame.sprite.LayeredUpdates:
        """Get sprite group for rendering"""
        return self.all_sprites

class AIUIManager:
    """UI manager for AI-enhanced game"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        
        # Initialize fonts
        self.font = pygame.font.SysFont('Arial', 20)
        self.big_font = pygame.font.SysFont('Arial', 48)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
    def draw_menu(self, game_info: Dict[str, Any] = None):
        """Draw main menu"""
        # Clear screen
        self.screen.fill((135, 206, 250))  # Light blue background
        
        # Title
        title = self.big_font.render("DUCK HUNT AI", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Los patos aprenden de ti", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 130))
        self.screen.blit(subtitle, subtitle_rect)
        
        # AI Level indicator
        ai_level = game_info.get('ai_level', 1) if game_info else 1
        ai_text = self.font.render(f"Nivel de IA: {ai_level}", True, ORANGE)
        ai_rect = ai_text.get_rect(center=(self.screen_width // 2, 170))
        self.screen.blit(ai_text, ai_rect)
        
        # Games played
        games_played = game_info.get('games_played', 0) if game_info else 0
        games_text = self.font.render(f"Partidas jugadas: {games_played}", True, BLACK)
        games_rect = games_text.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(games_text, games_rect)
        
        # Instructions
        instructions = [
            "Controles:",
            "• Mouse: Mover cursor y disparar",
            "• P: Pausar",
            "• ESC: Salir",
            "",
            "Los patos se vuelven más inteligentes",
            "y rápidos con cada partida."
        ]
        
        y_offset = 250
        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
            
        # Start instruction
        start_text = self.font.render("Presiona ENTER para comenzar", True, RED)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, 420))
        self.screen.blit(start_text, start_rect)
        
    def draw_hud(self, game_info: Dict[str, Any]):
        """Draw heads-up display during gameplay"""
        # Score
        score_text = self.font.render(f"Puntos: {game_info['score']}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Ducks shot
        ducks_text = self.font.render(f"Patos: {game_info['ducks_shot']}", True, WHITE)
        self.screen.blit(ducks_text, (10, 35))
        
        # Accuracy
        accuracy = game_info['accuracy']
        accuracy_text = self.font.render(f"Precisión: {accuracy:.1f}%", True, WHITE)
        self.screen.blit(accuracy_text, (10, 60))
        
        # AI Level
        ai_text = self.font.render(f"IA Nivel: {game_info['ai_level']}", True, ORANGE)
        self.screen.blit(ai_text, (10, 85))
        
        # Time remaining
        time_remaining = game_info['time_remaining'] // 1000
        time_text = self.font.render(f"Tiempo: {time_remaining}s", True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (self.screen_width - 10, 10)
        self.screen.blit(time_text, time_rect)
        
        # Shots
        shots_text = self.font.render(f"Disparos: {game_info['total_shots']}", True, WHITE)
        shots_rect = shots_text.get_rect()
        shots_rect.topright = (self.screen_width - 10, 35)
        self.screen.blit(shots_text, shots_rect)
        
    def draw_paused(self):
        """Draw pause screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.big_font.render("PAUSA", True, WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        instruction_text = self.font.render("Presiona P para continuar", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(instruction_text, instruction_rect)
        
    def draw_game_over(self, game_info: Dict[str, Any]):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.big_font.render("¡FIN DEL JUEGO!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Puntuación Final: {game_info['score']}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 140))
        self.screen.blit(score_text, score_rect)
        
        # Ducks shot
        ducks_text = self.font.render(f"Patos Abatidos: {game_info['ducks_shot']}", True, WHITE)
        ducks_rect = ducks_text.get_rect(center=(self.screen_width // 2, 165))
        self.screen.blit(ducks_text, ducks_rect)
        
        # Accuracy
        accuracy = game_info['accuracy']
        accuracy_text = self.font.render(f"Precisión: {accuracy:.1f}%", True, WHITE)
        accuracy_rect = accuracy_text.get_rect(center=(self.screen_width // 2, 190))
        self.screen.blit(accuracy_text, accuracy_rect)
        
        # AI Level
        ai_text = self.font.render(f"Nivel de IA: {game_info['ai_level']}", True, ORANGE)
        ai_rect = ai_text.get_rect(center=(self.screen_width // 2, 215))
        self.screen.blit(ai_text, ai_rect)
        
        # Performance rating
        rating = self._get_performance_rating(accuracy, game_info['ducks_shot'])
        rating_text = self.font.render(f"Calificación: {rating}", True, YELLOW)
        rating_rect = rating_text.get_rect(center=(self.screen_width // 2, 250))
        self.screen.blit(rating_text, rating_rect)
        
        # AI learning message
        if game_info['ai_level'] > 1:
            learning_text = self.font.render("¡Los patos están aprendiendo!", True, GREEN)
            learning_rect = learning_text.get_rect(center=(self.screen_width // 2, 280))
            self.screen.blit(learning_text, learning_rect)
        
        # Restart instruction
        restart_text = self.font.render("Presiona R para jugar de nuevo", True, GREEN)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, 320))
        self.screen.blit(restart_text, restart_rect)
        
        # Exit instruction
        exit_text = self.font.render("Presiona ESC para salir", True, WHITE)
        exit_rect = exit_text.get_rect(center=(self.screen_width // 2, 350))
        self.screen.blit(exit_text, exit_rect)
        
    def _get_performance_rating(self, accuracy: float, ducks_shot: int) -> str:
        """Get performance rating based on accuracy and ducks shot"""
        if accuracy >= 80 and ducks_shot >= 10:
            return "¡EXCELENTE! 🏆"
        elif accuracy >= 60 and ducks_shot >= 7:
            return "¡MUY BUENO! 🎯"
        elif accuracy >= 40 and ducks_shot >= 5:
            return "BUENO 👍"
        elif accuracy >= 20 and ducks_shot >= 3:
            return "REGULAR 😊"
        else:
            return "PRACTICA MÁS 💪"
            
    def draw_all(self, game_state: int, game_info: Dict[str, Any], sprites: pygame.sprite.LayeredUpdates):
        """Draw everything based on game state"""
        # Clear screen
        self.screen.fill((135, 206, 250))
        
        # Draw sprites
        sprites.draw(self.screen)
        
        # Draw UI based on state
        if game_state == MENU:
            self.draw_menu(game_info)
        elif game_state == PLAYING:
            self.draw_hud(game_info)
        elif game_state == PAUSED:
            self.draw_hud(game_info)
            self.draw_paused()
        elif game_state == GAME_OVER:
            self.draw_game_over(game_info)

class AIDuckHuntGame:
    """Main AI-enhanced Duck Hunt game"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                             pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Duck Hunt AI - Los patos aprenden de ti")
        
        # Hide system cursor
        pygame.mouse.set_visible(False)
        
        # Initialize modules
        self.asset_manager = AssetManager()
        self.game_engine = AIGameEngine(self.asset_manager)
        self.ui_manager = AIUIManager(self.screen, self.asset_manager)
        
        # Game loop variables
        self.clock = pygame.time.Clock()
        self.running = True
        
    def handle_input(self):
        """Handle all input events"""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_RETURN and self.game_engine.state == MENU:
                    self.game_engine.start_game()
                elif event.key == pygame.K_p and self.game_engine.state in [PLAYING, PAUSED]:
                    self.game_engine.toggle_pause()
                elif event.key == pygame.K_r and self.game_engine.state == GAME_OVER:
                    self.game_engine.reset_game()
                    
            elif event.type == pygame.MOUSEMOTION:
                self.game_engine.update_cursor(event.pos)
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_engine.state == PLAYING:
                    self.game_engine.shoot(event.pos)
                elif self.game_engine.state == GAME_OVER:
                    self.game_engine.reset_game()
                    
    def update(self, delta_time: float):
        """Update game state"""
        self.game_engine.update(delta_time)
        
    def draw(self):
        """Draw everything"""
        # Get current game state
        game_state = self.game_engine.state
        game_info = self.game_engine.get_game_info()
        sprites = self.game_engine.get_sprites()
        
        # Draw everything
        self.ui_manager.draw_all(game_state, game_info, sprites)
        
        # Dibuja la mira/cursor por encima de todo
        if self.game_engine.cursor:
            self.screen.blit(self.game_engine.cursor.image, self.game_engine.cursor.rect)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        print("🎮 Iniciando Duck Hunt AI...")
        print("🤖 Los patos aprenden de tu rendimiento")
        print("📋 Controles:")
        print("   • Mouse: Mover cursor y disparar")
        print("   • P: Pausar")
        print("   • ESC: Salir")
        print("   • ENTER: Iniciar juego")
        print("   • R: Reiniciar (en fin de juego)")
        
        # Main game loop
        while self.running:
            # Cap frame rate and get delta time
            delta_time = self.clock.tick(FPS) / 1000.0
            
            # Handle input
            self.handle_input()
            
            # Update game
            self.update(delta_time)
            
            # Draw everything
            self.draw()
            
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Limpiando recursos...")
        pygame.quit()

def main():
    """Main entry point"""
    print("🦆 Duck Hunt AI")
    print("=" * 50)
    print("Los patos se vuelven más inteligentes con cada partida!")
    
    try:
        # Create and run game
        game = AIDuckHuntGame()
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Juego interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 