import pygame
from game import Game
from database.db_handler import DatabaseHandler

def main():
    pygame.init()
    # Optionally, set up the display or other initial configurations here
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
