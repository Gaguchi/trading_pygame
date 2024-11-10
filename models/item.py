import logging
from dataclasses import dataclass
from database.db_handler import DatabaseHandler

@dataclass
class Item:
    id: int
    name: str
    buy_price: int
    sell_price: int
    description: str
    category: str
    quantity: int = 0  # Ensure quantity is included

    @staticmethod
    def load_all_items():
        logging.info("Loading all items...")
        db = DatabaseHandler()
        items_data = db.get_items()
        items = []
        for data in items_data:
            item = Item(
                id=data['id'],
                name=data['name'],
                buy_price=data['buy_price'],
                sell_price=data['sell_price'],
                description=data['description'],
                category=data['category'],
                quantity=0  # Set quantity to 0 as items table does not have 'quantity'
            )
            print(f"Loaded item: {item.name} (ID: {item.id}) x{item.quantity}")  # Retain quantities
            logging.debug(f"Loaded item: {item.name} (ID: {item.id}) x{item.quantity}")
        logging.info(f"Total items loaded: {len(items)}")
        return items

    @staticmethod
    def get_item_by_id(item_id):
        print(f"Retrieving item by ID: {item_id}")
        logging.info(f"Retrieving item by ID: {item_id}")
        db = DatabaseHandler()
        data = db.get_item_by_id(item_id)
        if data:
            item = Item(
                id=data['id'],
                name=data['name'],
                buy_price=data['buy_price'],
                sell_price=data['sell_price'],
                description=data['description'],
                category=data['category'],
                quantity=0  # Set quantity to 0 since get_item_by_id does not include 'quantity'
            )
            print(f"Item retrieved: {item.name} (ID: {item.id}) x{item.quantity}")  # Retain quantities
            logging.debug(f"Item retrieved: {item.name} (ID: {item.id}) x{item.quantity}")
            return item
        print("Item not found.")
        logging.warning("Item not found.")
        return None
