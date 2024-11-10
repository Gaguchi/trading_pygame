import pygame
import random
from database.db_handler import DatabaseHandler
from models.item import Item
import logging  # Ensure logging is imported

class Settlement:
    def __init__(self, x, y, name, settlement_type, id=None):
        print(f"Initializing Settlement: {name}, Type: {settlement_type}, Location: ({x}, {y}), ID: {id}")
        self.id = id  # Assign the settlement ID
        self.x = x
        self.y = y
        self.name = name
        self.settlement_type = settlement_type
        self.size = 20  # Example size for settlement radius
        self.inventory = {}  # Inventory as {item_id: Item}
        self.gold = 1000  # Starting gold for settlements
        self.load_inventory()

    def load_inventory(self):
        print(f"\nLoading inventory for Settlement ID {self.id}...")
        db = DatabaseHandler()
        if self.id is not None:
            items_data = db.get_settlement_items(self.id)
            print(f"Raw items data: {[dict(item) for item in items_data]}")  # Debug raw data
            for data in items_data:
                try:
                    item = Item(
                        id=data['id'],
                        name=data['name'],
                        buy_price=data['buy_price'],
                        sell_price=data['sell_price'],
                        description=data['description'],
                        category=data['category'],
                        quantity=data['quantity']
                    )
                    self.inventory[item.id] = item
                    print(f"Successfully added to inventory: {item.name} x{item.quantity}")
                except Exception as e:
                    print(f"Error loading item: {e}")
                    print(f"Data: {dict(data)}")
        else:
            print("Settlement ID is None; skipping inventory load.")
        
        print(f"Total items in settlement inventory: {len(self.inventory)}")

    def update_prices(self, game_tick):
        # Only log price updates occasionally
        if game_tick % 100 == 0:  # Match the update frequency in game.py
            print(f"Updating prices for {self.name} (ID: {self.id})")
        for item in self.inventory.values():
            price_fluctuation = random.uniform(0.9, 1.1)
            item.buy_price = max(1, int(item.buy_price * price_fluctuation))
            item.sell_price = max(1, int(item.sell_price * price_fluctuation))

    def add_item(self, item_id, quantity):
        print(f"Adding item ID {item_id} x{quantity} to Settlement ID {self.id}")
        if item_id in self.inventory:
            self.inventory[item_id].quantity += quantity
            self.gold += quantity * self.inventory[item_id].buy_price  # Update settlement's gold
            print(f"Updated {self.inventory[item_id].name} quantity to {self.inventory[item_id].quantity}")
        else:
            item = Item.get_item_by_id(item_id)
            if item:
                item.quantity = quantity
                self.inventory[item_id] = item
                self.gold += quantity * item.buy_price  # Update settlement's gold
                print(f"Added new item to inventory: {item.name} x{item.quantity}")

    def remove_item(self, item_id, quantity):
        print(f"Removing item ID {item_id} x{quantity} from Settlement ID {self.id}")
        if item_id in self.inventory:
            self.inventory[item_id].quantity -= quantity
            self.gold -= quantity * self.inventory[item_id].sell_price  # Update settlement's gold
            print(f"Updated {self.inventory[item_id].name} quantity to {self.inventory[item_id].quantity}")
            if self.inventory[item_id].quantity <= 0:
                print(f"Quantity for {self.inventory[item_id].name} is zero or less. Removing from inventory.")
                del self.inventory[item_id]
        else:
            print("Attempted to remove an item that doesn't exist in inventory.")

        return list(self.inventory.values())

    def get_inventory_items(self):
        logging.debug(f"Retrieving inventory items for Settlement ID {self.id}")
        return list(self.inventory.values())

    def draw(self, screen):
        # Draw settlement as a circle with different colors based on type
        if self.settlement_type == "castle":
            color = (128, 128, 128)  # Grey for castle
        elif self.settlement_type == "town":
            color = (0, 0, 255)  # Blue for town
        else:
            color = (0, 255, 0)  # Green for village
        pygame.draw.circle(screen, color, (self.x, self.y), self.size)
