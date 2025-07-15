"""
Game Modes System for PyHunt
Offers different gameplay experiences and challenges
"""
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import random
import math

class GameMode(Enum):
    """Available game modes"""
    CLASSIC = "classic"
    SURVIVAL = "survival"
    TIME_ATTACK = "time_attack"
    PRECISION = "precision"
    BOSS_RUSH = "boss_rush"
    INFINITE = "infinite"
    CHALLENGE = "challenge"

class GameModeConfig:
    """Configuration for a specific game mode"""
    
    def __init__(self, name: str, description: str, duration: int, 
                 spawn_delay: int, ai_start_level: int, special_rules: Dict[str, Any]):
        self.name = name
        self.description = description
        self.duration = duration  # milliseconds, 0 for infinite
        self.spawn_delay = spawn_delay
        self.ai_start_level = ai_start_level
        self.special_rules = special_rules
        
    def get_description(self) -> str:
        """Get full description with rules"""
        desc = f"{self.description}\n\n"
        desc += f"⏱️ Duración: {self.duration // 1000}s" if self.duration > 0 else "⏱️ Duración: Infinita"
        desc += f"\n🎯 IA inicial: Nivel {self.ai_start_level}"
        
        if self.special_rules:
            desc += "\n\n📋 Reglas especiales:"
            for rule, value in self.special_rules.items():
                desc += f"\n• {rule}: {value}"
                
        return desc

