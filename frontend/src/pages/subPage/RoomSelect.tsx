import RoomList from '@/components/room/RoomList';
import RoomCreatePanel from '@/components/room/RoomCreatePanel';
import { useRooms } from '@/hooks/useRooms';

export default function RoomSelect() {
  const {
    rooms,
    loading,
    creating,
    sortKey,
    searchInput,
    totalOnlineMembers,
    newRoomName,
    description,
    tagInput,
    minAge,
    maxAge,
    maxMembers,
    setNewRoomName,
    setDescription,
    setTagInput,
    setMinAge,
    setMaxAge,
    setMaxMembers,
    setSortKey,
    setSearchInput,
    submitSearch,
    fetchRooms,
    createRoom,
  } = useRooms();

  return (
    <div className="relative flex h-full min-h-0 flex-col overflow-hidden p-0">
      <div className="min-h-0 flex-1 overflow-auto bg-[#090909] p-6">
        <RoomList
          rooms={rooms}
          loading={loading}
          sortKey={sortKey}
          searchInput={searchInput}
          totalOnlineMembers={totalOnlineMembers}
          onSortChange={setSortKey}
          onSearchInputChange={setSearchInput}
          onSearchSubmit={submitSearch}
          onRefresh={fetchRooms}
        />
      </div>
      <RoomCreatePanel
        creating={creating}
        newRoomName={newRoomName}
        description={description}
        tagInput={tagInput}
        minAge={minAge}
        maxAge={maxAge}
        maxMembers={maxMembers}
        onNewRoomNameChange={setNewRoomName}
        onDescriptionChange={setDescription}
        onTagInputChange={setTagInput}
        onMinAgeChange={setMinAge}
        onMaxAgeChange={setMaxAge}
        onMaxMembersChange={setMaxMembers}
        onCreateRoom={createRoom}
      />
    </div>
  );
}
