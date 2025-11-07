"""Analytics and Dashboard System for Kitchen Game"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os


@dataclass
class GameSession:
    """Represents a single game session"""
    session_id: str
    username: str
    start_time: str
    end_time: Optional[str] = None
    recipes_completed: int = 0
    recipes_failed: int = 0
    duration_seconds: float = 0.0


@dataclass
class AnalyticsData:
    """Analytics data summary"""
    total_games: int = 0
    total_recipes_completed: int = 0
    total_recipes_failed: int = 0
    total_time_played: float = 0.0
    success_rate: float = 0.0
    average_game_duration: float = 0.0
    average_recipes_per_game: float = 0.0


class Analytics:
    """Analytics and dashboard system"""
    
    def __init__(self, data_file: str = "analytics_data.json"):
        self.data_file = data_file
        self.sessions: List[Dict] = []
        self.current_session: Optional[GameSession] = None
        self._load_sessions()
    
    def _load_sessions(self):
        """Load session data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.sessions = json.load(f)
            except json.JSONDecodeError:
                self.sessions = []
    
    def _save_sessions(self):
        """Save session data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def start_session(self, username: str, session_id: Optional[str] = None):
        """Start a new game session"""
        if session_id is None:
            session_id = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = GameSession(
            session_id=session_id,
            username=username,
            start_time=datetime.now().isoformat()
        )
    
    def end_session(self):
        """End current game session"""
        if self.current_session:
            self.current_session.end_time = datetime.now().isoformat()
            
            # Calculate duration with error handling
            try:
                start = datetime.fromisoformat(self.current_session.start_time)
                end = datetime.fromisoformat(self.current_session.end_time)
                self.current_session.duration_seconds = (end - start).total_seconds()
            except (ValueError, TypeError) as e:
                # If timestamp parsing fails, log the error and use 0 as fallback
                print(f"Warning: Failed to parse session timestamps: {e}")
                self.current_session.duration_seconds = 0.0
            
            # Save session
            self.sessions.append(asdict(self.current_session))
            self._save_sessions()
            self.current_session = None
    
    def record_recipe_completed(self):
        """Record a completed recipe in current session"""
        if self.current_session:
            self.current_session.recipes_completed += 1
    
    def record_recipe_failed(self):
        """Record a failed recipe in current session"""
        if self.current_session:
            self.current_session.recipes_failed += 1
    
    def get_analytics(self, username: Optional[str] = None) -> AnalyticsData:
        """Get analytics data for user or all users"""
        # Filter sessions by username if provided
        filtered_sessions = self.sessions
        if username:
            filtered_sessions = [s for s in self.sessions if s["username"] == username]
        
        if not filtered_sessions:
            return AnalyticsData()
        
        total_games = len(filtered_sessions)
        total_recipes_completed = sum(s["recipes_completed"] for s in filtered_sessions)
        total_recipes_failed = sum(s["recipes_failed"] for s in filtered_sessions)
        total_time_played = sum(s["duration_seconds"] for s in filtered_sessions)
        
        # Calculate success rate
        total_recipes = total_recipes_completed + total_recipes_failed
        success_rate = (total_recipes_completed / total_recipes * 100) if total_recipes > 0 else 0.0
        
        # Calculate averages
        avg_duration = total_time_played / total_games if total_games > 0 else 0.0
        avg_recipes = total_recipes / total_games if total_games > 0 else 0.0
        
        return AnalyticsData(
            total_games=total_games,
            total_recipes_completed=total_recipes_completed,
            total_recipes_failed=total_recipes_failed,
            total_time_played=total_time_played,
            success_rate=success_rate,
            average_game_duration=avg_duration,
            average_recipes_per_game=avg_recipes
        )
    
    def display_dashboard(self, username: Optional[str] = None):
        """Display analytics dashboard"""
        analytics = self.get_analytics(username)
        
        title = f"Dashboard - {username}" if username else "Global Dashboard"
        print("\n" + "=" * 50)
        print(f"{title:^50}")
        print("=" * 50)
        
        print(f"\n📊 Game Statistics:")
        print(f"  Total Games Played: {analytics.total_games}")
        print(f"  Total Time Played: {analytics.total_time_played:.1f} seconds")
        print(f"  Average Game Duration: {analytics.average_game_duration:.1f} seconds")
        
        print(f"\n🍳 Recipe Statistics:")
        print(f"  Recipes Completed: {analytics.total_recipes_completed}")
        print(f"  Recipes Failed: {analytics.total_recipes_failed}")
        print(f"  Success Rate: {analytics.success_rate:.1f}%")
        print(f"  Average Recipes per Game: {analytics.average_recipes_per_game:.1f}")
        
        print("\n" + "=" * 50 + "\n")
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players by recipes completed"""
        # Aggregate data by username
        user_stats: Dict[str, Dict] = {}
        
        for session in self.sessions:
            username = session["username"]
            if username not in user_stats:
                user_stats[username] = {
                    "username": username,
                    "total_recipes": 0,
                    "success_rate": 0.0
                }
            
            user_stats[username]["total_recipes"] += session["recipes_completed"]
        
        # Calculate success rates
        for username in user_stats:
            analytics = self.get_analytics(username)
            user_stats[username]["success_rate"] = analytics.success_rate
        
        # Sort by total recipes completed
        leaderboard = sorted(
            user_stats.values(),
            key=lambda x: x["total_recipes"],
            reverse=True
        )[:limit]
        
        return leaderboard
    
    def display_leaderboard(self, limit: int = 10):
        """Display leaderboard"""
        leaderboard = self.get_leaderboard(limit)
        
        print("\n" + "=" * 50)
        print(f"{'🏆 Leaderboard - Top Players':^50}")
        print("=" * 50)
        
        if not leaderboard:
            print("\n  No data available yet\n")
        else:
            print(f"\n{'Rank':<6} {'Username':<20} {'Recipes':<10} {'Success %':<10}")
            print("-" * 50)
            
            for i, player in enumerate(leaderboard, 1):
                print(f"{i:<6} {player['username']:<20} {player['total_recipes']:<10} {player['success_rate']:.1f}%")
        
        print("\n" + "=" * 50 + "\n")


# Example usage
if __name__ == "__main__":
    analytics = Analytics()
    
    # Simulate a game session
    print("Starting game session for player1...")
    analytics.start_session("player1")
    
    # Simulate some gameplay
    analytics.record_recipe_completed()
    analytics.record_recipe_completed()
    analytics.record_recipe_failed()
    analytics.record_recipe_completed()
    
    import time
    time.sleep(2)  # Simulate game time
    
    print("Ending game session...")
    analytics.end_session()
    
    # Display dashboard
    analytics.display_dashboard("player1")
    
    # Display leaderboard
    analytics.display_leaderboard()
