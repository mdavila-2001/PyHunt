"""
Enhanced Duck Hunt - PyHunt Ultimate
Integrates all advanced features: AI, achievements, power-ups, game modes, statistics, and gestures
"""
import pygame
import os
import random
import math
import json
from typing import Dict, List, Any, Optional
from pygame import mixer

# Import all our enhanced systems
from simple_asset_manager import AssetManager
from achievement_system import AchievementSystem
from powerup_system import PowerUpSystem, PowerUpType
from game_modes import GameModeManager, GameMode
from statistics_system import StatisticsSystem
from enhanced_ai_ducks import EnhancedAIDuck
from gesture_controller import GestureController
from input_manager import InputManager

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
PURPLE = (128, 0, 128)

# Game states
MENU = 0
MODE_SELECTION = 1
PLAYING = 2
PAUSED = 3
GAME_OVER = 4
STATISTICS = 5
ACHIEVEMENTS = 6

class EnhancedCursor(pygame.sprite.Sprite):
    """Enhanced cursor with visual effects"""
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.asset_manager.cursor_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Visual effects
        self.rotation = 0
        self.scale = 1.0
        self.original_image = self.image
        
    def update(self, position: tuple):
        """Update cursor position and effects"""
        if position and len(position) == 2:
            self.rect.center = position
            
        # Apply power-up effects
        if self.game.powerup_system.has_effect(PowerUpType.RAPID_FIRE):
            self.scale = 1.2
        else:
            self.scale = 1.0
            
        # Rotate cursor slightly
        self.rotation += 2
        if self.rotation >= 360:
            self.rotation = 0
            
        # Apply transformations
        rotated = pygame.transform.rotate(self.original_image, self.rotation)
        scaled = pygame.transform.scale(rotated, 
                                      (int(rotated.get_width() * self.scale),
                                       int(rotated.get_height() * self.scale)))
        self.image = scaled
        self.rect = self.image.get_rect(center=self.rect.center)

