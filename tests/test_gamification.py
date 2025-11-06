import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app
from gamification import GamificationManager


@pytest.fixture
def client():
    """Setup Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGamificationManager:
    """Test the GamificationManager class"""
    
    def test_initialization_empty(self):
        """Test initialization with no data"""
        manager = GamificationManager()
        assert manager.xp == 0
        assert manager.level == 1
        assert manager.total_sessions == 0
        assert manager.current_streak == 0
    
    def test_initialization_with_data(self):
        """Test initialization with existing data"""
        data = {
            'xp': 250,
            'level': 3,
            'total_sessions': 5,
            'current_streak': 2
        }
        manager = GamificationManager(data)
        assert manager.xp == 250
        assert manager.level == 3
        assert manager.total_sessions == 5
        assert manager.current_streak == 2
    
    def test_complete_pomodoro_awards_xp(self):
        """Test that completing a Pomodoro awards XP"""
        manager = GamificationManager()
        result = manager.complete_pomodoro(1500)
        
        assert result['xp_gained'] == 50
        assert manager.xp == 50
        assert manager.total_sessions == 1
    
    def test_level_up_at_100_xp(self):
        """Test level up at 100 XP"""
        manager = GamificationManager({'xp': 60})
        result = manager.complete_pomodoro(1500)
        
        assert manager.xp == 110
        assert manager.level == 2
        assert result['leveled_up'] == True
    
    def test_first_pomodoro_achievement(self):
        """Test first Pomodoro achievement is unlocked"""
        manager = GamificationManager()
        result = manager.complete_pomodoro(1500)
        
        assert len(result['new_achievements']) > 0
        achievement_ids = [a['id'] for a in result['new_achievements']]
        assert 'first_pomodoro' in achievement_ids
    
    def test_streak_tracking_first_day(self):
        """Test streak tracking for first day"""
        manager = GamificationManager()
        result = manager.complete_pomodoro(1500)
        
        assert manager.current_streak == 1
        assert result['current_streak'] == 1
    
    def test_xp_progress_calculation(self):
        """Test XP progress calculation"""
        manager = GamificationManager({'xp': 150})
        progress = manager.get_xp_progress()
        
        assert progress['current_level'] == 2
        assert progress['next_level'] == 3
        assert progress['xp_progress'] == 50  # 150 - 100 (level 2 requirement)
        assert progress['xp_needed'] == 150  # 250 - 100
    
    def test_get_stats(self):
        """Test getting statistics"""
        manager = GamificationManager({
            'xp': 200,
            'level': 2,
            'total_sessions': 4,
            'current_streak': 2
        })
        stats = manager.get_stats()
        
        assert stats['xp'] == 200
        assert stats['level'] == 2
        assert stats['total_sessions'] == 4
        assert stats['current_streak'] == 2
        assert 'achievements' in stats
        assert 'available_achievements' in stats
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        manager = GamificationManager()
        manager.complete_pomodoro(1500)
        
        data = manager.to_dict()
        assert isinstance(data, dict)
        assert 'xp' in data
        assert 'level' in data
        assert 'total_sessions' in data
        assert data['xp'] == 50
        assert data['total_sessions'] == 1


class TestGamificationEndpoints:
    """Test gamification API endpoints"""
    
    def test_complete_pomodoro_endpoint(self, client):
        """Test completing a Pomodoro through the API"""
        response = client.post('/gamification/complete', json={
            'focusTime': 1500
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'xp_gained' in data
        assert 'total_xp' in data
        assert 'level' in data
        assert data['xp_gained'] == 50
    
    def test_get_gamification_stats(self, client):
        """Test getting gamification stats"""
        # First complete a Pomodoro
        client.post('/gamification/complete', json={'focusTime': 1500})
        
        # Then get stats
        response = client.get('/gamification/stats')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'stats' in data
        assert 'xp_progress' in data
        assert data['stats']['total_sessions'] == 1
        assert data['stats']['level'] == 1
    
    def test_get_chart_data(self, client):
        """Test getting chart data"""
        response = client.get('/gamification/charts')
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'weekly' in data
        assert 'monthly' in data
        assert isinstance(data['weekly'], list)
        assert isinstance(data['monthly'], list)
    
    def test_multiple_completions(self, client):
        """Test multiple Pomodoro completions"""
        # Complete 3 Pomodoros
        for _ in range(3):
            response = client.post('/gamification/complete', json={'focusTime': 1500})
            assert response.status_code == 200
        
        # Check stats
        response = client.get('/gamification/stats')
        data = response.get_json()
        
        assert data['stats']['total_sessions'] == 3
        assert data['stats']['xp'] == 150
        assert data['stats']['level'] == 2  # Should be level 2 at 150 XP
