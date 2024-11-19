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
    DEBUG_MENU = "debug_menu"  # Add new state

class Game:
    def __init__(self):
        print("Starting Game Initialization...")
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Medieval Merchant")
        self.clock = pygame.time.Clock()
        self.state = GameState.WORLD_MAP
        self.debug_font = pygame.font.Font(None, 20)
        self.debug_menu_visible = False  # Toggle for debug menu
        print(f"Game state set to {self.state}.")
        
        # Initialize database and world size first
        self.db = DatabaseHandler()
        self.world_width = 4000
        self.world_height = 3000
        
        # Load settlements before creating merchant
        self.settlements = self.generate_settlements()
        
        # Find Western Capital for starting position
        capitals = [s for s in self.settlements if s.settlement_type == "capital"]
        if capitals:
            western_capital = min(capitals, key=lambda s: s.x)
            # Place merchant slightly to the left of western capital
            start_x = western_capital.x - 100
            start_y = western_capital.y
        else:
            print("Warning: No capital settlements found. Using default starting position.")
            start_x = self.world_width // 2
            start_y = self.world_height // 2
        
        # Initialize merchant at starting position
        self.merchant = Merchant(start_x, start_y)
        
        # Initialize other game components
        self.trading_ui = TradingUI(self.width, self.height)
        self.current_settlement = None
        self.selected_settlement = None
        self.destination_settlement = None
        self.game_tick = 0
        
        # Initialize camera position centered on merchant
        self.camera_x = self.width//2 - start_x
        self.camera_y = self.height//2 - start_y
        
        print("Game Initialization Complete.")

    def generate_settlements(self):
        print("Loading settlements from database...")
        settlements = []
        
        # Load settlement data from database
        db_settlements = self.db.load_settlements()
        
        # Create Settlement objects from database data
        for settlement_data in db_settlements:
            settlement = Settlement(
                x=settlement_data['x'],
                y=settlement_data['y'],
                name=settlement_data['name'],
                settlement_type=settlement_data['settlement_type'],
                id=settlement_data['id']
            )
            # Populate items if needed
            if not self.db.get_settlement_items(settlement.id):
                self.db.populate_settlement_items(settlement.id)
            settlements.append(settlement)
            print(f"Loaded Settlement: {settlement.name} ({settlement.settlement_type}) with ID {settlement.id}")
        
        print(f"Total settlements loaded: {len(settlements)}")
        return settlements

    def update_camera(self):
        # Camera follows merchant with smooth movement
        target_x = self.width//2 - self.merchant.x
        target_y = self.height//2 - self.merchant.y
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        return (int(x + self.camera_x), int(y + self.camera_y))

    def screen_to_world(self, x, y):
        """Convert screen coordinates to world coordinates"""
        return (int(x - self.camera_x), int(y - self.camera_y))

    def draw_world(self):
        # Draw terrain (simple for now)
        self.screen.fill((34, 139, 34))  # Green background for grass
        
        # Draw grid for reference (optional)
        grid_size = 100
        for x in range(0, self.world_width, grid_size):
            screen_x = x + self.camera_x
            if 0 <= screen_x <= self.width:
                pygame.draw.line(self.screen, (0, 100, 0), 
                               (screen_x, 0), 
                               (screen_x, self.height))
        for y in range(0, self.world_height, grid_size):
            screen_y = y + self.camera_y
            if 0 <= screen_y <= self.height:
                pygame.draw.line(self.screen, (0, 100, 0), 
                               (0, screen_y), 
                               (self.width, screen_y))

        # Categorize settlements
        castle = None
        capitals = []
        towns = []
        villages = []
        
        for settlement in self.settlements:
            if settlement.settlement_type == "castle":
                castle = settlement
            elif settlement.settlement_type == "capital":
                capitals.append(settlement)
            elif settlement.settlement_type == "town":
                towns.append(settlement)
            elif settlement.settlement_type == "village":
                villages.append(settlement)

        # Draw paths in hierarchical order
        # 1. Major roads between capitals (thick brown roads)
        for i in range(len(capitals)):
            for j in range(i + 1, len(capitals)):
                start = self.world_to_screen(capitals[i].x, capitals[i].y)
                end = self.world_to_screen(capitals[j].x, capitals[j].y)
                # Draw thick brown road with black border
                pygame.draw.line(self.screen, (101, 67, 33), start, end, 8)  # Main road
                pygame.draw.line(self.screen, (139, 69, 19), start, end, 6)  # Road center

        # 2. Regional roads from capitals to their towns (medium roads)
        for capital in capitals:
            cap_pos = self.world_to_screen(capital.x, capital.y)
            # Find towns that belong to this capital's territory
            for town in towns:
                # Calculate if town belongs to this capital's territory
                dist_to_capital = math.sqrt((town.x - capital.x)**2 + (town.y - capital.y)**2)
                closest_capital = min(capitals, key=lambda c: 
                    math.sqrt((town.x - c.x)**2 + (town.y - c.y)**2))
                
                # Only connect if this is the closest capital
                if closest_capital == capital and dist_to_capital < 1000:
                    town_pos = self.world_to_screen(town.x, town.y)
                    pygame.draw.line(self.screen, (139, 119, 101), cap_pos, town_pos, 4)

        # 3. Local roads from towns to nearby villages (thin roads)
        for town in towns:
            town_pos = self.world_to_screen(town.x, town.y)
            # Find closest villages
            nearby_villages = []
            for village in villages:
                dist = math.sqrt((town.x - village.x)**2 + (town.y - village.y)**2)
                if dist < 500:  # Only connect to very close villages
                    village_pos = self.world_to_screen(village.x, village.y)
                    nearby_villages.append((dist, village_pos, village))
            
            # Connect only to the closest villages (max 2 per town)
            nearby_villages.sort(key=lambda x: x[0])
            for _, village_pos, _ in nearby_villages[:2]:
                pygame.draw.line(self.screen, (160, 140, 120), town_pos, village_pos, 2)

        # Draw all settlements with screen coordinate conversion
        for settlement in self.settlements:
            screen_pos = self.world_to_screen(settlement.x, settlement.y)
            # Only draw if on screen
            if (-settlement.size <= screen_pos[0] <= self.width + settlement.size and
                -settlement.size <= screen_pos[1] <= self.height + settlement.size):
                pygame.draw.circle(self.screen, settlement.color, screen_pos, settlement.size)
                # Draw settlement name
                font = pygame.font.Font(None, 24)
                text = font.render(settlement.name, True, (255, 255, 255))
                self.screen.blit(text, (screen_pos[0] - text.get_width()//2, 
                                      screen_pos[1] + settlement.size + 5))

        # Draw merchant with screen coordinate conversion
        merchant_pos = self.world_to_screen(self.merchant.x, self.merchant.y)
        self.merchant.draw(self.screen, merchant_pos)

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

    def draw_debug_menu(self):
        # Draw semi-transparent background
        s = pygame.Surface((300, self.height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        # Draw settlement list
        y = 10
        header = self.debug_font.render("DEBUG MENU (Press F3 to toggle)", True, (255, 255, 0))
        self.screen.blit(header, (10, y))
        y += 30
        
        # Group settlements by type
        settlement_types = ["castle", "capital", "town", "village"]
        for stype in settlement_types:
            # Draw type header
            type_text = self.debug_font.render(f"--- {stype.upper()} ---", True, (0, 255, 0))
            self.screen.blit(type_text, (10, y))
            y += 20
            
            # List settlements of this type
            for settlement in [s for s in self.settlements if s.settlement_type == stype]:
                text = self.debug_font.render(
                    f"{settlement.name} ({settlement.x}, {settlement.y})", 
                    True, 
                    (255, 255, 255)
                )
                rect = text.get_rect(x=10, y=y)
                
                # Highlight if mouse is over
                mouse_pos = pygame.mouse.get_pos()
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(self.screen, (50, 50, 50), rect)
                
                self.screen.blit(text, rect)
                y += 20
            
            y += 10  # Space between categories

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.TRADING:
                        self.state = GameState.WORLD_MAP
                elif event.key == pygame.K_F3:  # Toggle debug menu
                    self.debug_menu_visible = not self.debug_menu_visible
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.debug_menu_visible:
                        # Check if click is in debug menu
                        if pygame.mouse.get_pos()[0] < 300:
                            # Find clicked settlement
                            y = 60  # Start after header
                            for stype in ["castle", "capital", "town", "village"]:
                                y += 20  # Type header
                                for settlement in [s for s in self.settlements if s.settlement_type == stype]:
                                    rect = pygame.Rect(10, y, 290, 20)
                                    if rect.collidepoint(pygame.mouse.get_pos()):
                                        # Teleport merchant to settlement
                                        self.merchant.x = settlement.x
                                        self.merchant.y = settlement.y
                                        print(f"DEBUG: Teleported to {settlement.name}")
                                        return True
                                    y += 20
                                y += 10  # Space between categories
                            return True
                    
                    # Convert screen coordinates to world coordinates for click handling
                    screen_pos = pygame.mouse.get_pos()
                    world_pos = self.screen_to_world(*screen_pos)
                    if self.state == GameState.WORLD_MAP:
                        # Check for settlement clicks first
                        clicked_settlement = None
                        for settlement in self.settlements:
                            distance = math.sqrt((world_pos[0] - settlement.x)**2 + 
                                              (world_pos[1] - settlement.y)**2)
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
                            self.merchant.target_x = world_pos[0]
                            self.merchant.target_y = world_pos[1]
                            self.merchant.arrived_at_settlement = False
                    elif self.state == GameState.TRADING:
                        self.trading_ui.handle_click(pygame.mouse.get_pos(), self.current_settlement, self.merchant)
        return True

    def update(self):
        self.game_tick += 1
        self.update_camera()  # Update camera position
        
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
            if self.debug_menu_visible:
                self.draw_debug_menu()
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