class EnhancedGameEngine:
    """Enhanced game engine with all systems integrated"""
    
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
        # Game state
        self.state = MENU
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        self.game_time = 60000
        self.start_time = 0
        
        # AI system
        self.ai_level = 1
        self.games_played = 0
        self.performance_history = []
        
        # Enhanced systems
        self.achievement_system = AchievementSystem()
        self.powerup_system = PowerUpSystem(self)
        self.game_mode_manager = GameModeManager()
        self.statistics_system = StatisticsSystem()
        
        # Sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ducks = pygame.sprite.Group()
        
        # Game objects
        self.cursor = None
        self.background = None
        self.foreground = None
        
        # Game variables
        self.spawn_timer = 0
        self.spawn_delay = 2000
        
        # Player tracking
        self.player_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.player_accuracy = 0.0
        
        # Mode-specific variables
        self.current_mode_rules = {}
        self.shots_remaining = None
        self.survival_timer = 0
        self.survival_level = 1
        
        # Initialize game objects
        self._init_game_objects()
        
        # Load AI data
        self.load_ai_data()
        
    def _init_game_objects(self):
        """Initialize game objects"""
        # Create enhanced cursor
        self.cursor = EnhancedCursor(self)
        self.all_sprites.add(self.cursor)
        
        # Create background and foreground
        self.background = pygame.sprite.Sprite()
        self.background.image = self.asset_manager.background_img
        self.background.rect = self.background.image.get_rect()
        self.background.rect.topleft = (0, 0)
        
        self.foreground = pygame.sprite.Sprite()
        self.foreground.image = self.asset_manager.foreground_img
        self.foreground.rect = self.foreground.image.get_rect()
        self.foreground.rect.bottomleft = (0, SCREEN_HEIGHT)
        
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
            
    def start_game(self, mode: GameMode = GameMode.CLASSIC):
        """Start a new game with specified mode"""
        self.game_mode_manager.set_current_mode(mode)
        self.current_mode_rules = self.game_mode_manager.apply_mode_rules(self)
        
        self.state = PLAYING
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        self.start_time = pygame.time.get_ticks()
        self.spawn_timer = 0
        
        # Reset systems
        self.powerup_system.reset()
        
        # Clear existing ducks
        for duck in self.ducks:
            duck.kill()
            
        # Initialize mode-specific variables
        if 'precision_mode' in self.current_mode_rules:
            self.shots_remaining = self.current_mode_rules.get('max_shots', 10)
        if 'survival_mode' in self.current_mode_rules:
            self.survival_timer = 0
            self.survival_level = 1
            
    def reset_game(self):
        """Reset game to menu"""
        # Update AI and statistics before resetting
        if self.state == GAME_OVER:
            self.update_ai_level()
            self._record_game_session()
            
        self.state = MENU
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        
        # Clear ducks
        for duck in self.ducks:
            duck.kill()
            
        # Reset systems
        self.powerup_system.reset()
        
    def _record_game_session(self):
        """Record game session for statistics"""
        game_info = self.get_game_info()
        mode_name = self.game_mode_manager.get_current_mode().name
        self.statistics_system.record_game_session(game_info, mode_name)
        
        # Check achievements
        newly_unlocked = self.achievement_system.check_achievements(game_info)
        if newly_unlocked:
            print(f"🎉 ¡Logros desbloqueados: {len(newly_unlocked)}!")
            for achievement in newly_unlocked:
                print(f"  {achievement.icon} {achievement.name}: {achievement.description}")
                
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING
            
    def spawn_duck(self):
        """Spawn a new enhanced AI duck"""
        colors = list(self.asset_manager.duck_sprites.keys())
        weights = [0.5, 0.3, 0.2]
        color = random.choices(colors, weights=weights)[0]
        
        # Use enhanced AI duck
        duck = EnhancedAIDuck(self, color, self.ai_level)
        self.ducks.add(duck)
        self.all_sprites.add(duck)
        self.total_ducks += 1
        
    def shoot(self, position: tuple):
        """Handle shooting at position"""
        # Check if shooting is allowed
        if self.shots_remaining is not None and self.shots_remaining <= 0:
            return
            
        self.total_shots += 1
        if self.shots_remaining is not None:
            self.shots_remaining -= 1
            
        self.asset_manager.shot_sound.play()
        
        # Check for power-up collection
        for powerup in self.powerup_system.get_sprites():
            if powerup.rect.collidepoint(position):
                self.powerup_system.collect_powerup(powerup)
                return
                
        # Check for duck hits
        for duck in self.ducks:
            if duck.alive and duck.rect.collidepoint(position):
                duck.hit()
                
                # Apply power-up effects
                points = duck.points
                if self.powerup_system.has_effect(PowerUpType.DOUBLE_POINTS):
                    points *= 2
                    
                self.score += points
                self.ducks_shot += 1
                break
                
    def update(self, delta_time: float):
        """Update game state"""
        if self.state != PLAYING:
            return
            
        # Apply time scale from power-ups
        if self.powerup_system.has_effect(PowerUpType.SLOW_MOTION):
            delta_time *= 0.5
            
        # Update mode-specific logic
        self.game_mode_manager.update_mode_specific_logic(self, delta_time)
        
        # Update spawn timer
        self.spawn_timer += delta_time * 1000
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_duck()
            self.spawn_timer = 0
            
        # Update power-up system
        self.powerup_system.update(delta_time)
        
        # Update all sprites except cursor
        for sprite in self.all_sprites:
            if isinstance(sprite, EnhancedCursor):
                continue
            sprite.update(delta_time)
            
        # Update cursor
        if self.cursor:
            self.cursor.update(self.player_position)
            
        # Check game time
        current_time = pygame.time.get_ticks()
        if self.game_time > 0 and current_time - self.start_time >= self.game_time:
            self.state = GAME_OVER
            self.games_played += 1
            
        # Check precision mode end condition
        if self.shots_remaining is not None and self.shots_remaining <= 0:
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
        if self.game_time <= 0:
            return 0
        current_time = pygame.time.get_ticks()
        return max(0, self.game_time - (current_time - self.start_time))
        
    def get_game_info(self) -> Dict[str, Any]:
        """Get current game information"""
        time_remaining = self.get_time_remaining()
        accuracy = (self.ducks_shot / max(1, self.total_shots)) * 100
        
        return {
            "state": self.state,
            "score": self.score,
            "ducks_shot": self.ducks_shot,
            "total_shots": self.total_shots,
            "accuracy": accuracy,
            "time_remaining": time_remaining,
            "total_ducks": self.total_ducks,
            "ai_level": self.ai_level,
            "games_played": self.games_played,
            "shots_remaining": self.shots_remaining,
            "survival_level": getattr(self, 'survival_level', 1)
        }
        
    def get_sprites(self) -> pygame.sprite.LayeredUpdates:
        """Get sprite group for rendering"""
        return self.all_sprites
        
    def update_ai_level(self):
        """Update AI level based on player performance"""
        performance = self.calculate_performance_score()
        self.performance_history.append(performance)
        
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
            
        avg_performance = sum(self.performance_history) / len(self.performance_history)
        
        if avg_performance > 0.7:
            self.ai_level = min(10, self.ai_level + 1)
        elif avg_performance < 0.3:
            self.ai_level = max(1, self.ai_level - 1)
            
        self.save_ai_data()
        
    def calculate_performance_score(self) -> float:
        """Calculate current performance score"""
        if self.total_shots == 0:
            return 0.0
            
        accuracy = self.ducks_shot / self.total_shots
        speed_bonus = min(1.0, self.ducks_shot / 10.0)
        time_bonus = max(0.0, (self.game_time - self.get_time_remaining()) / self.game_time)
        
        return (accuracy * 0.5) + (speed_bonus * 0.3) + (time_bonus * 0.2)

