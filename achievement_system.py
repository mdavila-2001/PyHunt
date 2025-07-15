"""
Achievement System for PyHunt
Tracks player accomplishments and provides rewards
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class Achievement:
    """Individual achievement class"""
    
    def __init__(self, id: str, name: str, description: str, 
                 icon: str, points: int, condition: Dict[str, Any]):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.condition = condition
        self.unlocked = False
        self.unlock_date = None
        
    def check_condition(self, game_stats: Dict[str, Any]) -> bool:
        """Check if achievement condition is met"""
        if self.unlocked:
            return False
            
        for key, value in self.condition.items():
            if key not in game_stats:
                return False
            if game_stats[key] < value:
                return False
        return True
        
    def unlock(self):
        """Unlock the achievement"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points': self.points,
            'condition': self.condition,
            'unlocked': self.unlocked,
            'unlock_date': self.unlock_date
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """Create achievement from dictionary"""
        achievement = cls(
            data['id'], data['name'], data['description'],
            data['icon'], data['points'], data['condition']
        )
        achievement.unlocked = data.get('unlocked', False)
        achievement.unlock_date = data.get('unlock_date')
        return achievement

class AchievementSystem:
    """Main achievement system"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.total_points = 0
        self.unlocked_count = 0
        
        # Initialize achievements
        self._init_achievements()
        
        # Load progress
        self.load_progress()
        
    def _init_achievements(self):
        """Initialize all achievements"""
        achievements_data = [
            # Accuracy achievements
            {
                'id': 'sharp_shooter',
                'name': 'Sharp Shooter',
                'description': 'Achieve 90% accuracy in a single game',
                'icon': '🎯',
                'points': 100,
                'condition': {'accuracy': 90}
            },
            {
                'id': 'dead_eye',
                'name': 'Dead Eye',
                'description': 'Achieve 95% accuracy in a single game',
                'icon': '👁️',
                'points': 200,
                'condition': {'accuracy': 95}
            },
            {
                'id': 'perfect_shot',
                'name': 'Perfect Shot',
                'description': 'Achieve 100% accuracy in a single game',
                'icon': '💯',
                'points': 500,
                'condition': {'accuracy': 100}
            },
            
            # Score achievements
            {
                'id': 'duck_hunter',
                'name': 'Duck Hunter',
                'description': 'Score 1000 points in a single game',
                'icon': '🦆',
                'points': 50,
                'condition': {'score': 1000}
            },
            {
                'id': 'duck_master',
                'name': 'Duck Master',
                'description': 'Score 2000 points in a single game',
                'icon': '🏆',
                'points': 150,
                'condition': {'score': 2000}
            },
            {
                'id': 'duck_legend',
                'name': 'Duck Legend',
                'description': 'Score 5000 points in a single game',
                'icon': '👑',
                'points': 500,
                'condition': {'score': 5000}
            },
            
            # Ducks shot achievements
            {
                'id': 'first_blood',
                'name': 'First Blood',
                'description': 'Shoot your first duck',
                'icon': '🩸',
                'points': 10,
                'condition': {'ducks_shot': 1}
            },
            {
                'id': 'duck_slayer',
                'name': 'Duck Slayer',
                'description': 'Shoot 10 ducks in a single game',
                'icon': '⚔️',
                'points': 100,
                'condition': {'ducks_shot': 10}
            },
            {
                'id': 'duck_annihilator',
                'name': 'Duck Annihilator',
                'description': 'Shoot 20 ducks in a single game',
                'icon': '💀',
                'points': 300,
                'condition': {'ducks_shot': 20}
            },
            
            # AI level achievements
            {
                'id': 'ai_challenger',
                'name': 'AI Challenger',
                'description': 'Reach AI level 5',
                'icon': '🤖',
                'points': 200,
                'condition': {'ai_level': 5}
            },
            {
                'id': 'ai_master',
                'name': 'AI Master',
                'description': 'Reach AI level 10',
                'icon': '🧠',
                'points': 500,
                'condition': {'ai_level': 10}
            },
            
            # Games played achievements
            {
                'id': 'dedicated_hunter',
                'name': 'Dedicated Hunter',
                'description': 'Play 10 games',
                'icon': '🎮',
                'points': 50,
                'condition': {'games_played': 10}
            },
            {
                'id': 'veteran_hunter',
                'name': 'Veteran Hunter',
                'description': 'Play 50 games',
                'icon': '🎖️',
                'points': 200,
                'condition': {'games_played': 50}
            },
            
            # Special achievements
            {
                'id': 'speed_demon',
                'name': 'Speed Demon',
                'description': 'Shoot 5 ducks in under 30 seconds',
                'icon': '⚡',
                'points': 150,
                'condition': {'ducks_shot': 5, 'time_remaining': 30000}
            },
            {
                'id': 'efficient_hunter',
                'name': 'Efficient Hunter',
                'description': 'Shoot 10 ducks with 100% accuracy',
                'icon': '🎯',
                'points': 400,
                'condition': {'ducks_shot': 10, 'accuracy': 100}
            }
        ]
        
        for data in achievements_data:
            achievement = Achievement(**data)
            self.achievements[achievement.id] = achievement
            
    def check_achievements(self, game_stats: Dict[str, Any]) -> List[Achievement]:
        """Check and unlock achievements based on game stats"""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if achievement.check_condition(game_stats):
                achievement.unlock()
                newly_unlocked.append(achievement)
                self.unlocked_count += 1
                self.total_points += achievement.points
                
        if newly_unlocked:
            self.save_progress()
            
        return newly_unlocked
        
    def get_achievement_progress(self) -> Dict[str, Any]:
        """Get achievement progress summary"""
        return {
            'total_achievements': len(self.achievements),
            'unlocked_count': self.unlocked_count,
            'total_points': self.total_points,
            'completion_percentage': (self.unlocked_count / len(self.achievements)) * 100
        }
        
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get list of unlocked achievements"""
        return [a for a in self.achievements.values() if a.unlocked]
        
    def get_locked_achievements(self) -> List[Achievement]:
        """Get list of locked achievements"""
        return [a for a in self.achievements.values() if not a.unlocked]
        
    def get_achievement_by_id(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID"""
        return self.achievements.get(achievement_id)
        
    def save_progress(self):
        """Save achievement progress to file"""
        data = {
            'total_points': self.total_points,
            'unlocked_count': self.unlocked_count,
            'achievements': {aid: a.to_dict() for aid, a in self.achievements.items()}
        }
        
        with open('achievements.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def load_progress(self):
        """Load achievement progress from file"""
        try:
            with open('achievements.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.total_points = data.get('total_points', 0)
            self.unlocked_count = data.get('unlocked_count', 0)
            
            achievements_data = data.get('achievements', {})
            for aid, a_data in achievements_data.items():
                if aid in self.achievements:
                    self.achievements[aid] = Achievement.from_dict(a_data)
                    
        except FileNotFoundError:
            # First time running, create new file
            self.save_progress()
            
    def reset_progress(self):
        """Reset all achievement progress"""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_date = None
            
        self.total_points = 0
        self.unlocked_count = 0
        self.save_progress() 