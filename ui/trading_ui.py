import pygame

class TradingUI:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.Font(None, 24)
        self.width = screen_width
        self.height = screen_height
        self.current_category = None
        print("Trading UI initialized")

    def handle_click(self, mouse_pos, settlement, merchant):
        # Only log when actual interaction happens
        if self.is_buy_area(mouse_pos):
            clicked_item = self.get_clicked_item(mouse_pos, settlement)
            if clicked_item:
                print(f"Attempting to buy {clicked_item.name}")
                self.buy_item(merchant, settlement, clicked_item)
        elif self.is_sell_area(mouse_pos):
            clicked_item = self.get_clicked_item_from_merchant(mouse_pos, merchant)
            if clicked_item:
                print(f"Attempting to sell {clicked_item.name}")
                self.sell_item(merchant, settlement, clicked_item)

    def draw(self, screen, settlement, merchant):
        # Draw trading interface background
        pygame.draw.rect(screen, (50, 50, 50), (50, 50, self.width - 100, self.height - 100))
        
        # Draw settlement name
        title_font = pygame.font.Font(None, 36)
        title_surface = title_font.render(f"Trading with {settlement.name}", True, (255, 255, 255))
        screen.blit(title_surface, (self.width//2 - title_surface.get_width()//2, 60))

        # Draw settlement inventory (left side)
        y_offset = 100
        pygame.draw.rect(screen, (70, 70, 70), (75, 95, self.width//2 - 100, self.height - 200))
        settlement_items = settlement.get_inventory_items()
        if not settlement_items:
            text_surface = self.font.render("No items available", True, (255, 255, 255))
            screen.blit(text_surface, (100, y_offset))
        else:
            for item in settlement_items:
                if item.quantity > 0:  # Only show items with stock
                    item_text = f"{item.name} - Buy: {item.buy_price}g - Stock: {item.quantity}"
                    text_surface = self.font.render(item_text, True, (255, 255, 255))
                    screen.blit(text_surface, (100, y_offset))
                    y_offset += 30

        # Draw merchant inventory (right side)
        y_offset = 100
        pygame.draw.rect(screen, (70, 70, 70), (self.width//2 + 25, 95, self.width//2 - 100, self.height - 200))
        merchant_items = merchant.get_inventory_items()
        if not merchant_items:
            text_surface = self.font.render("No items in inventory", True, (255, 255, 255))
            screen.blit(text_surface, (self.width//2 + 50, y_offset))
        else:
            for item in merchant_items:
                if item.quantity > 0:  # Only show items merchant has
                    item_text = f"{item.name} - Sell: {item.sell_price}g - Own: {item.quantity}"
                    text_surface = self.font.render(item_text, True, (255, 255, 255))
                    screen.blit(text_surface, (self.width//2 + 50, y_offset))
                    y_offset += 30

        # Draw merchant's gold
        gold_text = self.font.render(f"Your Gold: {merchant.gold}g", True, (255, 215, 0))
        screen.blit(gold_text, (self.width//2 - gold_text.get_width()//2, self.height - 40))

    def get_clicked_item(self, mouse_pos, settlement):
        # Check if click is in settlement inventory area
        x, y = mouse_pos
        if 75 <= x <= self.width//2 - 25 and 95 <= y <= self.height - 105:
            index = (y - 100) // 30
            items = settlement.get_inventory_items()
            if 0 <= index < len(items):
                return items[index]
        return None

    def get_clicked_item_from_merchant(self, mouse_pos, merchant):
        # Check if click is in merchant inventory area
        x, y = mouse_pos
        if self.width//2 + 25 <= x <= self.width - 75 and 95 <= y <= self.height - 105:
            index = (y - 100) // 30
            items = [item for item in merchant.get_inventory_items() if item.quantity > 0]
            if 0 <= index < len(items):
                return items[index]
        return None

    def is_buy_area(self, mouse_pos):
        return 75 <= mouse_pos[0] <= self.width//2 - 25

    def is_sell_area(self, mouse_pos):
        return self.width//2 + 25 <= mouse_pos[0] <= self.width - 75

    def buy_item(self, merchant, settlement, item):
        print(f"Executing buy operation for item ID {item.id}: {item.name}")
        if item.quantity > 0 and merchant.gold >= item.buy_price:
            merchant.add_item(item.id, 1)
            settlement.remove_item(item.id, 1)
            merchant.gold -= item.buy_price
            if hasattr(settlement, 'gold'):
                settlement.gold += item.buy_price
                print(f"Merchant bought {item.name} for {item.buy_price} gold.")
            else:
                print("Settlement does not have a gold attribute.")
        else:
            if item.quantity <= 0:
                print("Cannot buy item: Item out of stock.")
            if merchant.gold < item.buy_price:
                print("Cannot buy item: Not enough gold.")

    def sell_item(self, merchant, settlement, item):
        print(f"Executing sell operation for item ID {item.id}: {item.name}")
        if item.quantity > 0:
            merchant.remove_item(item.id, 1)
            settlement.add_item(item.id, 1)
            merchant.gold += item.sell_price
            if hasattr(settlement, 'gold'):
                settlement.gold -= item.sell_price
                print(f"Merchant sold {item.name} for {item.sell_price} gold.")
            else:
                print("Settlement does not have a gold attribute.")
        else:
            print("Cannot sell item: Merchant does not have this item.")
