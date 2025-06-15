-- Create a table
CREATE TABLE IF NOT EXISTS city (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Insert predefined data
INSERT INTO city (name) VALUES
('Chimbote'),
('Lima');