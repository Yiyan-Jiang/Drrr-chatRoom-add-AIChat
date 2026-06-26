import { useEffect, useState } from 'react'
import { Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { gateApi } from '@/api/gate'

export default function GateGuard() {
  const navigate = useNavigate()
  const location = useLocation()
  const [gateChecked, setGateChecked] = useState(false)
  const [gateAllowed, setGateAllowed] = useState(false)

  useEffect(() => {
    let cancelled = false

    const checkGate = async () => {
      try {
        await gateApi.check()
        if (!cancelled) {
          setGateAllowed(true)
          setGateChecked(true)
        }
      } catch {
        if (!cancelled) {
          setGateAllowed(false)
          setGateChecked(true)
          navigate('/gate', { replace: true, state: { from: location.pathname } })
        }
      }
    }

    checkGate()

    return () => {
      cancelled = true
    }
  }, [location.pathname, navigate])

  if (!gateChecked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!gateAllowed) {
    return <Navigate to="/gate" replace />
  }

  return <Outlet />
}
