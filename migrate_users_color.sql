ALTER TABLE users ADD COLUMN color TEXT;
UPDATE users SET color = '#FF6B6B' WHERE username = 'erik';
UPDATE users SET color = '#4ECDC4' WHERE username = 'mark';