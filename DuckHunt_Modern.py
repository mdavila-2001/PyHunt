"""
    Modern Duck Hunt
    
    A Pygame-based implementation of the classic Duck Hunt game.
    This version replaces the old livewires dependency with pure Pygame.
"""
import pygame
import os
import random
import sys
from pygame import mixer

# Suppress PNG warnings
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='pygame')

# Initialize pygame and its modules
pygame.init()
mixer.init()

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Set up the display with hardware acceleration and double buffering
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.display.set_caption("Duck Hunt")
        
        # Hide the system cursor (we'll use our own cursor)
        pygame.mouse.set_visible(False)
        
        # Set window position and focus
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = MENU
        self.score = 0
        self.ducks_shot = 0
        self.total_shots = 0
        self.total_ducks = 0
        self.game_time = 60000  # 60 seconds in milliseconds
        self.start_time = 0
        
        # Load assets
        self.load_assets()
        
        # Create sprite groups using LayeredUpdates for proper z-ordering
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ducks = pygame.sprite.Group()
        
        # Create cursor
        self.cursor = Cursor(self)
        self.all_sprites.add(self.cursor)
        
        # Game objects
        self.background = Background(self)
        self.foreground = Foreground(self)
        self.all_sprites.add(self.background)
        self.all_sprites.add(self.foreground)
        
        # UI Elements
        self.font = pygame.font.SysFont('Arial', 30)
        self.big_font = pygame.font.SysFont('Arial', 50)
        
        # Game variables
        self.spawn_timer = 0
        self.spawn_delay = 2000  # milliseconds between duck spawns
        
    def load_assets(self):
        """Load all game assets"""
        # Create directories if they don't exist
        if not os.path.exists('Sprites'):
            os.makedirs('Sprites')
        if not os.path.exists('Sounds'):
            os.makedirs('Sounds')
            
        # Load sounds
        self.shot_sound = self.load_sound("shot.wav")
        self.beep_sound = self.load_sound("beep.wav")
        
        # Load images
        self.cursor_img = self.load_image("cursor.png")
        self.foreground_img = self.load_image("foreground.png")
        # Background is in the root directory, not in Sprites
        try:
            self.background_img = pygame.image.load("background.png").convert()
        except pygame.error:
            # Create a blue background if image not found
            self.background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_img.fill((135, 206, 250))  # Light blue sky
        
        self.paused_img = self.load_image("paused.png")
        
        # Load duck sprites
        self.duck_sprites = {
            'blue': self.load_duck_sprites('blue'),
            'red': self.load_duck_sprites('red'),
            'black': self.load_duck_sprites('black')
        }
    
    def load_image(self, filename, scale=1, use_alpha=True):
        """Load an image from the Sprites directory"""
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
            
            if scale != 1:
                new_width = int(image.get_width() * scale)
                new_height = int(image.get_height() * scale)
                image = pygame.transform.scale(image, (new_width, new_height))
                
            return image
        except pygame.error as e:
            print(f"Error loading image {filename}: {e}")
            # Return a placeholder surface if the image can't be loaded
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 255))  # Magenta placeholder
            return surf
    
    def load_sound(self, filename):
        """Load a sound from the Sounds directory"""
        try:
            path = os.path.join('Sounds', filename)
            return mixer.Sound(path)
        except:
            print(f"Warning: Could not load sound {filename}")
            # Return a silent sound if the file can't be loaded
            return mixer.Sound(buffer=bytearray(44))
    
    def load_duck_sprites(self, color):
        """Load all sprites for a duck of a specific color"""
        sprites = {}
        
        # Flying right (1-3)
        sprites['fly_right'] = [
            self.load_image(f"{color}/duck1.png"),
            self.load_image(f"{color}/duck2.png"),
            self.load_image(f"{color}/duck3.png")
        ]
        
        # Flying straight right (4-6)
        sprites['fly_straight_right'] = [
            self.load_image(f"{color}/duck4.png"),
            self.load_image(f"{color}/duck5.png"),
            self.load_image(f"{color}/duck6.png")
        ]
        
        # Flying left (7-9)
        sprites['fly_left'] = [
            self.load_image(f"{color}/duck7.png"),
            self.load_image(f"{color}/duck8.png"),
            self.load_image(f"{color}/duck9.png")
        ]
        
        # Flying straight left (10-12)
        sprites['fly_straight_left'] = [
            self.load_image(f"{color}/duck10.png"),
            self.load_image(f"{color}/duck11.png"),
            self.load_image(f"{color}/duck12.png")
        ]
        
        # Dying (13-15)
        sprites['die'] = [
            self.load_image(f"{color}/duckDie1.png"),
            self.load_image(f"{color}/duckDie2.png"),
            self.load_image(f"{color}/duckDie3.png")
        ]
        
        return sprites
    
    def spawn_duck(self):
        """Spawn a new duck"""
        # Randomly select duck color
        colors = ['blue', 'red', 'black']
        color = random.choice(colors)
        
        # Create and add the duck
        duck = Duck(self, color)
        self.ducks.add(duck)
        self.all_sprites.add(duck)
        self.total_ducks += 1
        
        return duck
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Handle mouse motion events
            if event.type == pygame.MOUSEMOTION:
                # Force cursor position update
                if hasattr(self, 'cursor'):
                    self.cursor.rect.center = event.pos
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_p and self.state in [PLAYING, PAUSED]:
                    self.toggle_pause()
                elif event.key == pygame.K_RETURN and self.state == MENU:
                    self.start_game()
                elif event.key == pygame.K_r and self.state == GAME_OVER:
                    self.reset_game()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if self.state == PLAYING:
                    self.shoot()
                elif self.state == GAME_OVER:
                    self.reset_game()
        
        return True
    
    def shoot(self):
        """Handle shooting"""
        self.total_shots += 1
        self.shot_sound.play()
        
        # Check for duck hits
        mouse_pos = pygame.mouse.get_pos()
        for duck in self.ducks:
            if duck.alive and duck.rect.collidepoint(mouse_pos):
                duck.hit()
                self.score += duck.points
                self.ducks_shot += 1
    
    def toggle_pause(self):
        """Toggle pause state"""
        if self.state == PLAYING:
            self.state = PAUSED
            pygame.mouse.set_visible(True)
        elif self.state == PAUSED:
            self.state = PLAYING
            pygame.mouse.set_visible(False)
    
    def start_game(self):
        """Start a new game"""
        self.state = PLAYING
        self.start_time = pygame.time.get_ticks()
        pygame.mouse.set_visible(False)
    
    def reset_game(self):
        """Reset the game to its initial state"""
        self.__init__()
    
    def update(self):
        """Update game state"""
        if self.state == PLAYING:
            # Update game time
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            self.game_time = max(0, 60000 - elapsed)
            
            # Check for game over
            if self.game_time <= 0:
                self.state = GAME_OVER
                pygame.mouse.set_visible(True)
                return
            
            # Spawn new ducks
            self.spawn_timer += self.clock.get_time()
            if self.spawn_timer >= self.spawn_delay and len(self.ducks) < 5:  # Max 5 ducks at once
                self.spawn_duck()
                self.spawn_timer = 0
                # Increase difficulty by decreasing spawn delay (but not below 1 second)
                self.spawn_delay = max(1000, self.spawn_delay - 50)
            
            # Update sprites
            self.all_sprites.update()
            
            # Remove dead ducks that are off screen
            for duck in self.ducks:
                if not duck.alive and (duck.rect.y > SCREEN_HEIGHT or duck.rect.x < -100 or duck.rect.x > SCREEN_WIDTH + 100):
                    duck.kill()
    
    def draw(self):
        """Draw everything"""
        # Clear the screen
        self.screen.fill(BLACK)
        
        # Draw background image if available
        if hasattr(self, 'background_img'):
            self.screen.blit(self.background_img, (0, 0))
        
        # Draw all sprites in proper order
        self.all_sprites.draw(self.screen)
        
        # Draw UI
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PAUSED:
            self.draw_paused()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        
        # Draw HUD
        self.draw_hud()
        
        # Update the display
        pygame.display.flip()
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw ducks shot
        ducks_text = self.font.render(f"Ducks: {self.ducks_shot}", True, WHITE)
        self.screen.blit(ducks_text, (10, 50))
        
        # Draw time remaining
        seconds = self.game_time // 1000
        time_text = self.font.render(f"Time: {seconds}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
    
    def draw_menu(self):
        """Draw the main menu"""
        title = self.big_font.render("DUCK HUNT", True, WHITE)
        subtitle = self.font.render("Click to Start", True, WHITE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
    
    def draw_paused(self):
        """Draw the paused screen"""
        paused_text = self.big_font.render("PAUSED", True, WHITE)
        continue_text = self.font.render("Press P to continue", True, WHITE)
        
        paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        self.screen.blit(paused_text, paused_rect)
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over = self.big_font.render("GAME OVER", True, WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        ducks_text = self.font.render(f"Ducks Shot: {self.ducks_shot} of {self.total_ducks}", True, WHITE)
        
        if self.total_shots > 0:
            accuracy = (self.ducks_shot / self.total_shots) * 100
            accuracy_text = self.font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
        else:
            accuracy_text = self.font.render("Accuracy: 0%", True, WHITE)
        
        restart_text = self.font.render("Click or press R to restart", True, WHITE)
        
        # Position text
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        ducks_rect = ducks_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        accuracy_rect = accuracy_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        
        # Draw text
        self.screen.blit(game_over, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(ducks_text, ducks_rect)
        self.screen.blit(accuracy_text, accuracy_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        # Initial setup
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(False)
        
        # Create a clock for consistent frame rate
        clock = pygame.time.Clock()
        running = True
        
        # Main game loop
        while running:
            # Cap the frame rate and get delta time
            dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Update mouse position
            pygame.event.pump()  # Process event queue
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()


class Cursor(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.cursor_img
        self.rect = self.image.get_rect()
        
        # Initialize cursor properties
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Set up custom cursor
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(False)
        
        # Create a transparent cursor
        surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
    
    def update(self):
        # Update position to follow the mouse
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] < 0 or mouse_pos[0] > SCREEN_WIDTH or mouse_pos[1] < 0 or mouse_pos[1] > SCREEN_HEIGHT:
            # If mouse is outside window, don't update position
            return
            
        self.rect.center = mouse_pos
        
        # Keep cursor on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Ensure cursor is always on top
        if self in self.game.all_sprites:
            self.game.all_sprites.move_to_front(self)


class Duck(pygame.sprite.Sprite):
    def __init__(self, game, color):
        super().__init__()
        self.game = game
        self.color = color
        self.sprites = game.duck_sprites[color]
        self.image = self.sprites['fly_right'][0]
        self.rect = self.image.get_rect()
        
        # Set initial position (off-screen bottom)
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.bottom = SCREEN_HEIGHT + 10
        
        # Movement
        self.speed_x = random.choice([-2, -1, 1, 2])
        self.speed_y = -2  # Start by moving up
        
        # State
        self.alive = True
        self.dying = False
        self.dead = False
        self.direction = 1 if self.speed_x > 0 else -1  # 1 for right, -1 for left
        self.straight = False
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.current_animation = 'fly_right'
        
        # Points based on color
        self.points = {'blue': 25, 'red': 50, 'black': 75}[color]
        
        # Timing
        self.direction_timer = 0
        self.direction_change_interval = 1000  # ms
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        delta_time = now - self.last_update
        self.last_update = now
        
        if not self.alive and not self.dying:
            self.die()
            return
        
        if self.dying:
            self.update_dying(delta_time)
        elif self.alive:
            self.update_alive(delta_time)
        
        # Update animation
        self.animate()
        
        # Keep duck on screen
        self.rect.clamp_ip(pygame.Rect(-100, -100, SCREEN_WIDTH + 200, SCREEN_HEIGHT + 200))
    
    def update_alive(self, delta_time):
        # Change direction occasionally
        self.direction_timer += delta_time
        if self.direction_timer > self.direction_change_interval:
            self.direction_timer = 0
            self.change_direction()
        
        # Move the duck
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off screen edges
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x = abs(self.speed_x)
            self.direction = 1
        elif self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed_x = -abs(self.speed_x)
            self.direction = -1
        
        # Randomly change between straight and diagonal flight
        if random.random() < 0.01:  # 1% chance each frame
            self.straight = not self.straight
            if self.straight:
                self.speed_y = 0
                self.speed_x = 2 * self.direction
            else:
                self.speed_y = -1
    
    def update_dying(self, delta_time):
        # Fall to the ground
        self.speed_x = 0
        self.speed_y = 5  # Fall speed
        
        # Move down
        self.rect.y += self.speed_y
        
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def change_direction(self):
        """Randomly change the duck's direction"""
        if random.random() < 0.3:  # 30% chance to change direction
            self.direction *= -1
            self.speed_x *= -1
        
        # Random vertical movement
        if not self.straight and random.random() < 0.5:
            self.speed_y = random.choice([-2, -1, 0, 1])
    
    def hit(self):
        """Called when the duck is shot"""
        if self.alive:
            self.alive = False
            self.dying = True
            self.current_animation = 'die'
            self.animation_frame = 0
            self.speed_y = 0  # Stop vertical movement
    
    def die(self):
        """Start death animation"""
        self.dying = True
        self.current_animation = 'die'
    
    def animate(self):
        """Update animation frame"""
        # Get the current animation sequence
        animation = self.sprites.get(self.current_animation, self.sprites['fly_right'])
        
        # Update animation frame
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(animation):
            if self.dying:
                self.animation_frame = len(animation) - 1  # Stay on last frame
            else:
                self.animation_frame = 0
        
        # Update image
        frame_index = int(self.animation_frame)
        if frame_index < len(animation):
            self.image = animation[frame_index]
            
            # Flip image if needed
            if self.direction < 0 and self.current_animation != 'die':
                self.image = pygame.transform.flip(self.image, True, False)
            
            # Update rect to keep center
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Background(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.background_img
        self.rect = self.image.get_rect()


class Foreground(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.foreground_img
        self.rect = self.image.get_rect()
        self.rect.bottom = 390  # Position at the bottom of the screen


if __name__ == "__main__":
    game = Game()
    game.run()