class GameModeManager:
    """Manages different game modes"""
    
    def __init__(self):
        self.modes: Dict[GameMode, GameModeConfig] = {}
        self.current_mode = GameMode.CLASSIC
        self._init_modes()
        
    def _init_modes(self):
        """Initialize all game modes"""
        self.modes[GameMode.CLASSIC] = GameModeConfig(
            name="Clásico",
            description="El modo original de Duck Hunt. Dispara patos en 60 segundos.",
            duration=60000,
            spawn_delay=2000,
            ai_start_level=1,
            special_rules={}
        )
        
        self.modes[GameMode.SURVIVAL] = GameModeConfig(
            name="Supervivencia",
            description="Los patos se vuelven más rápidos y agresivos con el tiempo. ¡Sobrevive el mayor tiempo posible!",
            duration=0,  # Infinite
            spawn_delay=1500,
            ai_start_level=3,
            special_rules={
                "IA aumenta cada 30s": "Sí",
                "Velocidad aumenta": "Progresiva",
                "Puntos por tiempo": "Sí"
            }
        )
        
        self.modes[GameMode.TIME_ATTACK] = GameModeConfig(
            name="Contra Reloj",
            description="Dispara tantos patos como puedas en 30 segundos. ¡Cada segundo cuenta!",
            duration=30000,
            spawn_delay=1000,
            ai_start_level=2,
            special_rules={
                "Tiempo limitado": "30s",
                "Spawn rápido": "1s",
                "Bonus por velocidad": "Sí"
            }
        )
        
        self.modes[GameMode.PRECISION] = GameModeConfig(
            name="Precisión",
            description="Solo tienes 10 disparos. ¡Cada tiro debe contar!",
            duration=0,  # No time limit
            spawn_delay=3000,
            ai_start_level=1,
            special_rules={
                "Disparos limitados": "10",
                "Puntos por precisión": "Dobles",
                "Penalización por fallo": "Sí"
            }
        )
        
        self.modes[GameMode.BOSS_RUSH] = GameModeConfig(
            name="Jefe Final",
            description="Enfréntate a patos gigantes y poderosos. ¡Necesitarás múltiples disparos!",
            duration=120000,  # 2 minutes
            spawn_delay=5000,
            ai_start_level=5,
            special_rules={
                "Patos gigantes": "Sí",
                "Múltiples disparos": "Requeridos",
                "Puntos extra": "Por jefe"
            }
        )
        
        self.modes[GameMode.INFINITE] = GameModeConfig(
            name="Infinito",
            description="Juego sin fin. Los patos seguirán apareciendo hasta que decidas parar.",
            duration=0,
            spawn_delay=2500,
            ai_start_level=1,
            special_rules={
                "Sin límite de tiempo": "Sí",
                "IA adaptativa": "Sí",
                "Guardado de progreso": "Sí"
            }
        )
        
        self.modes[GameMode.CHALLENGE] = GameModeConfig(
            name="Desafío",
            description="Modo aleatorio con reglas cambiantes. ¡Nunca sabes qué esperar!",
            duration=90000,  # 90 seconds
            spawn_delay=2000,
            ai_start_level=4,
            special_rules={
                "Reglas aleatorias": "Sí",
                "Eventos especiales": "Sí",
                "Recompensas únicas": "Sí"
            }
        )
        
    def get_mode(self, mode: GameMode) -> Optional[GameModeConfig]:
        """Get configuration for a specific mode"""
        return self.modes.get(mode)
        
    def get_all_modes(self) -> Dict[GameMode, GameModeConfig]:
        """Get all available modes"""
        return self.modes.copy()
        
    def set_current_mode(self, mode: GameMode):
        """Set current game mode"""
        if mode in self.modes:
            self.current_mode = mode
            
    def get_current_mode(self) -> GameModeConfig:
        """Get current mode configuration"""
        return self.modes[self.current_mode]
        
    def apply_mode_rules(self, game_engine) -> Dict[str, Any]:
        """Apply current mode rules to game engine"""
        config = self.get_current_mode()
        rules = {}
        
        # Apply basic settings
        game_engine.game_time = config.duration
        game_engine.spawn_delay = config.spawn_delay
        game_engine.ai_level = config.ai_start_level
        
        # Apply special rules based on mode
        if self.current_mode == GameMode.SURVIVAL:
            rules = self._apply_survival_rules(game_engine)
        elif self.current_mode == GameMode.TIME_ATTACK:
            rules = self._apply_time_attack_rules(game_engine)
        elif self.current_mode == GameMode.PRECISION:
            rules = self._apply_precision_rules(game_engine)
        elif self.current_mode == GameMode.BOSS_RUSH:
            rules = self._apply_boss_rush_rules(game_engine)
        elif self.current_mode == GameMode.CHALLENGE:
            rules = self._apply_challenge_rules(game_engine)
            
        return rules
        
    def _apply_survival_rules(self, game_engine) -> Dict[str, Any]:
        """Apply survival mode rules"""
        rules = {
            'survival_mode': True,
            'ai_increase_interval': 30000,  # 30 seconds
            'ai_increase_amount': 1,
            'speed_increase_factor': 1.1,
            'time_bonus_points': 10  # Points per second survived
        }
        
        # Add survival-specific attributes to game engine
        game_engine.survival_timer = 0
        game_engine.survival_level = 1
        
        return rules
        
    def _apply_time_attack_rules(self, game_engine) -> Dict[str, Any]:
        """Apply time attack mode rules"""
        rules = {
            'time_attack_mode': True,
            'speed_bonus_multiplier': 2.0,
            'rapid_spawn': True
        }
        
        return rules
        
    def _apply_precision_rules(self, game_engine) -> Dict[str, Any]:
        """Apply precision mode rules"""
        rules = {
            'precision_mode': True,
            'max_shots': 10,
            'precision_bonus': 2.0,
            'miss_penalty': -50
        }
        
        # Add precision-specific attributes
        game_engine.shots_remaining = 10
        
        return rules
        
    def _apply_boss_rush_rules(self, game_engine) -> Dict[str, Any]:
        """Apply boss rush mode rules"""
        rules = {
            'boss_rush_mode': True,
            'boss_health': 3,
            'boss_size_multiplier': 2.0,
            'boss_points': 500
        }
        
        return rules
        
    def _apply_challenge_rules(self, game_engine) -> Dict[str, Any]:
        """Apply challenge mode rules"""
        # Random challenge selection
        challenges = [
            'inverted_controls',
            'speed_boost',
            'accuracy_required',
            'limited_ammo',
            'moving_targets'
        ]
        
        selected_challenge = random.choice(challenges)
        
        rules = {
            'challenge_mode': True,
            'current_challenge': selected_challenge,
            'challenge_duration': 15000  # 15 seconds per challenge
        }
        
        # Apply specific challenge
        if selected_challenge == 'inverted_controls':
            rules['inverted_mouse'] = True
        elif selected_challenge == 'speed_boost':
            rules['player_speed_boost'] = 2.0
        elif selected_challenge == 'accuracy_required':
            rules['min_accuracy'] = 80
        elif selected_challenge == 'limited_ammo':
            rules['ammo_limit'] = 5
        elif selected_challenge == 'moving_targets':
            rules['target_speed_multiplier'] = 1.5
            
        return rules
        
    def update_mode_specific_logic(self, game_engine, delta_time: float):
        """Update mode-specific game logic"""
        config = self.get_current_mode()
        
        if self.current_mode == GameMode.SURVIVAL:
            self._update_survival_logic(game_engine, delta_time)
        elif self.current_mode == GameMode.CHALLENGE:
            self._update_challenge_logic(game_engine, delta_time)
            
    def _update_survival_logic(self, game_engine, delta_time: float):
        """Update survival mode logic"""
        game_engine.survival_timer += delta_time * 1000
        
        # Increase AI level every 30 seconds
        if game_engine.survival_timer >= 30000:
            game_engine.ai_level = min(10, game_engine.ai_level + 1)
            game_engine.survival_timer = 0
            game_engine.survival_level += 1
            
            # Increase duck speed
            for duck in game_engine.ducks:
                duck.speed *= 1.1
                
    def _update_challenge_logic(self, game_engine, delta_time: float):
        """Update challenge mode logic"""
        if not hasattr(game_engine, 'challenge_timer'):
            game_engine.challenge_timer = 0
            
        game_engine.challenge_timer += delta_time * 1000
        
        # Change challenge every 15 seconds
        if game_engine.challenge_timer >= 15000:
            # Apply new random challenge
            self._apply_challenge_rules(game_engine)
            game_engine.challenge_timer = 0
            
    def get_mode_description(self, mode: GameMode) -> str:
        """Get description for a specific mode"""
        config = self.modes.get(mode)
        if config:
            return config.get_description()
        return "Modo no disponible"
        
    def get_mode_list(self) -> List[tuple]:
        """Get list of modes for UI selection"""
        return [(mode, config.name, config.description) 
                for mode, config in self.modes.items()] 