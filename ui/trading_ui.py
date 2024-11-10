import pygame

class TradingUI:
    # ...existing code...
    def __init__(self, screen_width, screen_height):
        # ...existing code...
        self.font = pygame.font.Font(None, 24)

    def handle_click(self, mouse_pos, settlement, merchant):
        # Handle clicks for buying/selling items
        # ...existing code...
        clicked_item = self.get_clicked_item(mouse_pos, settlement)
        if clicked_item:
            if self.is_buy_area(mouse_pos):
                self.buy_item(merchant, settlement, clicked_item)
            elif self.is_sell_area(mouse_pos):
                self.sell_item(merchant, settlement, clicked_item)

    def draw(self, screen, settlement, merchant):
        # Draw the trading UI
        # ...existing code...
        self.draw_inventory(screen, settlement, merchant)

    def draw_inventory(self, screen, settlement, merchant):
        # Display items and quantities
        y_offset = 100
        for item in settlement.get_inventory_items():
            item_text = f"{item.name} - Price: {item.buy_price} - Quantity: {item.quantity}"
            text_surface = self.font.render(item_text, True, (255, 255, 255))
            screen.blit(text_surface, (50, y_offset))
            y_offset += 30
        # Display merchant's inventory
        y_offset = 100
        for item in merchant.get_inventory_items():
            item_text = f"{item.name} - Quantity: {item.quantity}"
            text_surface = self.font.render(item_text, True, (255, 255, 255))
            screen.blit(text_surface, (400, y_offset))
            y_offset += 30

    def buy_item(self, merchant, settlement, item):
        if item.quantity > 0 and merchant.gold >= item.buy_price:
            merchant.add_item(item.id, 1)
            settlement.remove_item(item.id, 1)
            merchant.gold -= item.buy_price
            # Assuming settlements have gold, ensure Settlement class has a gold attribute
            if hasattr(settlement, 'gold'):
                settlement.gold += item.buy_price

    def sell_item(self, merchant, settlement, item):
        if item.quantity > 0:
            merchant.remove_item(item.id, 1)
            settlement.add_item(item.id, 1)
            merchant.gold += item.sell_price
            if hasattr(settlement, 'gold'):
                settlement.gold -= item.sell_price

    def get_clicked_item(self, mouse_pos, settlement):
        # Determine which item was clicked based on mouse position
        # ...implement logic...
        pass

    def is_buy_area(self, mouse_pos):
        # Check if the click was in the buying area
        # ...implement logic...
        pass

    def is_sell_area(self, mouse_pos):
        # Check if the click was in the selling area
        # ...implement logic...
        pass
