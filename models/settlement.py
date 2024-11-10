import pygame
import random
from database.db_handler import DatabaseHandler
from models.item import Item

class Settlement:
    def __init__(self, x, y, name, settlement_type, id=None):
        self.id = id  # Assign the settlement ID
        self.x = x
        self.y = y
        self.name = name
        self.settlement_type = settlement_type
        self.size = 20  # Example size for settlement radius
        self.inventory = {}  # Inventory as {item_id: Item}
        self.load_inventory()

    def load_inventory(self):
        db = DatabaseHandler()
        if self.id is not None:
            items_data = db.get_settlement_items(self.id)
            for data in items_data:
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

    def update_prices(self, game_tick):
        # Update item prices based on some logic or randomness
        for item in self.inventory.values():
            price_fluctuation = random.uniform(0.9, 1.1)
            item.buy_price = max(1, int(item.buy_price * price_fluctuation))
            item.sell_price = max(1, int(item.sell_price * price_fluctuation))

    def add_item(self, item_id, quantity):
        if item_id in self.inventory:
            self.inventory[item_id].quantity += quantity
        else:
            item = Item.get_item_by_id(item_id)
            if item:
                item.quantity = quantity
                self.inventory[item_id] = item

    def remove_item(self, item_id, quantity):
        if item_id in self.inventory:
            self.inventory[item_id].quantity -= quantity
            if self.inventory[item_id].quantity <= 0:
                del self.inventory[item_id]

    def get_inventory_items(self):
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
