CREATE DATABASE IF NOT EXISTS chat_rooms 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;


USE chat_rooms;


CREATE USER IF NOT EXISTS 'chat_user'@'localhost' IDENTIFIED BY 'change-me-in-env';
GRANT ALL PRIVILEGES ON chat_rooms.* TO 'chat_user'@'localhost';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS chatRoom_user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) UNIQUE,
  password VARCHAR(128),
  avatar_key VARCHAR(32) NOT NULL DEFAULT 'kanra',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chatRoom_user_avatar_key (avatar_key)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chatRoom_room (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(8) UNIQUE,
  description TEXT NULL,
  notice TEXT NULL,
  rules TEXT NULL,
  tags JSON NULL,
  min_age INT NULL,
  max_age INT NULL,
  max_members INT NOT NULL DEFAULT 20,
  peak_online_members INT NOT NULL DEFAULT 1,
  owner_id INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chatRoom_room_owner_id (owner_id),
  CONSTRAINT fk_chatRoom_room_owner
    FOREIGN KEY (owner_id) REFERENCES chatRoom_user(id)
    ON DELETE RESTRICT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chatRoom_message (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  content TEXT,
  room_id INT NOT NULL,
  message_type VARCHAR(20) NOT NULL DEFAULT 'user',
  client_message_id VARCHAR(64) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chatRoom_message_room_created_id (room_id, created_at, id),
  UNIQUE INDEX uq_chatRoom_message_client_message_id (client_message_id),
  CONSTRAINT fk_chatRoom_message_user
    FOREIGN KEY (user_id) REFERENCES chatRoom_user(id)
    ON DELETE SET NULL,
  CONSTRAINT fk_chatRoom_message_room
    FOREIGN KEY (room_id) REFERENCES chatRoom_room(id)
    ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SHOW DATABASES;
