import { useEffect, useRef, useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import api from "../lib/api"
import { fmtTime } from "../lib/fmt"

type MergeTicket = {
  ticket_id: string
  recorded_at: string
}

type DeployStatus = {
  environment?: string
  uptime: string
  uptime_seconds: number
  merge_tickets?: MergeTicket[]
}

const MERGE_TICKET_TOOLTIP_LIMIT = 20
const MERGE_TICKET_HOVER_DELAY_MS = 500

function mergeTicketDisplayLines(mergeTickets: MergeTicket[] | undefined): string[] {
  if (!mergeTickets?.length) return []
  return mergeTickets
    .slice(0, MERGE_TICKET_TOOLTIP_LIMIT)
    .map(({ ticket_id, recorded_at }) => `${ticket_id} ${fmtTime(recorded_at)}`)
}

export default function AdminDeployFooter() {
  const { loading: authLoading } = useAuth()
  const [status, setStatus] = useState<DeployStatus | null>(null)
  const [error, setError] = useState(false)
  const [tooltipVisible, setTooltipVisible] = useState(false)
  const hoverTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const envWrapRef = useRef<HTMLSpanElement>(null)

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

  useEffect(() => {
    return () => {
      if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current)
    }
  }, [])

  function handleEnvWrapMouseEnter() {
    if (!envInteractive) return
    if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current)
    hoverTimerRef.current = setTimeout(() => setTooltipVisible(true), MERGE_TICKET_HOVER_DELAY_MS)
  }

  function handleEnvWrapMouseLeave() {
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current)
      hoverTimerRef.current = null
    }
    setTooltipVisible(false)
  }

  if (authLoading || (!status && !error)) return null

  if (error) {
    return (
      <div className="nav-deploy-footer nav-deploy-footer-error" aria-label="Deploy status">
        Deploy status unavailable
      </div>
    )
  }

  const ticketLines = mergeTicketDisplayLines(status!.merge_tickets)
  const envInteractive = ticketLines.length > 0

  return (
    <div className="nav-deploy-footer" aria-label="Deploy status">
      {status!.environment != null && (
        <>
          <span
            className="nav-deploy-env-wrap"
            ref={envWrapRef}
            onMouseEnter={handleEnvWrapMouseEnter}
            onMouseLeave={handleEnvWrapMouseLeave}
          >
            <span
              className={
                envInteractive
                  ? "nav-deploy-env nav-deploy-env-interactive"
                  : "nav-deploy-env"
              }
            >
              {status!.environment}
            </span>
            {tooltipVisible && envInteractive && (
              <div
                className="nav-deploy-tickets-tooltip"
                role="tooltip"
                aria-label="Recent merge tickets"
              >
                {ticketLines.map(line => (
                  <div key={line} className="nav-deploy-tickets-tooltip-line">
                    {line}
                  </div>
                ))}
              </div>
            )}
          </span>
          <span className="nav-deploy-sep">·</span>
        </>
      )}
      <span className="nav-deploy-uptime">{status!.uptime}</span>
    </div>
  )
}
