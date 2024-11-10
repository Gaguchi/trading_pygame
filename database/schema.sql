
-- Table for items
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    buy_price INTEGER NOT NULL,
    sell_price INTEGER NOT NULL,
    description TEXT,
    category TEXT
);

-- Table for settlements
CREATE TABLE IF NOT EXISTS settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    settlement_type TEXT NOT NULL,
    base_price_modifier REAL DEFAULT 1.0
);

-- Table for settlement inventory
CREATE TABLE IF NOT EXISTS settlement_items (
    settlement_id INTEGER,
    item_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY(settlement_id) REFERENCES settlements(id),
    FOREIGN KEY(item_id) REFERENCES items(id),
    PRIMARY KEY (settlement_id, item_id)
);

-- You can add initial data with INSERT statements if needed
