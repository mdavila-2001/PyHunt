"""
Input Manager Module
Handles all input sources (keyboard, mouse, gestures)
"""
import pygame
from typing import Dict, Any, Optional, Tuple
from gesture_controller import GestureController

class InputManager:
    """Manages all input sources"""
    
    def __init__(self, gesture_controller: Optional[GestureController] = None):
        self.gesture_controller = gesture_controller
        self.use_gestures = gesture_controller is not None
        
        # Input state
        self.mouse_position = (0, 0)
        self.mouse_clicked = False
        self.key_pressed = None
        
        # Gesture state
        self.last_gesture_action = "none"
        self.gesture_cooldown = 0
        self.gesture_cooldown_time = 500  # milliseconds
        
    def update(self, delta_time: float):
        """Update input state"""
        # Update gesture cooldown
        if self.gesture_cooldown > 0:
            self.gesture_cooldown -= delta_time * 1000
            
        # Reset mouse click
        self.mouse_clicked = False
        self.key_pressed = None
        
    def handle_events(self, events) -> Dict[str, Any]:
        """Handle pygame events and return input actions"""
        actions = {
            'quit': False,
            'start_game': False,
            'pause': False,
            'reset': False,
            'shoot': False,
            'cursor_position': self.mouse_position
        }
        
        for event in events:
            if event.type == pygame.QUIT:
                actions['quit'] = True
                
            elif event.type == pygame.KEYDOWN:
                self.key_pressed = event.key
                
                if event.key == pygame.K_ESCAPE:
                    actions['quit'] = True
                elif event.key == pygame.K_RETURN:
                    actions['start_game'] = True
                elif event.key == pygame.K_p:
                    actions['pause'] = True
                elif event.key == pygame.K_r:
                    actions['reset'] = True
                    
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_position = event.pos
                actions['cursor_position'] = event.pos
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_clicked = True
                actions['shoot'] = True
                
        # Handle gesture inputs if available
        if self.use_gestures and self.gesture_cooldown <= 0:
            gesture_actions = self._handle_gesture_input()
            actions.update(gesture_actions)
            
        return actions
        
    def _handle_gesture_input(self) -> Dict[str, Any]:
        """Handle gesture-based input"""
        if not self.gesture_controller:
            return {}
            
        action, position, confidence = self.gesture_controller.get_current_action()
        
        # Only process gestures with sufficient confidence
        if confidence < 0.5:
            return {'cursor_position': self.mouse_position}
            
        actions = {'cursor_position': position}
        
        # Handle different gesture actions
        if action == "shoot" and self.last_gesture_action != "shoot":
            actions['shoot'] = True
            self.last_gesture_action = "shoot"
            self.gesture_cooldown = self.gesture_cooldown_time
            
        elif action == "pause" and self.last_gesture_action != "pause":
            actions['pause'] = True
            self.last_gesture_action = "pause"
            self.gesture_cooldown = self.gesture_cooldown_time
            
        elif action == "menu" and self.last_gesture_action != "menu":
            actions['reset'] = True
            self.last_gesture_action = "menu"
            self.gesture_cooldown = self.gesture_cooldown_time
            
        elif action == "move_cursor":
            self.last_gesture_action = "move_cursor"
            
        return actions
        
    def get_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position"""
        if self.use_gestures and self.gesture_controller:
            action, position, confidence = self.gesture_controller.get_current_action()
            if confidence >= 0.3:  # Lower threshold for movement
                return position
        return self.mouse_position
        
    def is_shooting(self) -> bool:
        """Check if shooting action is triggered"""
        return self.mouse_clicked or (
            self.use_gestures and 
            self.gesture_controller and 
            self.gesture_cooldown <= 0 and
            self._get_gesture_action() == "shoot"
        )
        
    def _get_gesture_action(self) -> str:
        """Get current gesture action"""
        if not self.gesture_controller:
            return "none"
        action, _, confidence = self.gesture_controller.get_current_action()
        return action if confidence >= 0.5 else "none"
        
    def get_gesture_info(self) -> Optional[Dict[str, Any]]:
        """Get gesture detection information"""
        if not self.gesture_controller:
            return None
        return self.gesture_controller.get_gesture_info()
        
    def enable_gestures(self, gesture_controller: GestureController):
        """Enable gesture input"""
        self.gesture_controller = gesture_controller
        self.use_gestures = True
        
    def disable_gestures(self):
        """Disable gesture input"""
        self.gesture_controller = None
        self.use_gestures = False 