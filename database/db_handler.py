import sqlite3
import os
import random  # Add this import at the top

class DatabaseHandler:
    def __init__(self, db_path="game_data.db"):
        print("Initializing DatabaseHandler...")
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        print("Connecting to database at:", self.db_path)
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
        print("Ensured 'items' table exists.")

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
        print("Ensured 'settlements' table exists.")

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
        print("Ensured 'settlement_items' table exists.")

        self.conn.commit()
        print("Database tables initialized.")

    def get_items(self):
        print("Fetching all items from the database...")
        cursor = self.conn.cursor()
        items = cursor.execute('SELECT * FROM items').fetchall()
        print(f"Retrieved {len(items)} items.")
        return items

    def get_item_by_id(self, item_id):
        print(f"Fetching item with ID: {item_id}")
        cursor = self.conn.cursor()
        item = cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        if item:
            print(f"Item found: {item['name']}")
        else:
            print("Item not found.")
        return item

    def get_settlement_items(self, settlement_id):
        print(f"Fetching items for settlement ID: {settlement_id}")
        cursor = self.conn.cursor()
        items = cursor.execute('''
            SELECT i.*, si.quantity FROM items i
            JOIN settlement_items si ON i.id = si.item_id
            WHERE si.settlement_id = ?
        ''', (settlement_id,)).fetchall()
        print(f"Retrieved {len(items)} items for settlement ID {settlement_id}.")
        return items

    def update_price_modifier(self, settlement_id, modifier):
        print(f"Updating price modifier for settlement ID {settlement_id} to {modifier}.")
        self.conn.execute('''
            UPDATE settlements 
            SET base_price_modifier = ?
            WHERE id = ?
        ''', (modifier, settlement_id))
        self.conn.commit()
        print("Price modifier updated.")

    def update_item_quantity(self, settlement_id, item_id, quantity):
        print(f"Updating quantity for item ID {item_id} in settlement ID {settlement_id} to {quantity}.")
        self.conn.execute('''
            UPDATE settlement_items
            SET quantity = ?
            WHERE settlement_id = ? AND item_id = ?
        ''', (quantity, settlement_id, item_id))
        self.conn.commit()
        print("Item quantity updated.")

    def insert_settlement(self, name, x, y, settlement_type):
        print(f"Inserting settlement: {name}, Type: {settlement_type}, Location: ({x}, {y})")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO settlements (name, x, y, settlement_type)
            VALUES (?, ?, ?, ?)
        ''', (name, x, y, settlement_type))
        self.conn.commit()
        settlement_id = cursor.lastrowid
        print(f"Settlement inserted with ID: {settlement_id}")
        return settlement_id  # Return the ID of the newly inserted settlement

    def insert_item(self, name, buy_price, sell_price, description, category):
        print(f"Inserting item: {name}, Category: {category}")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO items (name, buy_price, sell_price, description, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, buy_price, sell_price, description, category))
        self.conn.commit()
        item_id = cursor.lastrowid
        print(f"Item inserted with ID: {item_id}")
        return item_id  # Return the ID of the newly inserted item

    def insert_settlement_item(self, settlement_id, item_id, quantity):
        print(f"Inserting/Updating settlement_item: Settlement ID {settlement_id}, Item ID {item_id}, Quantity {quantity}")
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO settlement_items (settlement_id, item_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(settlement_id, item_id) DO UPDATE SET quantity = settlement_items.quantity + ?
        ''', (settlement_id, item_id, quantity, quantity))
        self.conn.commit()
        print("Settlement item inserted/updated.")

    def populate_settlement_items(self, settlement_id):
        print(f"Populating items for settlement ID {settlement_id}")
        cursor = self.conn.cursor()
        
        # Get all available items
        items = self.get_items()
        
        try:
            # For each item, insert a random quantity (5-20) into the settlement
            for item in items:
                quantity = random.randint(5, 20)
                cursor.execute('''
                    INSERT INTO settlement_items (settlement_id, item_id, quantity)
                    VALUES (?, ?, ?)
                ''', (settlement_id, item['id'], quantity))
                print(f"Added {quantity}x of item {item['name']} to settlement {settlement_id}")
            
            self.conn.commit()
            print(f"Successfully populated items for settlement {settlement_id}")
        except Exception as e:
            print(f"Error populating items for settlement {settlement_id}: {e}")
            self.conn.rollback()
