import pygame
import math
from models.item import Item

class Merchant:
    def __init__(self, x, y):
        # Assign the merchant's current position
        self.x = x  # Current x position
        self.y = y  # Current y position
        self.target_x = x  # Destination x position
        self.target_y = y  # Destination y position
        self.speed = 2  # Movement speed (pixels per frame)
        self.arrived_at_settlement = True  # Flag to indicate arrival
        self.gold = 100  # Starting gold
        self.cart_capacity = 50  # Maximum cargo capacity
        self.current_load = 0  # Current load
        self.inventory = {}  # Inventory as {item_id: Item}
        self.load_inventory()

    def load_inventory(self):
        # Initialize merchant's inventory
        items = Item.load_all_items()
        for item in items:
            self.inventory[item.id] = Item(
                id=item.id,
                name=item.name,
                buy_price=item.buy_price,
                sell_price=item.sell_price,
                description=item.description,
                category=item.category,
                quantity=0  # Start with zero quantity
            )

    def move(self):
        if self.x == self.target_x and self.y == self.target_y:
            self.arrived_at_settlement = True
            return True
        else:
            self.arrived_at_settlement = False
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.hypot(dx, dy)
            if distance == 0:
                return True
            # Normalize the direction
            dx /= distance
            dy /= distance
            # Update position based on speed
            self.x += dx * self.speed
            self.y += dy * self.speed
            # Check if arrived
            if math.hypot(self.target_x - self.x, self.target_y - self.y) < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.arrived_at_settlement = True
                return True
            return False

    def draw(self, screen):
        # Draw merchant as a blue circle
        pygame.draw.circle(screen, (0, 0, 255), (int(self.x), int(self.y)), 10)

    def add_item(self, item_id, quantity):
        if item_id in self.inventory:
            if self.current_load + quantity <= self.cart_capacity:
                self.inventory[item_id].quantity += quantity
                self.current_load += quantity
            else:
                print("Cannot add item: Cart capacity exceeded.")
        else:
            item = Item.get_item_by_id(item_id)
            if item:
                if self.current_load + quantity <= self.cart_capacity:
                    item.quantity = quantity
                    self.inventory[item_id] = item
                    self.current_load += quantity
                else:
                    print("Cannot add item: Cart capacity exceeded.")

    def remove_item(self, item_id, quantity):
        if item_id in self.inventory:
            if self.inventory[item_id].quantity >= quantity:
                self.inventory[item_id].quantity -= quantity
                self.current_load -= quantity
                if self.inventory[item_id].quantity == 0:
                    del self.inventory[item_id]
            else:
                print("Cannot remove item: Not enough quantity.")
        else:
            print("Cannot remove item: Item not in inventory.")

    def get_inventory_items(self):
        return list(self.inventory.values())
