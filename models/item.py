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
    quantity: int = 0  # Add quantity for inventory management

    @staticmethod
    def load_all_items():
        db = DatabaseHandler()
        items_data = db.get_items()
        items = []
        for data in items_data:
            items.append(Item(
                id=data['id'],
                name=data['name'],
                buy_price=data['buy_price'],
                sell_price=data['sell_price'],
                description=data['description'],
                category=data['category']
            ))
        return items

    @staticmethod
    def get_item_by_id(item_id):
        db = DatabaseHandler()
        data = db.get_item_by_id(item_id)
        if data:
            return Item(
                id=data['id'],
                name=data['name'],
                buy_price=data['buy_price'],
                sell_price=data['sell_price'],
                description=data['description'],
                category=data['category']
            )
        return None
