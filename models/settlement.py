import pygame
import random
from database.db_handler import DatabaseHandler
from models.item import Item
import logging  # Ensure logging is imported
from handlers.pricing_handler import PricingHandler

class Settlement:
    def __init__(self, x, y, name, settlement_type, id=None):
        self.x = x
        self.y = y
        self.name = name
        self.settlement_type = settlement_type
        self.id = id
        
        # Set size based on settlement type
        if settlement_type == "castle":
            self.size = 25
            self.color = (139, 69, 19)  # Brown
        elif settlement_type == "capital":
            self.size = 20
            self.color = (178, 34, 34)  # Firebrick Red
        elif settlement_type == "town":
            self.size = 15
            self.color = (70, 130, 180)  # Steel Blue
        else:  # village
            self.size = 10
            self.color = (34, 139, 34)  # Forest Green

        self.inventory = {}  # Inventory as {item_id: Item}
        self.gold = 1000  # Starting gold for settlements
        self.load_inventory()

    def load_inventory(self):
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
            PricingHandler.update_settlement_prices(self)

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
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
    def draw(self, screen):
        # Draw settlement as a circle with different colors based on type
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
