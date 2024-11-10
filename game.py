import pygame
import random
import math
from enum import Enum
from models.item import Item
from models.settlement import Settlement
from models.merchant import Merchant
from ui.trading_ui import TradingUI
from database.db_handler import DatabaseHandler  # Ensure DatabaseHandler is imported

class GameState(Enum):
    WORLD_MAP = "world_map"
    TRADING = "trading"

class Game:
    def __init__(self):
        print("Starting Game Initialization...")
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Medieval Merchant")
        self.clock = pygame.time.Clock()
        self.state = GameState.WORLD_MAP
        print(f"Game state set to {self.state}.")
        
        self.db = DatabaseHandler()  # Initialize DatabaseHandler
        self.merchant = Merchant(self.width // 2, self.height // 2)
        self.settlements = self.generate_settlements()
        self.trading_ui = TradingUI(self.width, self.height)
        self.current_settlement = None
        self.selected_settlement = None
        self.destination_settlement = None  # Track where merchant is heading
        self.game_tick = 0
        print("Game Initialization Complete.")

    def generate_settlements(self):
        print("Generating settlements...")
        settlements = []
        
        # Generate one main castle
        settlement_id = self.db.insert_settlement("King's Haven", self.width//2, self.height//2, "castle")
        self.db.populate_settlement_items(settlement_id)  # Add items to settlement
        settlements.append(Settlement(self.width//2, self.height//2, "King's Haven", "castle", id=settlement_id))
        print(f"Added Settlement: King's Haven with ID {settlement_id}")
        
        # Generate towns and villages
        names = ["Riverwood", "Oakvale", "Millbrook", "Ironforge", "Meadowbrook"]
        for i, name in enumerate(names):
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            settlement_type = "town" if i < 2 else "village"
            settlement_id = self.db.insert_settlement(name, x, y, settlement_type)
            self.db.populate_settlement_items(settlement_id)  # Add items to settlement
            settlements.append(Settlement(x, y, name, settlement_type, id=settlement_id))
            print(f"Added Settlement: {name} ({settlement_type}) with ID {settlement_id}")
        
        print(f"Total settlements generated: {len(settlements)}")
        return settlements

    def draw_world(self):
        # Draw terrain (simple for now)
        self.screen.fill((34, 139, 34))  # Green background for grass
        
        # Draw roads connecting settlements
        for i, settlement in enumerate(self.settlements):
            if i > 0:  # Connect to previous settlement
                pygame.draw.line(self.screen, (139, 119, 101), 
                               (settlement.x, settlement.y),
                               (self.settlements[i-1].x, self.settlements[i-1].y), 3)

        # Draw settlements
        for settlement in self.settlements:
            settlement.draw(self.screen)
        
        # Draw merchant
        self.merchant.draw(self.screen)

        # Draw cargo capacity
        font = pygame.font.Font(None, 36)
        cargo_text = font.render(f"Cargo: {self.merchant.current_load}/{self.merchant.cart_capacity}", 
                               True, (255, 255, 255))
        self.screen.blit(cargo_text, (10, 10))
        
        # Optionally: Draw a marker at merchant's target position
        if not self.merchant.arrived_at_settlement:
            if abs(self.merchant.x - self.merchant.target_x) > 5 or \
               abs(self.merchant.y - self.merchant.target_y) > 5:
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (int(self.merchant.target_x), int(self.merchant.target_y)), 5, 1)

        # Draw travel destination if exists
        if self.destination_settlement and self.state == GameState.WORLD_MAP:
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (int(self.destination_settlement.x), 
                              int(self.destination_settlement.y)), 
                             self.destination_settlement.size + 5, 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.TRADING:
                        self.state = GameState.WORLD_MAP
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.state == GameState.WORLD_MAP:
                        # Check for settlement clicks first
                        clicked_settlement = None
                        for settlement in self.settlements:
                            distance = math.sqrt((mouse_pos[0] - settlement.x)**2 + 
                                              (mouse_pos[1] - settlement.y)**2)
                            if distance < settlement.size + 20:
                                clicked_settlement = settlement
                                break
                        
                        if clicked_settlement:
                            # Set destination and log event
                            self.destination_settlement = clicked_settlement
                            self.merchant.target_x = clicked_settlement.x
                            self.merchant.target_y = clicked_settlement.y
                            self.merchant.arrived_at_settlement = False
                            print(f"Merchant destination set to Settlement ID {settlement.id}: {settlement.name}")
                        else:
                            # Clear destination if clicking empty space
                            self.destination_settlement = None
                            self.merchant.target_x = mouse_pos[0]
                            self.merchant.target_y = mouse_pos[1]
                            self.merchant.arrived_at_settlement = False
                    elif self.state == GameState.TRADING:
                        self.trading_ui.handle_click(pygame.mouse.get_pos(), self.current_settlement, self.merchant)
        return True

    def update(self):
        self.game_tick += 1
        
        if self.state == GameState.WORLD_MAP:
            # Update settlement prices periodically
            if self.game_tick % 100 == 0:  # Only update prices every 100 ticks
                for settlement in self.settlements:
                    settlement.update_prices(self.game_tick)
            
            if self.merchant.move():  # If merchant just arrived
                if self.destination_settlement:
                    distance = math.sqrt((self.merchant.x - self.destination_settlement.x)**2 + 
                                      (self.merchant.y - self.destination_settlement.y)**2)
                    if distance < self.destination_settlement.size + 5:
                        print("\n=== Entering Trading Mode ===")
                        print(f"Current Settlement: {self.destination_settlement.name}")
                        print(f"Settlement inventory items: {len(self.destination_settlement.get_inventory_items())}")
                        print(f"Merchant inventory items: {len(self.merchant.get_inventory_items())}")
                        self.state = GameState.TRADING
                        self.current_settlement = self.destination_settlement
                        self.trading_ui.current_category = None
                        self.destination_settlement = None

    def draw(self):
        if self.state == GameState.WORLD_MAP:
            self.draw_world()
        elif self.state == GameState.TRADING:
            # Draw semi-transparent background
            s = pygame.Surface((self.width, self.height))
            s.set_alpha(128)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0,0))
            
            # Draw trading UI
            self.trading_ui.draw(self.screen, self.current_settlement, self.merchant)

        pygame.display.flip()

    def run(self):
        print("Starting game loop...")
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        print("Game loop has ended.")

if __name__ == "__main__":
    game = Game()
    game.run()