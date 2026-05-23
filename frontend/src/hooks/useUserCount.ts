import { useCallback, useEffect, useRef, useState } from "react";
import type { Usercnt } from '../types/chat' 
import { usersApi } from "../api/users";

export function useUserCount() {
  const [ data, setData ] = useState<Usercnt | null>(null)
  const [ loading, serLoading ] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cancelledRef = useRef(false)

  const fetchUserCount = useCallback(async ():Promise<void>=> {
    setError(null)

    try {
      const res:Usercnt = await usersApi.getUserCnt()
      if (!cancelledRef.current) {
        setData(res)
      } 
    }catch(err) {
      console.error(err);
      if(!cancelledRef.current){
        setError('获取失败')
      }
    }finally{
      if(!cancelledRef.current){
        serLoading(false)
      }
    }
  },[])

  useEffect(()=>{
    cancelledRef.current = false
    const timer = window.setTimeout(() => {
      fetchUserCount()
    }, 0)

    return () => {
      window.clearTimeout(timer)
      cancelledRef.current = true
    }
  },[fetchUserCount])

  return {
    data,
    loading,
    error,
    refetch: fetchUserCount
  }

}
