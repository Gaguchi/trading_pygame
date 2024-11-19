import math
import random
from typing import Dict

class PricingHandler:
    # Price modifiers based on settlement type
    SETTLEMENT_TYPE_MODIFIERS = {
        "capital": 1.2,    # Capitals have higher prices
        "castle": 1.3,     # Castles have highest prices
        "town": 1.0,       # Towns have normal prices
        "village": 0.8     # Villages have lower prices
    }

    # Stock level thresholds
    STOCK_LEVELS = {
        "scarce": 5,       # 0-5 units
        "low": 10,         # 6-10 units
        "normal": 20,      # 11-20 units
        "abundant": 30     # 21+ units
    }

    # Stock level price modifiers
    STOCK_MODIFIERS = {
        "scarce": 1.5,     # Low stock = higher prices
        "low": 1.2,
        "normal": 1.0,
        "abundant": 0.8    # High stock = lower prices
    }

    @classmethod
    def calculate_price(cls, base_price: int, quantity: int, demand: float, 
                       settlement_type: str, is_buying: bool = True) -> int:
        """
        Calculate the final price for an item based on various factors.
        
        Args:
            base_price: The base price of the item
            quantity: Current stock level
            demand: Demand level (0.0 to 2.0, where 1.0 is normal)
            settlement_type: Type of settlement
            is_buying: True if buying from settlement, False if selling to settlement
        
        Returns:
            Final calculated price
        """
        # 1. Apply settlement type modifier
        settlement_modifier = cls.SETTLEMENT_TYPE_MODIFIERS.get(settlement_type, 1.0)
        price = base_price * settlement_modifier

        # 2. Apply stock level modifier
        stock_modifier = cls._get_stock_modifier(quantity)
        price *= stock_modifier

        # 3. Apply demand modifier
        demand_modifier = cls._calculate_demand_modifier(demand)
        price *= demand_modifier

        # 4. Apply buy/sell modifier (settlements buy for less than they sell)
        if not is_buying:
            price *= 0.7  # Settlements buy at 70% of calculated price

        # 5. Apply small random fluctuation (±5%)
        fluctuation = random.uniform(0.95, 1.05)
        price *= fluctuation

        # Ensure minimum price of 1
        return max(1, int(round(price)))

    @classmethod
    def _get_stock_modifier(cls, quantity: int) -> float:
        """Determine price modifier based on current stock level."""
        if quantity <= cls.STOCK_LEVELS["scarce"]:
            return cls.STOCK_MODIFIERS["scarce"]
        elif quantity <= cls.STOCK_LEVELS["low"]:
            return cls.STOCK_MODIFIERS["low"]
        elif quantity <= cls.STOCK_LEVELS["normal"]:
            return cls.STOCK_MODIFIERS["normal"]
        else:
            return cls.STOCK_MODIFIERS["abundant"]

    @classmethod
    def _calculate_demand_modifier(cls, demand: float) -> float:
        """Calculate price modifier based on demand level."""
        # Demand of 1.0 is normal, below 1.0 reduces price, above 1.0 increases price
        return math.pow(demand, 1.5)  # Using power of 1.5 for more pronounced effect

    @classmethod
    def update_settlement_prices(cls, settlement) -> None:
        """
        Update all item prices in a settlement based on current conditions.
        """
        print(f"Updating prices for settlement: {settlement.name}")
        
        # Calculate base demand for the settlement type
        base_demand = {
            "capital": 1.2,
            "castle": 1.3,
            "town": 1.0,
            "village": 0.8
        }.get(settlement.settlement_type, 1.0)

        # Update prices for each item in settlement's inventory
        for item_id, item in settlement.inventory.items():
            # Calculate unique demand for this item (base demand + random variation)
            item_demand = base_demand * random.uniform(0.8, 1.2)
            
            # Update buy price (when player buys from settlement)
            item.buy_price = cls.calculate_price(
                base_price=item.buy_price,
                quantity=item.quantity,
                demand=item_demand,
                settlement_type=settlement.settlement_type,
                is_buying=True
            )

            # Update sell price (when player sells to settlement)
            item.sell_price = cls.calculate_price(
                base_price=item.buy_price,  # Use buy_price as base for sell_price
                quantity=item.quantity,
                demand=item_demand,
                settlement_type=settlement.settlement_type,
                is_buying=False
            )

    @classmethod
    def get_price_factors(cls, item, settlement) -> Dict[str, float]:
        """
        Get detailed breakdown of price factors for an item in a settlement.
        Useful for debugging and UI tooltips.
        """
        base_demand = {
            "capital": 1.2,
            "castle": 1.3,
            "town": 1.0,
            "village": 0.8
        }.get(settlement.settlement_type, 1.0)

        return {
            "base_price": item.buy_price,
            "settlement_modifier": cls.SETTLEMENT_TYPE_MODIFIERS.get(settlement.settlement_type, 1.0),
            "stock_modifier": cls._get_stock_modifier(item.quantity),
            "demand_modifier": cls._calculate_demand_modifier(base_demand),
            "quantity": item.quantity,
            "demand_level": base_demand
        }
