"""
Gamification module for Pomodoro Timer
Handles XP, levels, achievements, streaks, and statistics
"""
from datetime import datetime, timedelta
import json


class GamificationManager:
    """Manages gamification features including XP, levels, achievements, and streaks"""
    
    # XP requirements for each level (progressive scaling)
    LEVEL_XP_REQUIREMENTS = {
        1: 0,
        2: 100,
        3: 250,
        4: 500,
        5: 1000,
        6: 2000,
        7: 3500,
        8: 5500,
        9: 8000,
        10: 11000,
    }
    
    # XP awarded per completed Pomodoro
    XP_PER_POMODORO = 50
    
    # Achievement definitions
    ACHIEVEMENTS = {
        'first_pomodoro': {
            'name': 'First Steps',
            'description': 'Complete your first Pomodoro',
            'condition': lambda stats: stats.get('total_sessions', 0) >= 1
        },
        'streak_3': {
            'name': '3 Day Streak',
            'description': 'Complete Pomodoros for 3 consecutive days',
            'condition': lambda stats: stats.get('current_streak', 0) >= 3
        },
        'streak_7': {
            'name': 'Week Warrior',
            'description': 'Complete Pomodoros for 7 consecutive days',
            'condition': lambda stats: stats.get('current_streak', 0) >= 7
        },
        'weekly_10': {
            'name': 'Productive Week',
            'description': 'Complete 10 Pomodoros in a week',
            'condition': lambda stats: stats.get('this_week_sessions', 0) >= 10
        },
        'weekly_25': {
            'name': 'Power Week',
            'description': 'Complete 25 Pomodoros in a week',
            'condition': lambda stats: stats.get('this_week_sessions', 0) >= 25
        },
        'total_50': {
            'name': 'Century Club',
            'description': 'Complete 50 total Pomodoros',
            'condition': lambda stats: stats.get('total_sessions', 0) >= 50
        },
        'total_100': {
            'name': 'Centurion',
            'description': 'Complete 100 total Pomodoros',
            'condition': lambda stats: stats.get('total_sessions', 0) >= 100
        },
    }
    
    def __init__(self, user_data=None):
        """Initialize with user data"""
        if user_data is None:
            user_data = {}
        
        self.xp = user_data.get('xp', 0)
        self.level = user_data.get('level', 1)
        self.total_sessions = user_data.get('total_sessions', 0)
        self.total_focus_time = user_data.get('total_focus_time', 0)
        self.unlocked_achievements = set(user_data.get('unlocked_achievements', []))
        self.current_streak = user_data.get('current_streak', 0)
        self.last_completion_date = user_data.get('last_completion_date', None)
        self.daily_stats = user_data.get('daily_stats', {})  # {date: sessions_count}
        self.weekly_stats = user_data.get('weekly_stats', {})  # {week: sessions_count}
        self.monthly_stats = user_data.get('monthly_stats', {})  # {month: sessions_count}
        
        # Calculate level based on XP if not explicitly set
        if 'level' not in user_data and self.xp > 0:
            self.level = self._calculate_level()
    
    def complete_pomodoro(self, focus_time_seconds=1500):
        """
        Process a completed Pomodoro session
        Awards XP, updates stats, checks for level ups and achievements
        """
        # Award XP
        self.xp += self.XP_PER_POMODORO
        
        # Update session counts
        self.total_sessions += 1
        self.total_focus_time += focus_time_seconds
        
        # Update daily stats and streak
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_stats[today] = self.daily_stats.get(today, 0) + 1
        self._update_streak(today)
        
        # Update weekly and monthly stats
        week_key = datetime.now().strftime('%Y-W%U')
        month_key = datetime.now().strftime('%Y-%m')
        self.weekly_stats[week_key] = self.weekly_stats.get(week_key, 0) + 1
        self.monthly_stats[month_key] = self.monthly_stats.get(month_key, 0) + 1
        
        # Check for level up
        new_level = self._calculate_level()
        leveled_up = new_level > self.level
        self.level = new_level
        
        # Check for new achievements
        new_achievements = self._check_achievements()
        
        return {
            'xp_gained': self.XP_PER_POMODORO,
            'total_xp': self.xp,
            'level': self.level,
            'leveled_up': leveled_up,
            'new_achievements': new_achievements,
            'current_streak': self.current_streak
        }
    
    def _calculate_level(self):
        """Calculate level based on current XP"""
        level = 1
        for lvl in sorted(self.LEVEL_XP_REQUIREMENTS.keys(), reverse=True):
            if self.xp >= self.LEVEL_XP_REQUIREMENTS[lvl]:
                level = lvl
                break
        return level
    
    def _update_streak(self, today):
        """Update the consecutive day streak"""
        if self.last_completion_date is None:
            # First ever completion
            self.current_streak = 1
        else:
            last_date = datetime.strptime(self.last_completion_date, '%Y-%m-%d')
            today_date = datetime.strptime(today, '%Y-%m-%d')
            days_diff = (today_date - last_date).days
            
            if days_diff == 0:
                # Same day, streak unchanged
                pass
            elif days_diff == 1:
                # Consecutive day
                self.current_streak += 1
            else:
                # Streak broken
                self.current_streak = 1
        
        self.last_completion_date = today
    
    def _check_achievements(self):
        """Check for newly unlocked achievements"""
        new_achievements = []
        
        stats = self.get_stats()
        
        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            if achievement_id not in self.unlocked_achievements:
                if achievement['condition'](stats):
                    self.unlocked_achievements.add(achievement_id)
                    new_achievements.append({
                        'id': achievement_id,
                        'name': achievement['name'],
                        'description': achievement['description']
                    })
        
        return new_achievements
    
    def get_stats(self):
        """Get current statistics"""
        # Calculate this week's sessions
        current_week = datetime.now().strftime('%Y-W%U')
        this_week_sessions = self.weekly_stats.get(current_week, 0)
        
        # Calculate this month's sessions
        current_month = datetime.now().strftime('%Y-%m')
        this_month_sessions = self.monthly_stats.get(current_month, 0)
        
        # Calculate today's sessions
        today = datetime.now().strftime('%Y-%m-%d')
        today_sessions = self.daily_stats.get(today, 0)
        
        return {
            'xp': self.xp,
            'level': self.level,
            'total_sessions': self.total_sessions,
            'total_focus_time': self.total_focus_time,
            'current_streak': self.current_streak,
            'this_week_sessions': this_week_sessions,
            'this_month_sessions': this_month_sessions,
            'today_sessions': today_sessions,
            'achievements': [
                {
                    'id': aid,
                    'name': self.ACHIEVEMENTS[aid]['name'],
                    'description': self.ACHIEVEMENTS[aid]['description'],
                    'unlocked': True
                }
                for aid in self.unlocked_achievements
            ],
            'available_achievements': [
                {
                    'id': aid,
                    'name': achievement['name'],
                    'description': achievement['description'],
                    'unlocked': False
                }
                for aid, achievement in self.ACHIEVEMENTS.items()
                if aid not in self.unlocked_achievements
            ]
        }
    
    def get_xp_progress(self):
        """Get XP progress to next level"""
        current_level_xp = self.LEVEL_XP_REQUIREMENTS.get(self.level, 0)
        next_level = self.level + 1
        next_level_xp = self.LEVEL_XP_REQUIREMENTS.get(next_level, current_level_xp)
        
        if next_level > max(self.LEVEL_XP_REQUIREMENTS.keys()):
            # Max level reached
            return {
                'current_level': self.level,
                'next_level': self.level,
                'current_xp': self.xp,
                'xp_for_next_level': self.xp,
                'xp_progress': self.xp - current_level_xp,
                'xp_needed': 0,
                'progress_percentage': 100,
                'max_level': True
            }
        
        xp_progress = self.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress_percentage = (xp_progress / xp_needed * 100) if xp_needed > 0 else 100
        
        return {
            'current_level': self.level,
            'next_level': next_level,
            'current_xp': self.xp,
            'xp_for_next_level': next_level_xp,
            'xp_progress': xp_progress,
            'xp_needed': xp_needed,
            'progress_percentage': progress_percentage,
            'max_level': False
        }
    
    def get_weekly_chart_data(self, weeks=4):
        """Get weekly session data for chart"""
        data = []
        current_date = datetime.now()
        
        for i in range(weeks):
            week_date = current_date - timedelta(weeks=i)
            week_key = week_date.strftime('%Y-W%U')
            week_label = week_date.strftime('Week %U')
            sessions = self.weekly_stats.get(week_key, 0)
            data.insert(0, {
                'label': week_label,
                'value': sessions
            })
        
        return data
    
    def get_monthly_chart_data(self, months=6):
        """Get monthly session data for chart"""
        data = []
        current_date = datetime.now()
        
        for i in range(months):
            # Calculate month by going back i months
            month = current_date.month - i
            year = current_date.year
            while month <= 0:
                month += 12
                year -= 1
            
            month_key = f'{year}-{month:02d}'
            month_date = datetime(year, month, 1)
            month_label = month_date.strftime('%b %Y')
            sessions = self.monthly_stats.get(month_key, 0)
            data.insert(0, {
                'label': month_label,
                'value': sessions
            })
        
        return data
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'xp': self.xp,
            'level': self.level,
            'total_sessions': self.total_sessions,
            'total_focus_time': self.total_focus_time,
            'unlocked_achievements': list(self.unlocked_achievements),
            'current_streak': self.current_streak,
            'last_completion_date': self.last_completion_date,
            'daily_stats': self.daily_stats,
            'weekly_stats': self.weekly_stats,
            'monthly_stats': self.monthly_stats
        }
