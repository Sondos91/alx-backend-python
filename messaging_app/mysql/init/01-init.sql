-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS messaging_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the messaging user
GRANT ALL PRIVILEGES ON messaging_db.* TO 'messaging_user'@'%';
FLUSH PRIVILEGES;
