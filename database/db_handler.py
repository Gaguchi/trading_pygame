import sqlite3
import os

class DatabaseHandler:
    def __init__(self, db_path="game_data.db"):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()
        # Create items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                buy_price INTEGER NOT NULL,
                sell_price INTEGER NOT NULL,
                description TEXT,
                category TEXT
            )
        ''')
        # Create settlements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settlements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                settlement_type TEXT NOT NULL,
                base_price_modifier REAL DEFAULT 1.0
            )
        ''')
        # Create settlement_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settlement_items (
                settlement_id INTEGER,
                item_id INTEGER,
                quantity INTEGER NOT NULL,
                FOREIGN KEY(settlement_id) REFERENCES settlements(id),
                FOREIGN KEY(item_id) REFERENCES items(id),
                PRIMARY KEY (settlement_id, item_id)
            )
        ''')
        self.conn.commit()

    def get_items(self):
        cursor = self.conn.cursor()
        return cursor.execute('SELECT * FROM items').fetchall()

    def get_item_by_id(self, item_id):
        cursor = self.conn.cursor()
        return cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()

    def get_settlement_items(self, settlement_id):
        cursor = self.conn.cursor()
        return cursor.execute('''
            SELECT i.*, si.quantity FROM items i
            JOIN settlement_items si ON i.id = si.item_id
            WHERE si.settlement_id = ?
        ''', (settlement_id,)).fetchall()

    def update_price_modifier(self, settlement_id, modifier):
        self.conn.execute('''
            UPDATE settlements 
            SET base_price_modifier = ?
            WHERE id = ?
        ''', (modifier, settlement_id))
        self.conn.commit()

    def update_item_quantity(self, settlement_id, item_id, quantity):
        self.conn.execute('''
            UPDATE settlement_items
            SET quantity = ?
            WHERE settlement_id = ? AND item_id = ?
        ''', (quantity, settlement_id, item_id))
        self.conn.commit()

    def insert_settlement(self, name, x, y, settlement_type):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO settlements (name, x, y, settlement_type)
            VALUES (?, ?, ?, ?)
        ''', (name, x, y, settlement_type))
        self.conn.commit()
        return cursor.lastrowid  # Return the ID of the newly inserted settlement