class EnhancedUIManager:
    """Enhanced UI manager with all new features"""
    
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
        """Draw enhanced main menu"""
        # Clear screen
        self.screen.fill((135, 206, 250))
        
        # Title
        title = self.big_font.render("PYHUNT ULTIMATE", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Duck Hunt con IA Avanzada", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Stats summary
        if game_info:
            stats_text = [
                f"IA Nivel: {game_info.get('ai_level', 1)}",
                f"Partidas: {game_info.get('games_played', 0)}",
                f"Mejor Puntuación: {game_info.get('best_score', 0)}"
            ]
            
            y_offset = 140
            for stat in stats_text:
                text = self.font.render(stat, True, BLACK)
                text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 25
                
        # Menu options
        options = [
            "1. Jugar (Modo Clásico)",
            "2. Seleccionar Modo",
            "3. Estadísticas",
            "4. Logros",
            "5. Salir"
        ]
        
        y_offset = 220
        for option in options:
            text = self.font.render(option, True, BLACK)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
    def draw_mode_selection(self, mode_manager: GameModeManager):
        """Draw game mode selection screen"""
        self.screen.fill((135, 206, 250))
        
        # Title
        title = self.big_font.render("SELECCIONAR MODO", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Mode list
        modes = mode_manager.get_mode_list()
        y_offset = 100
        
        for i, (mode, name, description) in enumerate(modes):
            # Mode name
            mode_text = self.font.render(f"{i+1}. {name}", True, BLACK)
            self.screen.blit(mode_text, (50, y_offset))
            
            # Mode description (truncated)
            desc_text = self.small_font.render(description[:60] + "...", True, BLACK)
            self.screen.blit(desc_text, (50, y_offset + 25))
            
            y_offset += 60
            
        # Instructions
        instruction = self.font.render("Presiona el número del modo o ESC para volver", True, RED)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, 420))
        self.screen.blit(instruction, instruction_rect)
        
    def draw_hud(self, game_info: Dict[str, Any], powerup_system: PowerUpSystem):
        """Draw enhanced heads-up display"""
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
        
        # Shots remaining (for precision mode)
        if game_info.get('shots_remaining') is not None:
            shots_remaining = game_info['shots_remaining']
            shots_remaining_text = self.font.render(f"Disparos Restantes: {shots_remaining}", True, YELLOW)
            shots_remaining_rect = shots_remaining_text.get_rect()
            shots_remaining_rect.topright = (self.screen_width - 10, 60)
            self.screen.blit(shots_remaining_text, shots_remaining_rect)
            
        # Survival level
        if game_info.get('survival_level'):
            survival_text = self.font.render(f"Nivel: {game_info['survival_level']}", True, PURPLE)
            survival_rect = survival_text.get_rect()
            survival_rect.topright = (self.screen_width - 10, 85)
            self.screen.blit(survival_text, survival_rect)
            
        # Active power-ups
        self._draw_powerup_indicators(powerup_system)
        
    def _draw_powerup_indicators(self, powerup_system: PowerUpSystem):
        """Draw active power-up indicators"""
        active_effects = powerup_system.get_active_effects()
        if not active_effects:
            return
            
        # Background for power-up indicators
        bg_width = 200
        bg_height = len(active_effects) * 25 + 10
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.set_alpha(180)
        bg_surface.fill(BLACK)
        self.screen.blit(bg_surface, (10, self.screen_height - bg_height - 10))
        
        y_offset = self.screen_height - bg_height
        for effect in active_effects:
            # Power-up icon and name
            icon_text = self.small_font.render(f"{effect.powerup_type.value}", True, WHITE)
            self.screen.blit(icon_text, (15, y_offset + 5))
            
            # Progress bar
            progress = effect.get_remaining_percentage()
            bar_width = 150
            bar_height = 8
            bar_x = 15
            bar_y = y_offset + 20
            
            # Background bar
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, GREEN, 
                           (bar_x, bar_y, progress_width, bar_height))
            
            y_offset += 30
            
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
        
    def draw_game_over(self, game_info: Dict[str, Any], achievement_system: AchievementSystem):
        """Draw enhanced game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.big_font.render("¡FIN DEL JUEGO!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Puntuación Final: {game_info['score']}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(score_text, score_rect)
        
        # Ducks shot
        ducks_text = self.font.render(f"Patos Abatidos: {game_info['ducks_shot']}", True, WHITE)
        ducks_rect = ducks_text.get_rect(center=(self.screen_width // 2, 145))
        self.screen.blit(ducks_text, ducks_rect)
        
        # Accuracy
        accuracy = game_info['accuracy']
        accuracy_text = self.font.render(f"Precisión: {accuracy:.1f}%", True, WHITE)
        accuracy_rect = accuracy_text.get_rect(center=(self.screen_width // 2, 170))
        self.screen.blit(accuracy_text, accuracy_rect)
        
        # AI Level
        ai_text = self.font.render(f"Nivel de IA: {game_info['ai_level']}", True, ORANGE)
        ai_rect = ai_text.get_rect(center=(self.screen_width // 2, 195))
        self.screen.blit(ai_text, ai_rect)
        
        # Performance rating
        rating = self._get_performance_rating(accuracy, game_info['ducks_shot'])
        rating_text = self.font.render(f"Calificación: {rating}", True, YELLOW)
        rating_rect = rating_text.get_rect(center=(self.screen_width // 2, 230))
        self.screen.blit(rating_text, rating_rect)
        
        # Achievement progress
        achievement_progress = achievement_system.get_achievement_progress()
        achievement_text = self.font.render(
            f"Logros: {achievement_progress['unlocked_count']}/{achievement_progress['total_achievements']}", 
            True, GREEN)
        achievement_rect = achievement_text.get_rect(center=(self.screen_width // 2, 260))
        self.screen.blit(achievement_text, achievement_rect)
        
        # Instructions
        restart_text = self.font.render("Presiona R para jugar de nuevo", True, GREEN)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, 300))
        self.screen.blit(restart_text, restart_rect)
        
        exit_text = self.font.render("Presiona ESC para salir", True, WHITE)
        exit_rect = exit_text.get_rect(center=(self.screen_width // 2, 330))
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
        
    def draw_statistics(self, statistics_system: StatisticsSystem):
        """Draw statistics screen"""
        if not statistics_system:
            return
            
        # Title
        title = self.big_font.render("ESTADÍSTICAS", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 40))
        self.screen.blit(title, title_rect)
        
        # Get player stats
        player_stats = statistics_system.get_player_stats()
        
        # Stats display
        stats_data = [
            f"Partidas Totales: {player_stats.total_games}",
            f"Puntuación Total: {player_stats.total_score}",
            f"Mejor Puntuación: {player_stats.best_score}",
            f"Precisión Promedio: {player_stats.average_accuracy:.1f}%",
            f"Mejor Precisión: {player_stats.best_accuracy:.1f}%",
            f"Patos Abatidos: {player_stats.total_ducks_shot}",
            f"Mejor Racha: {player_stats.longest_streak}",
            f"Tiempo Jugado: {player_stats.total_play_time // 60} min",
            f"Modo Favorito: {player_stats.favorite_mode}",
            f"Logros Desbloqueados: {player_stats.achievements_unlocked}"
        ]
        
        y_offset = 80
        for stat in stats_data:
            text = self.font.render(stat, True, BLACK)
            self.screen.blit(text, (50, y_offset))
            y_offset += 30
            
        # Instructions
        instruction = self.font.render("Presiona ESC para volver al menú", True, RED)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, 420))
        self.screen.blit(instruction, instruction_rect)
        
    def draw_achievements(self, achievement_system: AchievementSystem):
        """Draw achievements screen"""
        if not achievement_system:
            return
            
        # Title
        title = self.big_font.render("LOGROS", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Progress summary
        progress = achievement_system.get_achievement_progress()
        progress_text = self.font.render(
            f"Progreso: {progress['unlocked_count']}/{progress['total_achievements']} "
            f"({progress['completion_percentage']:.1f}%)", True, BLACK)
        progress_rect = progress_text.get_rect(center=(self.screen_width // 2, 70))
        self.screen.blit(progress_text, progress_rect)
        
        # Points
        points_text = self.font.render(f"Puntos de Logros: {progress['total_points']}", True, ORANGE)
        points_rect = points_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(points_text, points_rect)
        
        # Show unlocked achievements
        unlocked = achievement_system.get_unlocked_achievements()
        y_offset = 130
        
        if unlocked:
            title_text = self.small_font.render("LOGROS DESBLOQUEADOS:", True, GREEN)
            self.screen.blit(title_text, (20, y_offset))
            y_offset += 25
            
            for achievement in unlocked[:8]:  # Show first 8
                achievement_text = self.small_font.render(
                    f"{achievement.icon} {achievement.name} (+{achievement.points} pts)", 
                    True, GREEN)
                self.screen.blit(achievement_text, (30, y_offset))
                y_offset += 20
        else:
            no_achievements = self.font.render("¡Aún no has desbloqueado logros!", True, BLACK)
            no_achievements_rect = no_achievements.get_rect(center=(self.screen_width // 2, 200))
            self.screen.blit(no_achievements, no_achievements_rect)
            
        # Instructions
        instruction = self.font.render("Presiona ESC para volver al menú", True, RED)
        instruction_rect = instruction.get_rect(center=(self.screen_width // 2, 420))
        self.screen.blit(instruction, instruction_rect)
            
    def draw_all(self, game_state: int, game_info: Dict[str, Any], 
                 sprites: pygame.sprite.LayeredUpdates, 
                 powerup_system: PowerUpSystem = None,
                 achievement_system: AchievementSystem = None,
                 mode_manager: GameModeManager = None,
                 statistics_system: StatisticsSystem = None):
        """Draw everything based on game state"""
        # Clear screen
        self.screen.fill((135, 206, 250))
        
        # Draw sprites
        sprites.draw(self.screen)
        
        # Draw UI based on state
        if game_state == MENU:
            self.draw_menu(game_info)
        elif game_state == MODE_SELECTION:
            self.draw_mode_selection(mode_manager)
        elif game_state == PLAYING:
            self.draw_hud(game_info, powerup_system)
        elif game_state == PAUSED:
            self.draw_hud(game_info, powerup_system)
            self.draw_paused()
        elif game_state == GAME_OVER:
            self.draw_game_over(game_info, achievement_system)
        elif game_state == STATISTICS:
            self.draw_statistics(statistics_system)
        elif game_state == ACHIEVEMENTS:
            self.draw_achievements(achievement_system)

class EnhancedDuckHuntGame:
    """Main enhanced Duck Hunt game"""
    
    def __init__(self, use_gestures: bool = False):
        # Initialize pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                             pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("PyHunt Ultimate - Duck Hunt con IA Avanzada")
        
        # Hide system cursor
        pygame.mouse.set_visible(False)
        
        # Initialize modules
        self.asset_manager = AssetManager()
        self.game_engine = EnhancedGameEngine(self.asset_manager)
        self.ui_manager = EnhancedUIManager(self.screen, self.asset_manager)
        
        # Initialize gesture controller if requested
        self.gesture_controller = None
        self.input_manager = InputManager()
        
        if use_gestures:
            try:
                self.gesture_controller = GestureController()
                self.gesture_controller.set_screen_dimensions(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.gesture_controller.start()
                self.input_manager.enable_gestures(self.gesture_controller)
                print("✅ Reconocimiento de gestos habilitado")
            except Exception as e:
                print(f"⚠️ No se pudo inicializar el reconocimiento de gestos: {e}")
                print("El juego funcionará solo con mouse/touchpad")
        
        # Game loop variables
        self.clock = pygame.time.Clock()
        self.running = True
        
    def handle_input(self):
        """Handle all input events"""
        events = pygame.event.get()
        actions = self.input_manager.handle_events(events)

        # --- Keep original event handling for everything except shooting/reset ---
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == pygame.MOUSEMOTION:
                self.game_engine.update_cursor(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_engine.state == PLAYING:
                    self.game_engine.shoot(event.pos)
                elif self.game_engine.state == GAME_OVER:
                    self.game_engine.reset_game()

        # --- Use InputManager for gesture/mouse shooting/reset only ---
        if actions['shoot'] and self.game_engine.state == PLAYING:
            self.game_engine.shoot(actions['cursor_position'])
        elif actions['shoot'] and self.game_engine.state == GAME_OVER:
            self.game_engine.reset_game()

        # Always update cursor position (prefer gesture if available)
        self.game_engine.update_cursor(actions['cursor_position'])
            
    def _handle_keydown(self, key):
        """Handle key press events"""
        if self.game_engine.state == MENU:
            self._handle_menu_key(key)
        elif self.game_engine.state == MODE_SELECTION:
            self._handle_mode_selection_key(key)
        elif self.game_engine.state == PLAYING:
            self._handle_playing_key(key)
        elif self.game_engine.state == PAUSED:
            self._handle_paused_key(key)
        elif self.game_engine.state == GAME_OVER:
            self._handle_game_over_key(key)
        elif self.game_engine.state == STATISTICS:
            self._handle_statistics_key(key)
        elif self.game_engine.state == ACHIEVEMENTS:
            self._handle_achievements_key(key)
            
    def _handle_menu_key(self, key):
        """Handle key press in menu state"""
        if key == pygame.K_1:
            print("🎮 Iniciando modo Clásico...")
            self.game_engine.start_game(GameMode.CLASSIC)
        elif key == pygame.K_2:
            print("📋 Abriendo selección de modos...")
            self.game_engine.state = MODE_SELECTION
        elif key == pygame.K_3:
            print("📊 Abriendo estadísticas...")
            self.game_engine.state = STATISTICS
        elif key == pygame.K_4:
            print("🏆 Abriendo logros...")
            self.game_engine.state = ACHIEVEMENTS
        elif key == pygame.K_5:
            print("👋 Saliendo del juego...")
            self.running = False
        elif key == pygame.K_ESCAPE:
            print("👋 Saliendo del juego...")
            self.running = False
            
    def _handle_mode_selection_key(self, key):
        """Handle key press in mode selection state"""
        if pygame.K_1 <= key <= pygame.K_7:
            mode_index = key - pygame.K_1
            modes = list(self.game_engine.game_mode_manager.modes.keys())
            if mode_index < len(modes):
                selected_mode = modes[mode_index]
                mode_name = self.game_engine.game_mode_manager.get_mode(selected_mode).name
                print(f"🎮 Iniciando modo {mode_name}...")
                self.game_engine.start_game(selected_mode)
        elif key == pygame.K_ESCAPE:
            print("🔙 Volviendo al menú principal...")
            self.game_engine.state = MENU
            
    def _handle_playing_key(self, key):
        """Handle key press in playing state"""
        if key == pygame.K_p:
            self.game_engine.toggle_pause()
        elif key == pygame.K_ESCAPE:
            self.game_engine.reset_game()
            
    def _handle_paused_key(self, key):
        """Handle key press in paused state"""
        if key == pygame.K_p:
            self.game_engine.toggle_pause()
        elif key == pygame.K_ESCAPE:
            self.game_engine.reset_game()
            
    def _handle_game_over_key(self, key):
        """Handle key press in game over state"""
        if key == pygame.K_r:
            print("🔄 Reiniciando juego...")
            self.game_engine.reset_game()
        elif key == pygame.K_ESCAPE:
            print("🔙 Volviendo al menú principal...")
            self.game_engine.reset_game()
            
    def _handle_statistics_key(self, key):
        """Handle key press in statistics state"""
        if key == pygame.K_ESCAPE:
            print("🔙 Volviendo al menú principal...")
            self.game_engine.state = MENU
            
    def _handle_achievements_key(self, key):
        """Handle key press in achievements state"""
        if key == pygame.K_ESCAPE:
            print("🔙 Volviendo al menú principal...")
            self.game_engine.state = MENU
        

            
    def update(self, delta_time: float):
        """Update game state"""
        # Update input manager
        self.input_manager.update(delta_time)
        
        # Update game engine
        self.game_engine.update(delta_time)
        
    def draw(self):
        """Draw everything"""
        # Get current game state
        game_state = self.game_engine.state
        game_info = self.game_engine.get_game_info()
        sprites = self.game_engine.get_sprites()
        
        # Draw everything
        self.ui_manager.draw_all(
            game_state, game_info, sprites,
            self.game_engine.powerup_system,
            self.game_engine.achievement_system,
            self.game_engine.game_mode_manager,
            self.game_engine.statistics_system
        )
        
        # Draw cursor on top
        if self.game_engine.cursor:
            self.screen.blit(self.game_engine.cursor.image, self.game_engine.cursor.rect)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        print("🎮 Iniciando PyHunt Ultimate...")
        print("🤖 IA Avanzada con múltiples modos de juego")
        print("📋 Controles:")
        print("   • Mouse: Mover cursor y disparar")
        print("   • P: Pausar")
        print("   • ESC: Salir")
        print("   • 1-5: Navegar menús")
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
        
        if self.gesture_controller:
            self.gesture_controller.stop()
            
        pygame.quit()

def main():
    """Main entry point"""
    print("🦆 PyHunt Ultimate")
    print("=" * 50)
    print("Duck Hunt con IA Avanzada y múltiples modos!")
    
    # Check if user wants to use gestures
    use_gestures = False
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--gestures', '-g']:
        use_gestures = True
        print("🎯 Modo: Mouse + Gestos")
    else:
        print("🎯 Modo: Solo mouse/touchpad")
    
    try:
        # Create and run game
        game = EnhancedDuckHuntGame(use_gestures=use_gestures)
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Juego interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 