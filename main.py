"""Enhanced Kitchen Game with User Auth, Analytics, and i18n"""
import time
from deliverManager import (
    KitchenObjectSO, RecipeSO, RecipeListSO,
    PlateKitchenObject, KitchenGameManager, DeliveryManager
)
from user_auth import UserAuth
from analytics import Analytics
from i18n import I18n


def main():
    """Main application with enhanced features"""
    
    # Initialize systems
    auth = UserAuth()
    analytics = Analytics()
    i18n = I18n()
    
    print("=" * 60)
    print(f"{i18n.t('game.title'):^60}")
    print("=" * 60)
    
    # User authentication demo
    print(f"\n{i18n.t('user.register')}...")
    username = "demo_player"
    password = "demo123"
    
    if not auth.register(username, password):
        print(f"  {i18n.t('user.register_failed')}")
    
    print(f"\n{i18n.t('user.login')}...")
    if auth.login(username, password):
        print(f"  ✓ {i18n.t('user.login')}: {username}")
    else:
        print(f"  ✗ {i18n.t('user.login_failed')}")
        return
    
    # Create sample game data
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # Initialize game
    game_manager = KitchenGameManager.get_instance()
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # Start analytics session
    analytics.start_session(username)
    
    # Set up event handlers with i18n
    def on_recipe_spawned(sender, args):
        print(f"  📋 {i18n.t('recipe.new')}")
    
    def on_recipe_success(sender, args):
        print(f"  ✓ {i18n.t('recipe.success')}")
        analytics.record_recipe_completed()
        auth.update_progress(recipes_completed=1)
    
    def on_recipe_failed(sender, args):
        print(f"  ✗ {i18n.t('recipe.failed')}")
        analytics.record_recipe_failed()
        auth.update_progress(recipes_failed=1)
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # Start game
    print(f"\n{i18n.t('game.start')}")
    game_manager.start_game()
    
    # Run game simulation
    start_time = time.time()
    game_duration = 5
    
    while time.time() - start_time < game_duration:
        delivery_manager.update()
        time.sleep(0.1)
    
    # Deliver some recipes
    print(f"\n{i18n.t('recipe.delivering')}")
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    delivery_manager.deliver_recipe(plate)
    
    # Try a failed delivery
    wrong_plate = PlateKitchenObject()
    wrong_plate.add_kitchen_object(bread)
    delivery_manager.deliver_recipe(wrong_plate)
    
    # End game
    game_manager.stop_game()
    elapsed_time = time.time() - start_time
    auth.update_progress(time_played=elapsed_time, game_finished=True)
    analytics.end_session()
    
    print(f"\n{i18n.t('game.stop')}")
    print(f"{i18n.t('recipe.waiting')}: {len(delivery_manager.get_waiting_recipe_so_list())}")
    print(f"{i18n.t('recipe.successful')}: {delivery_manager.get_successful_recipes_amount()}")
    
    # Display user progress
    progress = auth.get_user_progress()
    if progress:
        print(f"\n{i18n.t('user.progress')}:")
        print(f"  {i18n.t('user.username')}: {progress.username}")
        print(f"  {i18n.t('user.recipes_completed')}: {progress.total_recipes_completed}")
        print(f"  {i18n.t('user.recipes_failed')}: {progress.total_recipes_failed}")
        print(f"  {i18n.t('user.time_played')}: {progress.total_time_played:.1f} {i18n.t('seconds')}")
        print(f"  {i18n.t('user.games_played')}: {progress.games_played}")
    
    # Display analytics dashboard
    analytics.display_dashboard(username)
    
    # Display leaderboard
    analytics.display_leaderboard()
    
    # Demonstrate language switching
    print("\n" + "=" * 60)
    print(f"{i18n.t('language.changed')} Japanese")
    print("=" * 60)
    i18n.set_language("ja")
    
    print(f"\n{i18n.t('user.progress')}:")
    print(f"  {i18n.t('user.username')}: {progress.username}")
    print(f"  {i18n.t('user.recipes_completed')}: {progress.total_recipes_completed}")
    print(f"  {i18n.t('user.recipes_failed')}: {progress.total_recipes_failed}")
    
    # Logout
    auth.logout()
    print(f"\n{i18n.t('user.logout')}")


if __name__ == "__main__":
    main()
