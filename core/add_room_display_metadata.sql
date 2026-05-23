USE chat_rooms;

ALTER TABLE chatRoom_room
  ADD COLUMN description TEXT NULL,
  ADD COLUMN tags JSON NULL,
  ADD COLUMN min_age INT NULL,
  ADD COLUMN max_age INT NULL,
  ADD COLUMN max_members INT NOT NULL DEFAULT 20;

UPDATE chatRoom_room
SET description = COALESCE(description, ''),
    tags = COALESCE(tags, JSON_ARRAY());
