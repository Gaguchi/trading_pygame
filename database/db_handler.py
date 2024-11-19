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

        # Execute schema.sql to create tables
        try:
            with open('database/schema.sql', 'r') as schema_file:
                schema_script = schema_file.read()
                cursor.executescript(schema_script)
                self.conn.commit()
                print("Database schema initialized successfully")
        except Exception as e:
            print(f"Error initializing database schema: {e}")
            self.conn.rollback()

        # Check if settlements need to be initialized
        cursor.execute('SELECT COUNT(*) FROM settlements')
        if cursor.fetchone()[0] == 0:
            print("Initializing settlements from SQL file...")
            try:
                with open('database/init_settlements.sql', 'r') as sql_file:
                    sql_script = sql_file.read()
                    cursor.executescript(sql_script)
                    self.conn.commit()
                    print("Settlements initialized successfully")
            except Exception as e:
                print(f"Error initializing settlements: {e}")
                self.conn.rollback()

        # Check if items need to be initialized
        cursor.execute('SELECT COUNT(*) FROM items')
        if cursor.fetchone()[0] == 0:
            print("Initializing items from SQL file...")
            try:
                with open('database/init_items.sql', 'r') as sql_file:
                    sql_script = sql_file.read()
                    cursor.executescript(sql_script)
                    self.conn.commit()
                    print("Items initialized successfully")
            except Exception as e:
                print(f"Error initializing items: {e}")
                self.conn.rollback()

        # Populate settlement items
        cursor.execute('SELECT COUNT(*) FROM settlement_items')
        if cursor.fetchone()[0] == 0:
            print("Populating settlement items...")
            try:
                settlements = self.load_settlements()
                for settlement in settlements:
                    self.populate_settlement_items(settlement['id'])
                print("Settlement items populated successfully")
            except Exception as e:
                print(f"Error populating settlement items: {e}")
                self.conn.rollback()

        print("Database initialization complete")

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

    def get_settlement_id_by_name(self, name):
        """Get settlement ID by name, returns None if not found."""
        try:
            self.cursor.execute("SELECT id FROM settlements WHERE name = ?", (name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def load_settlements(self):
        """Load all settlements from database."""
        print("Loading settlements from database...")
        cursor = self.conn.cursor()
        
        # Get settlement counts by type
        cursor.execute('''
            SELECT settlement_type, COUNT(*) 
            FROM settlements 
            GROUP BY settlement_type
        ''')
        counts = cursor.fetchall()
        for type_count in counts:
            print(f"Found {type_count[1]} {type_count[0]}(s)")

        # Get all settlements
        cursor.execute('SELECT * FROM settlements ORDER BY settlement_type, name')
        settlements = cursor.fetchall()
        print(f"Loaded {len(settlements)} total settlements")
        return settlements
