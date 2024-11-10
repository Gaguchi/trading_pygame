from database.db_handler import DatabaseHandler

def populate_items(db):
    print("Populating 'items' table with sample data...")
    sample_items = [
        {
            'name': 'Iron Ore',
            'buy_price': 10,
            'sell_price': 8,
            'description': 'A valuable mineral used for making weapons and tools.',
            'category': 'Mineral'
        },
        {
            'name': 'Wheat',
            'buy_price': 5,
            'sell_price': 3,
            'description': 'Basic food staple used for making bread.',
            'category': 'Food'
        },
        {
            'name': 'Leather',
            'buy_price': 15,
            'sell_price': 12,
            'description': 'Used for crafting armor and bags.',
            'category': 'Crafting Material'
        },
        {
            'name': 'Herbs',
            'buy_price': 20,
            'sell_price': 18,
            'description': 'Medicinal plants used for healing potions.',
            'category': 'Medicinal'
        },
        {
            'name': 'Copper Wire',
            'buy_price': 25,
            'sell_price': 20,
            'description': 'Used in crafting basic electronics.',
            'category': 'Crafting Material'
        }
    ]

    for item in sample_items:
        db.insert_item(
            name=item['name'],
            buy_price=item['buy_price'],
            sell_price=item['sell_price'],
            description=item['description'],
            category=item['category']
        )
    print("Sample items population complete.\n")

def populate_settlement_items(db, settlement_id, item_quantities):
    print(f"Populating 'settlement_items' for Settlement ID {settlement_id}...")
    for item_id, quantity in item_quantities.items():
        db.insert_settlement_item(settlement_id, item_id, quantity)
    print(f"Settlement ID {settlement_id} inventory populated.\n")

def main():
    db = DatabaseHandler()

    # Check if 'items' table is empty
    items = db.get_items()
    if len(items) == 0:
        populate_items(db)
    else:
        print("'items' table already populated.\n")

    # Assume Settlements have been inserted. Fetch their IDs.
    print("Fetching all settlements to assign items...")
    cursor = db.conn.cursor()
    settlements = cursor.execute('SELECT id, name FROM settlements').fetchall()
    for settlement in settlements:
        settlement_id = settlement['id']
        settlement_name = settlement['name']
        print(f"Assigning items to Settlement ID {settlement_id}: {settlement_name}")

        # Example item assignments (can be customized per settlement)
        if settlement_name == "King's Haven":
            item_quantities = {
                1: 100,  # Iron Ore
                2: 200,  # Wheat
                3: 150,  # Leather
                4: 80,   # Herbs
                5: 60    # Copper Wire
            }
        elif settlement_name == "Riverwood":
            item_quantities = {
                2: 150,  # Wheat
                3: 100,  # Leather
                4: 50    # Herbs
            }
        elif settlement_name == "Oakvale":
            item_quantities = {
                1: 80,   # Iron Ore
                3: 120,  # Leather
                5: 40    # Copper Wire
            }
        elif settlement_name == "Millbrook":
            item_quantities = {
                2: 180,  # Wheat
                4: 70    # Herbs
            }
        elif settlement_name == "Ironforge":
            item_quantities = {
                1: 200,  # Iron Ore
                5: 100   # Copper Wire
            }
        elif settlement_name == "Meadowbrook":
            item_quantities = {
                2: 130,  # Wheat
                3: 90,   # Leather
                4: 60    # Herbs
            }
        else:
            item_quantities = {}

        populate_settlement_items(db, settlement_id, item_quantities)

if __name__ == "__main__":
    main()
