-- Clear existing settlements
DELETE FROM settlement_items;
DELETE FROM settlements;

-- Reset auto-increment
DELETE FROM sqlite_sequence WHERE name='settlements';

-- Insert settlements in hierarchical order
-- Central Castle
INSERT INTO settlements (name, x, y, settlement_type) VALUES 
('Imperial Citadel', 2000, 1500, 'castle');

-- Northern Kingdom
INSERT INTO settlements (name, x, y, settlement_type) VALUES 
('Northern Crown', 2000, 500, 'capital'),
('Frostbridge', 1600, 700, 'town'),
('Ironhold', 2400, 700, 'town'),
('Pine''s Rest', 1400, 600, 'village'),
('Coldwater', 2600, 600, 'village');

-- Eastern Empire
INSERT INTO settlements (name, x, y, settlement_type) VALUES 
('Eastern Haven', 3500, 1500, 'capital'),
('Silverport', 3200, 1200, 'town'),
('Eastwatch', 3200, 1800, 'town'),
('Fisher''s Cove', 3400, 1000, 'village'),
('Reed Haven', 3400, 2000, 'village');

-- Southern Kingdom
INSERT INTO settlements (name, x, y, settlement_type) VALUES 
('Southern Gate', 2000, 2500, 'capital'),
('Sunharbor', 1600, 2300, 'town'),
('Goldmeadow', 2400, 2300, 'town'),
('Sun''s Rest', 1400, 2400, 'village'),
('Wheat Creek', 2600, 2400, 'village');

-- Western Reich
INSERT INTO settlements (name, x, y, settlement_type) VALUES 
('Western Keep', 500, 1500, 'capital'),
('Westcliff', 800, 1200, 'town'),
('Stormgate', 800, 1800, 'town'),
('Stone Mill', 600, 1000, 'village'),
('Green Vale', 600, 2000, 'village');
