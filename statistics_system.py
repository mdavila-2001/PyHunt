"""
Statistics and Leaderboard System for PyHunt
Tracks player performance and maintains leaderboards
"""
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

@dataclass
class GameSession:
    """Represents a single game session"""
    timestamp: str
    mode: str
    score: int
    ducks_shot: int
    total_shots: int
    accuracy: float
    time_remaining: int
    ai_level: int
    duration: int  # Actual game duration in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        return cls(**data)

@dataclass
class PlayerStats:
    """Player statistics summary"""
    total_games: int
    total_score: int
    total_ducks_shot: int
    total_shots: int
    best_score: int
    best_accuracy: float
    best_ducks_shot: int
    average_score: float
    average_accuracy: float
    total_play_time: int  # in seconds
    favorite_mode: str
    current_streak: int
    longest_streak: int
    achievements_unlocked: int
    total_achievement_points: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerStats':
        return cls(**data)

@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    rank: int
    player_name: str
    score: int
    mode: str
    timestamp: str
    accuracy: float
    ducks_shot: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        return cls(**data)

class StatisticsSystem:
    """Main statistics system"""
    
    def __init__(self):
        self.sessions: List[GameSession] = []
        self.player_stats: Optional[PlayerStats] = None
        self.leaderboards: Dict[str, List[LeaderboardEntry]] = {}
        
        # Load existing data
        self.load_data()
        
        # Initialize player stats if not exists
        if not self.player_stats:
            self.player_stats = self._create_empty_stats()
            
    def _create_empty_stats(self) -> PlayerStats:
        """Create empty player statistics"""
        return PlayerStats(
            total_games=0,
            total_score=0,
            total_ducks_shot=0,
            total_shots=0,
            best_score=0,
            best_accuracy=0.0,
            best_ducks_shot=0,
            average_score=0.0,
            average_accuracy=0.0,
            total_play_time=0,
            favorite_mode="Clásico",
            current_streak=0,
            longest_streak=0,
            achievements_unlocked=0,
            total_achievement_points=0
        )
        
    def record_game_session(self, game_info: Dict[str, Any], mode: str):
        """Record a completed game session"""
        # Calculate actual game duration
        duration = (game_info.get('game_time', 60000) - game_info.get('time_remaining', 0)) // 1000
        
        session = GameSession(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            score=game_info.get('score', 0),
            ducks_shot=game_info.get('ducks_shot', 0),
            total_shots=game_info.get('total_shots', 0),
            accuracy=game_info.get('accuracy', 0.0),
            time_remaining=game_info.get('time_remaining', 0),
            ai_level=game_info.get('ai_level', 1),
            duration=duration
        )
        
        self.sessions.append(session)
        self._update_player_stats(session)
        self._update_leaderboards(session)
        self.save_data()
        
    def _update_player_stats(self, session: GameSession):
        """Update player statistics with new session"""
        stats = self.player_stats
        
        # Basic counters
        stats.total_games += 1
        stats.total_score += session.score
        stats.total_ducks_shot += session.ducks_shot
        stats.total_shots += session.total_shots
        stats.total_play_time += session.duration
        
        # Best records
        if session.score > stats.best_score:
            stats.best_score = session.score
        if session.accuracy > stats.best_accuracy:
            stats.best_accuracy = session.accuracy
        if session.ducks_shot > stats.best_ducks_shot:
            stats.best_ducks_shot = session.ducks_shot
            
        # Averages
        stats.average_score = stats.total_score / stats.total_games
        stats.average_accuracy = (stats.total_ducks_shot / max(1, stats.total_shots)) * 100
        
        # Favorite mode
        mode_counts = {}
        for s in self.sessions:
            mode_counts[s.mode] = mode_counts.get(s.mode, 0) + 1
        if mode_counts:
            stats.favorite_mode = max(mode_counts, key=mode_counts.get)
            
        # Streak calculation
        self._update_streaks(session)
        
    def _update_streaks(self, session: GameSession):
        """Update win/loss streaks"""
        stats = self.player_stats
        
        # Simple streak: consider it a "win" if score > 0
        if session.score > 0:
            stats.current_streak += 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
        else:
            stats.current_streak = 0
            
    def _update_leaderboards(self, session: GameSession):
        """Update leaderboards with new session"""
        # Overall leaderboard
        if 'overall' not in self.leaderboards:
            self.leaderboards['overall'] = []
            
        entry = LeaderboardEntry(
            rank=0,  # Will be calculated
            player_name="Player",  # Could be configurable
            score=session.score,
            mode=session.mode,
            timestamp=session.timestamp,
            accuracy=session.accuracy,
            ducks_shot=session.ducks_shot
        )
        
        self.leaderboards['overall'].append(entry)
        
        # Mode-specific leaderboard
        if session.mode not in self.leaderboards:
            self.leaderboards[session.mode] = []
            
        mode_entry = LeaderboardEntry(
            rank=0,
            player_name="Player",
            score=session.score,
            mode=session.mode,
            timestamp=session.timestamp,
            accuracy=session.accuracy,
            ducks_shot=session.ducks_shot
        )
        
        self.leaderboards[session.mode].append(mode_entry)
        
        # Sort and rank leaderboards
        self._sort_leaderboards()
        
    def _sort_leaderboards(self):
        """Sort all leaderboards by score and assign ranks"""
        for leaderboard_name, entries in self.leaderboards.items():
            # Sort by score (descending), then by accuracy (descending)
            entries.sort(key=lambda x: (x.score, x.accuracy), reverse=True)
            
            # Assign ranks
            for i, entry in enumerate(entries):
                entry.rank = i + 1
                
            # Keep only top 100 entries
            self.leaderboards[leaderboard_name] = entries[:100]
            
    def get_player_stats(self) -> PlayerStats:
        """Get current player statistics"""
        return self.player_stats
        
    def get_leaderboard(self, mode: str = "overall", limit: int = 10) -> List[LeaderboardEntry]:
        """Get leaderboard for specific mode"""
        if mode not in self.leaderboards:
            return []
        return self.leaderboards[mode][:limit]
        
    def get_recent_games(self, limit: int = 10) -> List[GameSession]:
        """Get recent game sessions"""
        return sorted(self.sessions, key=lambda x: x.timestamp, reverse=True)[:limit]
        
    def get_mode_stats(self, mode: str) -> Dict[str, Any]:
        """Get statistics for a specific game mode"""
        mode_sessions = [s for s in self.sessions if s.mode == mode]
        
        if not mode_sessions:
            return {}
            
        scores = [s.score for s in mode_sessions]
        accuracies = [s.accuracy for s in mode_sessions]
        ducks_shot = [s.ducks_shot for s in mode_sessions]
        
        return {
            'total_games': len(mode_sessions),
            'average_score': statistics.mean(scores),
            'best_score': max(scores),
            'average_accuracy': statistics.mean(accuracies),
            'best_accuracy': max(accuracies),
            'total_ducks_shot': sum(ducks_shot),
            'best_ducks_shot': max(ducks_shot),
            'total_play_time': sum(s.duration for s in mode_sessions)
        }
        
    def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Filter sessions for this date
            day_sessions = [
                s for s in self.sessions 
                if s.timestamp.startswith(date_str)
            ]
            
            if day_sessions:
                daily_stats.append({
                    'date': date_str,
                    'games_played': len(day_sessions),
                    'total_score': sum(s.score for s in day_sessions),
                    'average_accuracy': statistics.mean(s.accuracy for s in day_sessions),
                    'total_ducks_shot': sum(s.ducks_shot for s in day_sessions),
                    'play_time': sum(s.duration for s in day_sessions)
                })
            else:
                daily_stats.append({
                    'date': date_str,
                    'games_played': 0,
                    'total_score': 0,
                    'average_accuracy': 0.0,
                    'total_ducks_shot': 0,
                    'play_time': 0
                })
                
        return daily_stats
        
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        if len(self.sessions) < 2:
            return {}
            
        # Get last 20 sessions for trend analysis
        recent_sessions = sorted(self.sessions, key=lambda x: x.timestamp)[-20:]
        
        scores = [s.score for s in recent_sessions]
        accuracies = [s.accuracy for s in recent_sessions]
        
        # Calculate trends (simple linear regression)
        n = len(scores)
        if n > 1:
            x_values = list(range(n))
            
            # Score trend
            score_slope = self._calculate_slope(x_values, scores)
            
            # Accuracy trend
            accuracy_slope = self._calculate_slope(x_values, accuracies)
            
            return {
                'score_trend': score_slope,
                'accuracy_trend': accuracy_slope,
                'improving_score': score_slope > 0,
                'improving_accuracy': accuracy_slope > 0,
                'sessions_analyzed': n
            }
            
        return {}
        
    def _calculate_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate slope of linear regression"""
        n = len(x_values)
        if n < 2:
            return 0.0
            
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
        
    def update_achievement_stats(self, unlocked_count: int, total_points: int):
        """Update achievement-related statistics"""
        if self.player_stats:
            self.player_stats.achievements_unlocked = unlocked_count
            self.player_stats.total_achievement_points = total_points
            self.save_data()
            
    def save_data(self):
        """Save all statistics data to files"""
        # Save sessions
        sessions_data = [s.to_dict() for s in self.sessions]
        with open('game_sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            
        # Save player stats
        if self.player_stats:
            with open('player_stats.json', 'w', encoding='utf-8') as f:
                json.dump(self.player_stats.to_dict(), f, indent=2, ensure_ascii=False)
                
        # Save leaderboards
        leaderboards_data = {}
        for mode, entries in self.leaderboards.items():
            leaderboards_data[mode] = [e.to_dict() for e in entries]
            
        with open('leaderboards.json', 'w', encoding='utf-8') as f:
            json.dump(leaderboards_data, f, indent=2, ensure_ascii=False)
            
    def load_data(self):
        """Load all statistics data from files"""
        # Load sessions
        try:
            with open('game_sessions.json', 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
                self.sessions = [GameSession.from_dict(data) for data in sessions_data]
        except FileNotFoundError:
            self.sessions = []
            
        # Load player stats
        try:
            with open('player_stats.json', 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
                self.player_stats = PlayerStats.from_dict(stats_data)
        except FileNotFoundError:
            self.player_stats = None
            
        # Load leaderboards
        try:
            with open('leaderboards.json', 'r', encoding='utf-8') as f:
                leaderboards_data = json.load(f)
                self.leaderboards = {}
                for mode, entries_data in leaderboards_data.items():
                    self.leaderboards[mode] = [LeaderboardEntry.from_dict(data) for data in entries_data]
        except FileNotFoundError:
            self.leaderboards = {}
            
    def reset_all_data(self):
        """Reset all statistics data"""
        self.sessions.clear()
        self.player_stats = self._create_empty_stats()
        self.leaderboards.clear()
        self.save_data()
        
    def export_data(self, filename: str = "pyhunt_stats_export.json"):
        """Export all statistics data to a single file"""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'sessions': [s.to_dict() for s in self.sessions],
            'player_stats': self.player_stats.to_dict() if self.player_stats else None,
            'leaderboards': {
                mode: [e.to_dict() for e in entries]
                for mode, entries in self.leaderboards.items()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        return filename 