"""
Test script to verify all optional enhancements
"""
import sys
import os

# Ensure we can import the modules
sys.path.insert(0, os.path.dirname(__file__))


def test_user_auth():
    """Test user authentication system"""
    print("\n" + "="*60)
    print("Testing User Authentication System")
    print("="*60)
    
    from user_auth import UserAuth
    
    auth = UserAuth("test_users.json")
    
    # Test registration
    assert auth.register("test_user", "password123"), "Registration should succeed"
    assert not auth.register("test_user", "password123"), "Duplicate registration should fail"
    
    # Test login
    assert auth.login("test_user", "password123"), "Login with correct password should succeed"
    assert not auth.login("test_user", "wrong_password"), "Login with wrong password should fail"
    assert not auth.login("nonexistent", "password"), "Login with nonexistent user should fail"
    
    # Test progress tracking
    auth.login("test_user", "password123")
    auth.update_progress(recipes_completed=5, recipes_failed=2, time_played=100.0, game_finished=True)
    progress = auth.get_user_progress()
    assert progress.total_recipes_completed == 5, "Progress should track completed recipes"
    assert progress.total_recipes_failed == 2, "Progress should track failed recipes"
    assert progress.games_played == 1, "Progress should track games played"
    
    # Cleanup
    if os.path.exists("test_users.json"):
        os.remove("test_users.json")
    
    print("✓ All user authentication tests passed!")
    return True


def test_analytics():
    """Test analytics system"""
    print("\n" + "="*60)
    print("Testing Analytics System")
    print("="*60)
    
    from analytics import Analytics
    
    analytics = Analytics("test_analytics.json")
    
    # Test session tracking
    analytics.start_session("test_user")
    assert analytics.current_session is not None, "Session should start"
    
    analytics.record_recipe_completed()
    analytics.record_recipe_completed()
    analytics.record_recipe_failed()
    
    assert analytics.current_session.recipes_completed == 2, "Should track completed recipes"
    assert analytics.current_session.recipes_failed == 1, "Should track failed recipes"
    
    analytics.end_session()
    assert analytics.current_session is None, "Session should end"
    
    # Test analytics data
    data = analytics.get_analytics("test_user")
    assert data.total_games == 1, "Should track total games"
    assert data.total_recipes_completed == 2, "Should track total completed"
    assert data.total_recipes_failed == 1, "Should track total failed"
    assert abs(data.success_rate - 66.67) < 0.1, "Should calculate success rate"
    
    # Cleanup
    if os.path.exists("test_analytics.json"):
        os.remove("test_analytics.json")
    
    print("✓ All analytics tests passed!")
    return True


def test_i18n():
    """Test internationalization system"""
    print("\n" + "="*60)
    print("Testing Internationalization System")
    print("="*60)
    
    from i18n import I18n
    
    i18n = I18n()
    
    # Test English translations
    assert i18n.get_language() == "en", "Default language should be English"
    assert i18n.t("game.title") == "Kitchen Game Manager", "Should translate English"
    
    # Test language switching
    assert i18n.set_language("ja"), "Should switch to Japanese"
    assert i18n.get_language() == "ja", "Language should be Japanese"
    assert i18n.t("game.title") == "キッチンゲームマネージャー", "Should translate Japanese"
    
    # Test fallback
    i18n.set_language("en")
    assert i18n.t("nonexistent.key", "default") == "default", "Should use default for missing keys"
    
    # Test invalid language
    assert not i18n.set_language("invalid"), "Should reject invalid language"
    
    print("✓ All i18n tests passed!")
    return True


def test_integration():
    """Test integration of all systems"""
    print("\n" + "="*60)
    print("Testing System Integration")
    print("="*60)
    
    from user_auth import UserAuth
    from analytics import Analytics
    from i18n import I18n
    
    # Initialize all systems
    auth = UserAuth("test_integration_users.json")
    analytics = Analytics("test_integration_analytics.json")
    i18n = I18n()
    
    # Create user
    auth.register("integration_user", "password")
    auth.login("integration_user", "password")
    
    # Start session
    analytics.start_session("integration_user")
    
    # Simulate gameplay with i18n
    print(f"\n  {i18n.t('game.start')}")
    
    for _ in range(3):
        analytics.record_recipe_completed()
        auth.update_progress(recipes_completed=1)
    
    for _ in range(1):
        analytics.record_recipe_failed()
        auth.update_progress(recipes_failed=1)
    
    # End session
    auth.update_progress(time_played=120.0, game_finished=True)
    analytics.end_session()
    
    # Verify integration
    progress = auth.get_user_progress()
    data = analytics.get_analytics("integration_user")
    
    assert progress.total_recipes_completed == 3, "Auth should track recipes"
    assert data.total_recipes_completed == 3, "Analytics should track recipes"
    assert progress.games_played == 1, "Should track games"
    assert data.total_games == 1, "Should track sessions"
    
    # Test with Japanese
    i18n.set_language("ja")
    print(f"  {i18n.t('recipe.success')}")
    
    # Cleanup
    if os.path.exists("test_integration_users.json"):
        os.remove("test_integration_users.json")
    if os.path.exists("test_integration_analytics.json"):
        os.remove("test_integration_analytics.json")
    
    print("✓ All integration tests passed!")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING OPTIONAL ENHANCEMENTS TEST SUITE")
    print("="*60)
    
    tests = [
        ("User Authentication", test_user_auth),
        ("Analytics", test_analytics),
        ("Internationalization", test_i18n),
        ("Integration", test_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} test failed: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
