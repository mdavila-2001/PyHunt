"""
Duck Hunt with Gesture Recognition
Main game file that integrates all modules
"""
import pygame
import sys
import os
from typing import Optional

# Import our modules
from asset_manager import AssetManager
from game_engine import GameEngine, MENU, PLAYING, PAUSED, GAME_OVER
from ui_manager import UIManager
from input_manager import InputManager
from gesture_controller import GestureController

# Game constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 50

# Suppress pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

class DuckHuntGame:
    """Main game class that coordinates all modules"""
    
    def __init__(self, use_gestures: bool = True):
        # Initialize pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                             pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Duck Hunt - Con Reconocimiento de Gestos")
        
        # Hide system cursor
        pygame.mouse.set_visible(False)
        
        # Initialize modules
        self.asset_manager = AssetManager()
        self.game_engine = GameEngine(self.asset_manager)
        self.ui_manager = UIManager(self.screen, self.asset_manager)
        
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
        
        # Process actions
        if actions['quit']:
            self.running = False
            
        elif actions['start_game'] and self.game_engine.state == MENU:
            self.game_engine.start_game()
            
        elif actions['pause'] and self.game_engine.state in [PLAYING, PAUSED]:
            self.game_engine.toggle_pause()
            
        elif actions['reset'] and self.game_engine.state == GAME_OVER:
            self.game_engine.reset_game()
            
        elif actions['shoot'] and self.game_engine.state == PLAYING:
            self.game_engine.shoot(actions['cursor_position'])
            
        # Update cursor position
        cursor_pos = self.input_manager.get_cursor_position()
        self.game_engine.update_cursor(cursor_pos)
        
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
        
        # Get gesture info if available
        gesture_info = self.input_manager.get_gesture_info()
        
        # Draw everything
        self.ui_manager.draw_all(game_state, game_info, sprites, gesture_info)
        
        # Update display
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        print("🎮 Iniciando Duck Hunt con Reconocimiento de Gestos...")
        print("📋 Controles:")
        print("   • Mouse/Touchpad: Mover cursor y disparar")
        if self.gesture_controller:
            print("   • Mano abierta: Mover cursor")
            print("   • Mano cerrada: Disparar")
            print("   • Dedo índice: Apuntar")
            print("   • Paz: Volver al menú")
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
        
        if self.gesture_controller:
            self.gesture_controller.stop()
            
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    print("🦆 Duck Hunt con Reconocimiento de Gestos")
    print("=" * 50)
    
    # Check if user wants to use gestures
    use_gestures = True
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--no-gestures', '-n']:
        use_gestures = False
        print("🎯 Modo: Solo mouse/touchpad")
    else:
        print("🎯 Modo: Mouse/touchpad + Gestos")
    
    try:
        # Create and run game
        game = DuckHuntGame(use_gestures=use_gestures)
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Juego interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 