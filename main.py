import pygame
import logging
from game import Game
from database.db_handler import DatabaseHandler

def main():
    pygame.init()
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Change to logging.DEBUG for more detailed logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("game.log"),  # Logs will be saved to game.log
            logging.StreamHandler()  # Logs will also be printed to the console
        ]
    )
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
