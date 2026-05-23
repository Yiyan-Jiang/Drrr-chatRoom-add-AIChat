import { useCallback, useEffect, useMemo, useState } from 'react'
import toast from 'react-hot-toast'
import { roomApi } from '@/api/rooms'
import { handleApiError } from '@/utils/errorHandler'
import type { CreateRoomRequest, Room } from '@/types/chat'
import { sortRooms, type RoomSortKey } from '@/components/room/roomSort'
import { filterRoomsByName } from '@/components/room/roomSearch'

const DEFAULT_MAX_MEMBERS = 20
const ROOM_NAME_PATTERN = /^[\u4e00-\u9fa5A-Za-z0-9_]{1,8}$/

function parseTags(value: string) {
  return value
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

function parseOptionalNumber(value: string) {
  return value.trim() === '' ? null : Number(value)
}

export function useRooms() {
  const [rooms, setRooms] = useState<Room[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newRoomName, setNewRoomName] = useState('')
  const [description, setDescription] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [minAge, setMinAge] = useState('')
  const [maxAge, setMaxAge] = useState('')
  const [maxMembers, setMaxMembers] = useState(String(DEFAULT_MAX_MEMBERS))
  const [sortKey, setSortKey] = useState<RoomSortKey>('created_desc')
  const [searchInput, setSearchInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [totalOnlineMembers, setTotalOnlineMembers] = useState(0)

  const filteredRooms = useMemo(() => filterRoomsByName(rooms, searchQuery), [rooms, searchQuery])
  const visibleRooms = useMemo(() => sortRooms(filteredRooms, sortKey), [filteredRooms, sortKey])

  const submitSearch = useCallback(() => {
    setSearchQuery(searchInput)
  }, [searchInput])

  const fetchRooms = useCallback(async () => {
    try {
      setLoading(true)
      const [data, viewerCount] = await Promise.all([
        roomApi.list({ skip: 0, limit: 50 }),
        roomApi.getViewerCount(),
      ])
      setRooms(data)
      setTotalOnlineMembers(viewerCount.total)
    } catch (error: unknown) {
      handleApiError(error, '获取房间列表失败')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      fetchRooms()
    }, 0)
    return () => window.clearTimeout(timer)
  }, [fetchRooms])

  const resetForm = () => {
    setNewRoomName('')
    setDescription('')
    setTagInput('')
    setMinAge('')
    setMaxAge('')
    setMaxMembers(String(DEFAULT_MAX_MEMBERS))
  }

  const createRoom = async () => {
    const name = newRoomName.trim()
    if (!name) {
      toast.error('请输入房间名称')
      return
    }
    if (!ROOM_NAME_PATTERN.test(name)) {
      toast.error('房间名只能包含中文、英文、数字、下划线，长度 1 到 8 个字符')
      return
    }
    if (description.trim().length > 20) {
      toast.error('简介最多 20 个字符')
      return
    }

    const minAgeValue = parseOptionalNumber(minAge)
    const maxAgeValue = parseOptionalNumber(maxAge)
    const maxMembersValue = Number(maxMembers)

    if (
      (minAgeValue !== null && !Number.isFinite(minAgeValue)) ||
      (maxAgeValue !== null && !Number.isFinite(maxAgeValue)) ||
      !Number.isFinite(maxMembersValue)
    ) {
      toast.error('请输入有效的数字')
      return
    }

    if (minAgeValue !== null && maxAgeValue !== null && minAgeValue > maxAgeValue) {
      toast.error('最小年龄不能大于最大年龄')
      return
    }

    if (maxMembersValue < 1) {
      toast.error('最大人数至少为 1')
      return
    }

    const payload: CreateRoomRequest = {
      name,
      description: description.trim(),
      tags: parseTags(tagInput),
      min_age: minAgeValue,
      max_age: maxAgeValue,
      max_members: maxMembersValue,
    }

    setCreating(true)
    try {
      const newRoom = await roomApi.create(payload)
      toast.success(`房间 "${newRoom.name}" 创建成功`)
      resetForm()
      fetchRooms()
    } catch (error: unknown) {
      handleApiError(error, '创建房间失败')
    } finally {
      setCreating(false)
    }
  }

  return {
    rooms: visibleRooms,
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
  }
}
