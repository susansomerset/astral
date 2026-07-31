import { useMemo } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { fmtTime } from "../lib/fmt"

/** Renders a formatted timestamp in the selected candidate's timezone.
 *  Derives the timezone from CandidateContext at render time —
 *  no stale module-level reads, no effect timing issues. */
export default function Time({ value }: { value: string | null | undefined }) {
  const { candidates, selectedId } = useCandidate()
  const tz = useMemo(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    const profile = c?.candidate_data?.profile as Record<string, string> | undefined
    return profile?.timezone || "UTC"
  }, [candidates, selectedId])
  return <>{fmtTime(value, tz)}</>
}
