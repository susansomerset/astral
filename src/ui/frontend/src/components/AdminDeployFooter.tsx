import { useEffect, useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import api from "../lib/api"

type DeployStatus = {
  environment?: string
  uptime: string
  uptime_seconds: number
}

export default function AdminDeployFooter() {
  const { loading: authLoading } = useAuth()
  const [status, setStatus] = useState<DeployStatus | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    if (authLoading) return
    const fetchStatus = () =>
      api("/api/deploy_status")
        .then(r => {
          if (!r.ok) throw new Error(`${r.status}`)
          return r.json()
        })
        .then(data => {
          setStatus(data)
          setError(false)
        })
        .catch(() => setError(true))
    fetchStatus()
    const interval = setInterval(fetchStatus, 30_000)
    return () => clearInterval(interval)
  }, [authLoading])

  if (authLoading || (!status && !error)) return null

  if (error) {
    return (
      <div className="nav-deploy-footer nav-deploy-footer-error" aria-label="Deploy status">
        Deploy status unavailable
      </div>
    )
  }

  return (
    <div className="nav-deploy-footer" aria-label="Deploy status">
      {status!.environment != null && (
        <>
          <span className="nav-deploy-env">{status!.environment}</span>
          <span className="nav-deploy-sep">·</span>
        </>
      )}
      <span className="nav-deploy-uptime">{status!.uptime}</span>
    </div>
  )
}
