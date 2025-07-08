"""
UI Manager Module
Handles all user interface elements, menus, and rendering
"""
import pygame
from typing import Dict, Any, Optional

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

class UIManager:
    """Manages all UI elements and rendering"""
    
    def __init__(self, screen: pygame.Surface, asset_manager):
        self.screen = screen
        self.asset_manager = asset_manager
        
        # Initialize fonts
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Screen dimensions
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
    def draw_menu(self):
        """Draw main menu"""
        # Clear screen
        self.screen.fill((135, 206, 250))  # Light blue background
        
        # Title
        title = self.big_font.render("DUCK HUNT", True, BLACK)
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Con Reconocimiento de Gestos", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Instructions
        instructions = [
            "Controles:",
            "• Mano abierta: Mover cursor",
            "• Mano cerrada: Disparar",
            "• Dedo índice: Apuntar",
            "• P: Pausar",
            "• ESC: Salir"
        ]
        
        y_offset = 220
        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30
            
        # Start instruction
        start_text = self.font.render("Presiona ENTER para comenzar", True, RED)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, 400))
        self.screen.blit(start_text, start_rect)
        
    def draw_hud(self, game_info: Dict[str, Any]):
        """Draw heads-up display during gameplay"""
        # Score
        score_text = self.font.render(f"Puntos: {game_info['score']}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Ducks shot
        ducks_text = self.font.render(f"Patos: {game_info['ducks_shot']}", True, WHITE)
        self.screen.blit(ducks_text, (10, 40))
        
        # Accuracy
        accuracy = game_info['accuracy']
        accuracy_text = self.font.render(f"Precisión: {accuracy:.1f}%", True, WHITE)
        self.screen.blit(accuracy_text, (10, 70))
        
        # Time remaining
        time_remaining = game_info['time_remaining'] // 1000  # Convert to seconds
        time_text = self.font.render(f"Tiempo: {time_remaining}s", True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (self.screen_width - 10, 10)
        self.screen.blit(time_text, time_rect)
        
        # Shots
        shots_text = self.font.render(f"Disparos: {game_info['total_shots']}", True, WHITE)
        shots_rect = shots_text.get_rect()
        shots_rect.topright = (self.screen_width - 10, 40)
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
        game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Puntuación Final: {game_info['score']}", True, WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 180))
        self.screen.blit(score_text, score_rect)
        
        # Ducks shot
        ducks_text = self.font.render(f"Patos Abatidos: {game_info['ducks_shot']}", True, WHITE)
        ducks_rect = ducks_text.get_rect(center=(self.screen_width // 2, 210))
        self.screen.blit(ducks_text, ducks_rect)
        
        # Accuracy
        accuracy = game_info['accuracy']
        accuracy_text = self.font.render(f"Precisión: {accuracy:.1f}%", True, WHITE)
        accuracy_rect = accuracy_text.get_rect(center=(self.screen_width // 2, 240))
        self.screen.blit(accuracy_text, accuracy_rect)
        
        # Total shots
        shots_text = self.font.render(f"Total de Disparos: {game_info['total_shots']}", True, WHITE)
        shots_rect = shots_text.get_rect(center=(self.screen_width // 2, 270))
        self.screen.blit(shots_text, shots_rect)
        
        # Performance rating
        rating = self._get_performance_rating(accuracy, game_info['ducks_shot'])
        rating_text = self.font.render(f"Calificación: {rating}", True, YELLOW)
        rating_rect = rating_text.get_rect(center=(self.screen_width // 2, 310))
        self.screen.blit(rating_text, rating_rect)
        
        # Restart instruction
        restart_text = self.font.render("Presiona R para jugar de nuevo", True, GREEN)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, 360))
        self.screen.blit(restart_text, restart_rect)
        
        # Exit instruction
        exit_text = self.font.render("Presiona ESC para salir", True, WHITE)
        exit_rect = exit_text.get_rect(center=(self.screen_width // 2, 390))
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
            
    def draw_gesture_info(self, gesture_info: Dict[str, Any]):
        """Draw gesture detection information"""
        if not gesture_info:
            return
            
        # Gesture status
        gesture = gesture_info.get('gesture', 'none')
        confidence = gesture_info.get('confidence', 0.0)
        
        # Background for gesture info
        info_bg = pygame.Surface((200, 80))
        info_bg.set_alpha(180)
        info_bg.fill(BLACK)
        self.screen.blit(info_bg, (10, self.screen_height - 90))
        
        # Gesture text
        gesture_text = self.small_font.render(f"Gesto: {gesture}", True, WHITE)
        self.screen.blit(gesture_text, (15, self.screen_height - 80))
        
        # Confidence text
        conf_text = self.small_font.render(f"Confianza: {confidence:.1f}", True, WHITE)
        self.screen.blit(conf_text, (15, self.screen_height - 60))
        
        # Position text
        pos = gesture_info.get('screen_position', (0, 0))
        pos_text = self.small_font.render(f"Pos: ({pos[0]}, {pos[1]})", True, WHITE)
        self.screen.blit(pos_text, (15, self.screen_height - 40))
        
    def draw_controls_help(self):
        """Draw controls help overlay"""
        # Semi-transparent background
        overlay = pygame.Surface((300, 200))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (self.screen_width - 310, 10))
        
        # Help text
        help_lines = [
            "Controles:",
            "👋 Mano abierta: Mover",
            "✊ Mano cerrada: Disparar",
            "👆 Dedo índice: Apuntar",
            "✌️ Paz: Menú",
            "👍 Pulgar: Pausar"
        ]
        
        y_offset = 20
        for line in help_lines:
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (self.screen_width - 300, y_offset))
            y_offset += 25
            
    def draw_all(self, game_state: int, game_info: Dict[str, Any], 
                 sprites: pygame.sprite.LayeredUpdates, gesture_info: Optional[Dict[str, Any]] = None):
        """Draw everything based on game state"""
        # Clear screen
        self.screen.fill((135, 206, 250))
        
        # Draw sprites
        sprites.draw(self.screen)
        
        # Draw UI based on state
        if game_state == MENU:
            self.draw_menu()
        elif game_state == PLAYING:
            self.draw_hud(game_info)
            if gesture_info:
                self.draw_gesture_info(gesture_info)
            self.draw_controls_help()
        elif game_state == PAUSED:
            self.draw_hud(game_info)
            self.draw_paused()
        elif game_state == GAME_OVER:
            self.draw_game_over(game_info) 