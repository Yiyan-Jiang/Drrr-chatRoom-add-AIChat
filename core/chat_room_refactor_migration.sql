-- Chat room refactor migration notes.
-- Apply in phases for existing databases. Review owner backfill before production use.

USE chat_rooms;

-- Phase 1: add nullable/compatible columns.
ALTER TABLE chatRoom_user
  ADD COLUMN avatar_key VARCHAR(32) NULL;

ALTER TABLE chatRoom_room
  ADD COLUMN owner_id INT NULL;

ALTER TABLE chatRoom_message
  ADD COLUMN message_type VARCHAR(20) NULL,
  ADD COLUMN client_message_id VARCHAR(64) NULL;

-- Phase 2: backfill existing rows.
UPDATE chatRoom_user
SET avatar_key = 'kanra'
WHERE avatar_key IS NULL;

UPDATE chatRoom_message
SET message_type = 'user'
WHERE message_type IS NULL;

-- Owner backfill: choose the earliest message sender as room owner when possible.
UPDATE chatRoom_room r
JOIN (
  SELECT room_id, user_id
  FROM chatRoom_message m1
  WHERE m1.user_id IS NOT NULL
    AND m1.id = (
      SELECT MIN(m2.id)
      FROM chatRoom_message m2
      WHERE m2.room_id = m1.room_id
        AND m2.user_id IS NOT NULL
    )
) first_message ON first_message.room_id = r.id
SET r.owner_id = first_message.user_id
WHERE r.owner_id IS NULL;

-- Rooms without messages need manual owner assignment before Phase 3:
-- UPDATE chatRoom_room SET owner_id = <admin_user_id> WHERE owner_id IS NULL;

-- Phase 3: enforce constraints after verifying no nulls remain.
-- SELECT COUNT(*) FROM chatRoom_user WHERE avatar_key IS NULL;
-- SELECT COUNT(*) FROM chatRoom_room WHERE owner_id IS NULL;
-- SELECT COUNT(*) FROM chatRoom_message WHERE message_type IS NULL;

ALTER TABLE chatRoom_user
  MODIFY avatar_key VARCHAR(32) NOT NULL;

ALTER TABLE chatRoom_message
  MODIFY message_type VARCHAR(20) NOT NULL DEFAULT 'user';

-- Run this only after owner_id has no nulls.
-- ALTER TABLE chatRoom_room
--   MODIFY owner_id INT NOT NULL;

CREATE INDEX idx_chatRoom_user_avatar_key ON chatRoom_user (avatar_key);
CREATE INDEX idx_chatRoom_room_owner_id ON chatRoom_room (owner_id);
CREATE INDEX idx_chatRoom_message_room_created_id ON chatRoom_message (room_id, created_at, id);
CREATE UNIQUE INDEX uq_chatRoom_message_client_message_id ON chatRoom_message (client_message_id);

ALTER TABLE chatRoom_room
  ADD CONSTRAINT fk_chatRoom_room_owner
  FOREIGN KEY (owner_id) REFERENCES chatRoom_user(id)
  ON DELETE RESTRICT;
