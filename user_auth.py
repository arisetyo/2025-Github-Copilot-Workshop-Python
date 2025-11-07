"""User Authentication System for Kitchen Game"""
import json
import hashlib
import hmac
import secrets
import os
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserProgress:
    """User progress tracking"""
    username: str
    total_recipes_completed: int = 0
    total_recipes_failed: int = 0
    total_time_played: float = 0.0
    games_played: int = 0
    last_login: str = ""
    created_at: str = ""


class UserAuth:
    """User authentication and progress management"""
    
    def __init__(self, data_file: str = "users_data.json"):
        self.data_file = data_file
        self.current_user: Optional[str] = None
        self.users: Dict[str, Dict] = {}
        self._load_users()
    
    def _load_users(self):
        """Load user data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.users = json.load(f)
            except json.JSONDecodeError:
                self.users = {}
    
    def _save_users(self):
        """Save user data to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password using SHA256 with salt
        
        Note: SHA256 with salt is used for this workshop project to avoid external dependencies.
        For production systems, use dedicated password hashing algorithms like bcrypt, scrypt,
        or Argon2, which are specifically designed to be computationally expensive and resistant
        to brute-force attacks.
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate username and password inputs"""
        if not username or not password:
            return False
        if not username.strip() or not password.strip():
            return False
        if len(username) > 100 or len(password) > 100:
            return False
        return True
    
    def register(self, username: str, password: str) -> bool:
        """Register a new user"""
        if not self._validate_credentials(username, password):
            return False
        
        if username in self.users:
            return False
        
        password_hash, salt = self._hash_password(password)
        now = datetime.now().isoformat()
        self.users[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "progress": asdict(UserProgress(
                username=username,
                created_at=now,
                last_login=now
            ))
        }
        self._save_users()
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user"""
        if not self._validate_credentials(username, password):
            return False
        
        if username not in self.users:
            return False
        
        stored_hash = self.users[username]["password_hash"]
        salt = self.users[username].get("salt", "")
        password_hash, _ = self._hash_password(password, salt)
        
        # Use constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(password_hash, stored_hash):
            return False
        
        self.current_user = username
        self.users[username]["progress"]["last_login"] = datetime.now().isoformat()
        self._save_users()
        return True
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self) -> Optional[str]:
        """Get current logged in user"""
        return self.current_user
    
    def get_user_progress(self, username: Optional[str] = None) -> Optional[UserProgress]:
        """Get user progress"""
        user = username or self.current_user
        if user and user in self.users:
            progress_data = self.users[user]["progress"]
            return UserProgress(**progress_data)
        return None
    
    def update_progress(self, 
                       recipes_completed: int = 0,
                       recipes_failed: int = 0,
                       time_played: float = 0.0,
                       game_finished: bool = False):
        """Update current user's progress"""
        if not self.current_user:
            return
        
        progress = self.users[self.current_user]["progress"]
        progress["total_recipes_completed"] += recipes_completed
        progress["total_recipes_failed"] += recipes_failed
        progress["total_time_played"] += time_played
        
        if game_finished:
            progress["games_played"] += 1
        
        self._save_users()
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated"""
        return self.current_user is not None


# Example usage
if __name__ == "__main__":
    auth = UserAuth()
    
    # Register a new user
    print("Registering user...")
    if auth.register("player1", "password123"):
        print("✓ User registered successfully")
    else:
        print("✗ User already exists")
    
    # Login
    print("\nLogging in...")
    if auth.login("player1", "password123"):
        print(f"✓ Logged in as {auth.get_current_user()}")
    else:
        print("✗ Login failed")
    
    # Update progress
    print("\nUpdating progress...")
    auth.update_progress(recipes_completed=5, recipes_failed=2, time_played=300.5)
    
    # Get progress
    progress = auth.get_user_progress()
    if progress:
        print(f"\nUser Progress:")
        print(f"  Username: {progress.username}")
        print(f"  Recipes Completed: {progress.total_recipes_completed}")
        print(f"  Recipes Failed: {progress.total_recipes_failed}")
        print(f"  Time Played: {progress.total_time_played:.1f}s")
        print(f"  Games Played: {progress.games_played}")
    
    # Logout
    print("\nLogging out...")
    auth.logout()
    print(f"✓ Logged out")
