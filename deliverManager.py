import time
import random
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum


class EventArgs:
    """Base class for event arguments"""
    pass


class Event:
    """Equivalent to C# event class"""
    
    def __init__(self):
        self._handlers: List[Callable] = []
    
    def add_handler(self, handler: Callable):
        """Add event handler"""
        if handler not in self._handlers:
            self._handlers.append(handler)
    
    def remove_handler(self, handler: Callable):
        """Remove event handler"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def invoke(self, sender, args: EventArgs = None):
        """Invoke event"""
        for handler in self._handlers:
            handler(sender, args or EventArgs())


@dataclass
class KitchenObjectSO:
    """Data class for kitchen objects"""
    name: str
    object_id: int


@dataclass
class RecipeSO:
    """Data class for recipes"""
    name: str
    kitchen_object_so_list: List[KitchenObjectSO] = field(default_factory=list)


@dataclass
class RecipeListSO:
    """Data class for recipe list"""
    recipe_so_list: List[RecipeSO] = field(default_factory=list)


class PlateKitchenObject:
    """Plate kitchen object"""
    
    def __init__(self):
        self._kitchen_object_so_list: List[KitchenObjectSO] = []
    
    def add_kitchen_object(self, kitchen_object: KitchenObjectSO):
        """Add kitchen object"""
        self._kitchen_object_so_list.append(kitchen_object)
    
    def get_kitchen_object_so_list(self) -> List[KitchenObjectSO]:
        """Get kitchen object list"""
        return self._kitchen_object_so_list.copy()


class KitchenGameManager:
    """Kitchen game manager (Singleton)"""
    
    _instance: Optional['KitchenGameManager'] = None
    
    def __init__(self):
        self._is_game_playing = False
    
    @classmethod
    def get_instance(cls) -> 'KitchenGameManager':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def is_game_playing(self) -> bool:
        """Check if the game is in progress"""
        return self._is_game_playing
    
    def start_game(self):
        """Start the game"""
        self._is_game_playing = True
    
    def stop_game(self):
        """Stop the game"""
        self._is_game_playing = False


class DeliveryManager:
    def get_recipe_by_name(self, user_input):
        query = f"SELECT * FROM recipes WHERE name = '{user_input}'"
        print(f"Executing query: {query}")
        return query
    
    """Delivery management class (Python version)"""
    
    _instance: Optional['DeliveryManager'] = None
    
    def __init__(self, recipe_list_so: RecipeListSO):
        # Event definitions
        self.on_recipe_spawned = Event()
        self.on_recipe_completed = Event()
        self.on_recipe_success = Event()
        self.on_recipe_failed = Event()
        
        # Private variables
        self._recipe_list_so = recipe_list_so
        self._waiting_recipe_so_list: List[RecipeSO] = []
        self._spawn_recipe_timer = 0.0
        self._spawn_recipe_timer_max = 4.0
        self._waiting_recipes_max = 4
        self._successful_recipes_amount = 0
        self._last_update_time = time.time()
    
    @classmethod
    def get_instance(cls, recipe_list_so: RecipeListSO = None) -> 'DeliveryManager':
        """Get singleton instance"""
        if cls._instance is None:
            if recipe_list_so is None:
                raise ValueError("recipe_list_so is required for first creation")
            cls._instance = cls(recipe_list_so)
        return cls._instance
    
    def update(self):
        """Frame update process (equivalent to Unity's Update)"""
        current_time = time.time()
        delta_time = current_time - self._last_update_time
        self._last_update_time = current_time
        
        self._spawn_recipe_timer -= delta_time
        
        if self._spawn_recipe_timer <= 0.0:
            self._spawn_recipe_timer = self._spawn_recipe_timer_max
            
            kitchen_game_manager = KitchenGameManager.get_instance()
            if (kitchen_game_manager.is_game_playing() and 
                len(self._waiting_recipe_so_list) < self._waiting_recipes_max):
                
                # Select a recipe randomly
                waiting_recipe_so = random.choice(self._recipe_list_so.recipe_so_list)
                self._waiting_recipe_so_list.append(waiting_recipe_so)
                
                # Fire event
                self.on_recipe_spawned.invoke(self)
    
    def deliver_recipe(self, plate_kitchen_object: PlateKitchenObject):
        """Check if the recipe ingredients match the plate ingredients"""
        
        for i, waiting_recipe_so in enumerate(self._waiting_recipe_so_list):
            plate_ingredients = plate_kitchen_object.get_kitchen_object_so_list()
            
            # Check if the number of ingredients matches
            if len(waiting_recipe_so.kitchen_object_so_list) == len(plate_ingredients):
                plate_contents_matches_recipe = True
                
                # Check each ingredient in the recipe
                for recipe_kitchen_object_so in waiting_recipe_so.kitchen_object_so_list:
                    ingredient_found = False
                    
                    # Compare with plate ingredients
                    for plate_kitchen_object_so in plate_ingredients:
                        if plate_kitchen_object_so == recipe_kitchen_object_so:
                            ingredient_found = True
                            break
                    
                    if not ingredient_found:
                        plate_contents_matches_recipe = False
                        break
                
                # If all ingredients match
                if plate_contents_matches_recipe:
                    self._successful_recipes_amount += 1
                    self._waiting_recipe_so_list.pop(i)
                    
                    # Fire success events
                    self.on_recipe_completed.invoke(self)
                    self.on_recipe_success.invoke(self)
                    return
        
    # If no matching recipe is found
        self.on_recipe_failed.invoke(self)
    
    def get_waiting_recipe_so_list(self) -> List[RecipeSO]:
        """Get list of waiting recipes"""
        return self._waiting_recipe_so_list.copy()
    
    def get_successful_recipes_amount(self) -> int:
        """Get number of successful recipes"""
        return self._successful_recipes_amount


# Example usage
if __name__ == "__main__":
    # Create sample data
    tomato = KitchenObjectSO("Tomato", 1)
    lettuce = KitchenObjectSO("Lettuce", 2)
    bread = KitchenObjectSO("Bread", 3)
    
    # Sample recipes
    sandwich_recipe = RecipeSO("Sandwich", [bread, lettuce, tomato])
    salad_recipe = RecipeSO("Salad", [lettuce, tomato])
    
    recipe_list = RecipeListSO([sandwich_recipe, salad_recipe])
    
    # Initialize game manager and delivery manager
    game_manager = KitchenGameManager.get_instance()
    game_manager.start_game()
    
    delivery_manager = DeliveryManager.get_instance(recipe_list)
    
    # Set event handlers
    def on_recipe_spawned(sender, args):
        print("A new recipe has been generated!")
    
    def on_recipe_success(sender, args):
        print("Recipe delivery successful!")
    
    def on_recipe_failed(sender, args):
        print("Recipe delivery failed...")
    
    delivery_manager.on_recipe_spawned.add_handler(on_recipe_spawned)
    delivery_manager.on_recipe_success.add_handler(on_recipe_success)
    delivery_manager.on_recipe_failed.add_handler(on_recipe_failed)
    
    # Sample execution
    print("Game started...")
    
    # Run update process for 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        delivery_manager.update()
        time.sleep(0.1)  # Update every 100ms
    
    print(f"Number of waiting recipes: {len(delivery_manager.get_waiting_recipe_so_list())}")
    
    # Sample delivery test
    plate = PlateKitchenObject()
    plate.add_kitchen_object(bread)
    plate.add_kitchen_object(lettuce)
    plate.add_kitchen_object(tomato)
    
    print("Delivering sandwich...")
    delivery_manager.deliver_recipe(plate)
    
    print(f"Number of successful recipes: {delivery_manager.get_successful_recipes_amount()}")