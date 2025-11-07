"""Internationalization and Localization System"""
import json
import os
from typing import Dict, Optional


class I18n:
    """Internationalization and localization handler"""
    
    SUPPORTED_LANGUAGES = ["en", "ja"]
    
    def __init__(self, locale_dir: str = "locales", default_language: str = "en"):
        self.locale_dir = locale_dir
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        if not os.path.exists(self.locale_dir):
            os.makedirs(self.locale_dir)
            self._create_default_translations()
        
        for lang in self.SUPPORTED_LANGUAGES:
            translation_file = os.path.join(self.locale_dir, f"{lang}.json")
            if os.path.exists(translation_file):
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                except json.JSONDecodeError:
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}
    
    def _create_default_translations(self):
        """Create default translation files"""
        # English translations
        en_translations = {
            "game.title": "Kitchen Game Manager",
            "game.start": "Game started...",
            "game.stop": "Game stopped",
            "recipe.new": "A new recipe has been generated!",
            "recipe.success": "Recipe delivery successful!",
            "recipe.failed": "Recipe delivery failed...",
            "recipe.waiting": "Number of waiting recipes",
            "recipe.successful": "Number of successful recipes",
            "recipe.delivering": "Delivering sandwich...",
            "user.login": "Logged in as",
            "user.logout": "Logged out",
            "user.register": "User registered successfully",
            "user.register_failed": "User already exists",
            "user.login_failed": "Login failed",
            "user.progress": "User Progress",
            "user.username": "Username",
            "user.recipes_completed": "Recipes Completed",
            "user.recipes_failed": "Recipes Failed",
            "user.time_played": "Time Played",
            "user.games_played": "Games Played",
            "dashboard.title": "Dashboard",
            "dashboard.game_stats": "Game Statistics",
            "dashboard.recipe_stats": "Recipe Statistics",
            "dashboard.total_games": "Total Games Played",
            "dashboard.total_time": "Total Time Played",
            "dashboard.avg_duration": "Average Game Duration",
            "dashboard.success_rate": "Success Rate",
            "dashboard.avg_recipes": "Average Recipes per Game",
            "leaderboard.title": "Leaderboard - Top Players",
            "leaderboard.rank": "Rank",
            "leaderboard.username": "Username",
            "leaderboard.recipes": "Recipes",
            "leaderboard.success": "Success %",
            "leaderboard.no_data": "No data available yet",
            "language.changed": "Language changed to",
            "seconds": "seconds"
        }
        
        # Japanese translations
        ja_translations = {
            "game.title": "キッチンゲームマネージャー",
            "game.start": "ゲーム開始...",
            "game.stop": "ゲーム停止",
            "recipe.new": "新しいレシピが生成されました！",
            "recipe.success": "レシピ配達成功！",
            "recipe.failed": "レシピ配達失敗...",
            "recipe.waiting": "待機中のレシピ数",
            "recipe.successful": "成功したレシピ数",
            "recipe.delivering": "サンドイッチを配達中...",
            "user.login": "ログイン:",
            "user.logout": "ログアウトしました",
            "user.register": "ユーザー登録成功",
            "user.register_failed": "ユーザーは既に存在します",
            "user.login_failed": "ログイン失敗",
            "user.progress": "ユーザー進捗",
            "user.username": "ユーザー名",
            "user.recipes_completed": "完了レシピ数",
            "user.recipes_failed": "失敗レシピ数",
            "user.time_played": "プレイ時間",
            "user.games_played": "プレイしたゲーム数",
            "dashboard.title": "ダッシュボード",
            "dashboard.game_stats": "ゲーム統計",
            "dashboard.recipe_stats": "レシピ統計",
            "dashboard.total_games": "総プレイゲーム数",
            "dashboard.total_time": "総プレイ時間",
            "dashboard.avg_duration": "平均ゲーム時間",
            "dashboard.success_rate": "成功率",
            "dashboard.avg_recipes": "ゲームあたりの平均レシピ数",
            "leaderboard.title": "リーダーボード - トッププレイヤー",
            "leaderboard.rank": "順位",
            "leaderboard.username": "ユーザー名",
            "leaderboard.recipes": "レシピ",
            "leaderboard.success": "成功率 %",
            "leaderboard.no_data": "まだデータがありません",
            "language.changed": "言語を変更しました:",
            "seconds": "秒"
        }
        
        # Save translations
        for lang, translations in [("en", en_translations), ("ja", ja_translations)]:
            translation_file = os.path.join(self.locale_dir, f"{lang}.json")
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
    
    def set_language(self, language: str) -> bool:
        """Set current language"""
        if language in self.SUPPORTED_LANGUAGES:
            self.current_language = language
            return True
        return False
    
    def get_language(self) -> str:
        """Get current language"""
        return self.current_language
    
    def translate(self, key: str, default: Optional[str] = None) -> str:
        """Translate a key to current language"""
        if self.current_language in self.translations:
            translation = self.translations[self.current_language].get(key)
            if translation:
                return translation
        
        # Fallback to English
        if "en" in self.translations:
            translation = self.translations["en"].get(key)
            if translation:
                return translation
        
        # Return default or key
        return default if default else key
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """Shorthand for translate"""
        return self.translate(key, default)


# Global i18n instance
_i18n_instance: Optional[I18n] = None


def get_i18n() -> I18n:
    """Get global i18n instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


def t(key: str, default: Optional[str] = None) -> str:
    """Global translate function"""
    return get_i18n().translate(key, default)


# Example usage
if __name__ == "__main__":
    i18n = I18n()
    
    # Test English translations
    print("=== English ===")
    print(i18n.t("game.title"))
    print(i18n.t("recipe.success"))
    print(i18n.t("user.login") + " player1")
    
    # Switch to Japanese
    print("\n=== Japanese ===")
    i18n.set_language("ja")
    print(i18n.t("game.title"))
    print(i18n.t("recipe.success"))
    print(i18n.t("user.login") + " player1")
    
    # Test missing key
    print("\n=== Missing Key ===")
    print(i18n.t("missing.key", "Default value"))
    
    # List supported languages
    print("\n=== Supported Languages ===")
    print(f"Supported: {', '.join(I18n.SUPPORTED_LANGUAGES)}")
    print(f"Current: {i18n.get_language()}")
