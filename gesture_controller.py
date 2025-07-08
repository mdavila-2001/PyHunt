"""
Gesture Controller Module
Handles hand gesture detection and maps gestures to game actions
"""
import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple, Dict, Any

class GestureController:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.thread = None
        
        # Gesture detection parameters
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Current gesture state
        self.current_gesture = "none"
        self.hand_center = None
        self.gesture_confidence = 0.0
        
        # Gesture mapping
        self.gesture_actions = {
            "open_hand": "move_cursor",
            "closed_fist": "shoot",
            "pointing": "aim",
            "thumbs_up": "pause",
            "peace": "menu"
        }
        
        # Screen mapping (will be set by game)
        self.screen_width = 640
        self.screen_height = 480
        self.camera_width = 640
        self.camera_height = 480
        
    def start(self):
        """Start gesture detection in a separate thread"""
        if self.is_running:
            return
            
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
            
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        
        self.is_running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop gesture detection"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            
    def set_screen_dimensions(self, width: int, height: int):
        """Set screen dimensions for coordinate mapping"""
        self.screen_width = width
        self.screen_height = height
        
    def get_hand_center(self, contour) -> Optional[Tuple[int, int]]:
        """Calculate the center of a hand contour"""
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return None
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)
        
    def map_camera_to_screen(self, camera_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Map camera coordinates to screen coordinates"""
        if not camera_pos:
            return (self.screen_width // 2, self.screen_height // 2)
            
        x, y = camera_pos
        # Flip X axis and map to screen
        screen_x = int((self.camera_width - x) * self.screen_width / self.camera_width)
        screen_y = int(y * self.screen_height / self.camera_height)
        
        # Clamp to screen bounds
        screen_x = max(0, min(screen_x, self.screen_width))
        screen_y = max(0, min(screen_y, self.screen_height))
        
        return (screen_x, screen_y)
        
    def detect_gesture(self, contour) -> Tuple[str, float]:
        """Detect gesture from hand contour"""
        if contour is None or cv2.contourArea(contour) < 3000:
            return "none", 0.0
            
        # Calculate convex hull and defects
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is None or len(hull) < 3:
            return "none", 0.0
            
        defects = cv2.convexityDefects(contour, hull)
        if defects is None:
            return "none", 0.0
            
        # Count valid defects
        valid_defects = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            # Calculate angle to filter real defects
            a = np.linalg.norm(np.array(end) - np.array(start))
            b = np.linalg.norm(np.array(far) - np.array(start))
            c = np.linalg.norm(np.array(end) - np.array(far))
            angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c + 1e-5))
            
            if angle <= np.pi/2 and d > 10000:
                valid_defects += 1
                
        # Classify gesture based on defect count
        if valid_defects >= 4:
            return "open_hand", 0.9
        elif valid_defects == 0:
            return "closed_fist", 0.8
        elif valid_defects == 1:
            return "pointing", 0.7
        elif valid_defects == 2:
            return "peace", 0.6
        else:
            return "unknown", 0.3
            
    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to HSV and segment skin
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
            
            # Apply morphological operations
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get largest contour (hand)
                max_contour = max(contours, key=cv2.contourArea)
                
                # Detect gesture
                gesture, confidence = self.detect_gesture(max_contour)
                
                # Get hand center
                center = self.get_hand_center(max_contour)
                
                # Update state
                self.current_gesture = gesture
                self.gesture_confidence = confidence
                self.hand_center = center
                
                # Draw debug info on frame
                cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
                if center:
                    cv2.circle(frame, center, 7, (255, 0, 0), -1)
                    cv2.putText(frame, f'{gesture} ({confidence:.1f})', 
                              (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                self.current_gesture = "none"
                self.gesture_confidence = 0.0
                self.hand_center = None
                
            # Show debug window
            cv2.imshow('Gesture Detection', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
                break
                
        cv2.destroyAllWindows()
        
    def get_current_action(self) -> Tuple[str, Tuple[int, int], float]:
        """Get current action based on detected gesture"""
        action = self.gesture_actions.get(self.current_gesture, "none")
        screen_pos = self.map_camera_to_screen(self.hand_center)
        return action, screen_pos, self.gesture_confidence
        
    def get_gesture_info(self) -> Dict[str, Any]:
        """Get detailed gesture information"""
        return {
            "gesture": self.current_gesture,
            "confidence": self.gesture_confidence,
            "hand_center": self.hand_center,
            "screen_position": self.map_camera_to_screen(self.hand_center)
        } 